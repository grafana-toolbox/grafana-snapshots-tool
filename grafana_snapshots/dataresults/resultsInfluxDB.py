#!/usr/bin/python3
# -*- coding: utf-8 -*-
#***********************************************************************************************
from .resultsBase import resultsBase
from typing import Union

import re

#***********************************************************************************************
class resultsInfluxDB(resultsBase):
    """
    response contains an array of results:
    e.g.: InfluxDB
    "response": [
        {
            "statement_id": 0,
            "series": [
                { serie },
            ]
        }
    ]

    serie: {
        "name": "<serie_name>",
        "tags": {
            "tag_name": "tag_value"
        },
        "columns": [
            "time",
            "<others columns names>",
        ],
        "values":[
            [ timestamp_1, value_1],
            [ timestamp_2, value_2],
            [ ..., ...]
        ]
    }

    """
    #* to catch tag in alias [[ tag_<tagname> ]] 
    tagfinder = re.compile(r'(\[\[\s*tag_([a-zA-Z0-9_]+)\s*]])')
    var_tagfinder = re.compile(r'(\${?\s*tag_(\$?[a-zA-Z0-9_]+)\s*}?)')

    #***********************************************
    def __init__( *args, **kwargs ):
        self = args[0]

        super(resultsInfluxDB, self).__init__(**kwargs)

        self.results = kwargs.get('results', None)
        if "results" in self.results and self.results["results"]:
            for res in self.results["results"]:
                if "error" in res:
                    raise ValueError("infuxDB query error: '{0}'!".format(res["error"]))

    #***********************************************
    def get_snapshotData(self, targets: Union[list, dict])-> list:
        snapshotData = list()
        snapshotDataObj = {}
        (ts_part, value_part, ref_id) = ( None, None, None)

        if not self.results or not 'results' in self.results \
            or not isinstance(self.results['results'], list) \
            or len(self.results['results']) <= 0:
            return snapshotData

        if targets is None:
            targets = []
        if isinstance(targets, dict):
            targets = [ targets ]

        # it seems that v1 Influxdb data ha always the same format:
        # format time_series, table, logs provide the same results.

        # required format is time_series:
        if self.format == 'time_series':

            # loop on each timeseries received from the response
            for idx, statement in enumerate(self.results['results']):

                #* something wrong occurs with query !
                if 'error' in statement:
                    return snapshotData

                if len(targets)> idx:
                    target = targets[idx]
                else:
                    target = {}

                for serie in statement['series']:
                    snapshotDataObj = {}
                    name = None

                    #*** split list of [ (ts,val),...] from values into 2 lists of (ts, tsx,...) (val, valx,...)
                    ts=list()
                    values=list()

                    for value_pair in serie['values']:
                        if self.debug:
                            print('ts={0} - val={1}'.format(value_pair[0], value_pair[1]))
                        ts.append(int(value_pair[0]))
                        value = value_pair[1]
                        if value is None or value == 'NaN':
                            value = None
                        else:
                            value = float( value )
                        values.append(value)

                    (ts_part, value_part) = self.panel.get_FieldsConfig(serie['values'], values=values)
                    #** build timestamp list
                    ts_part.update( {
                        'name': 'Time',
                        'type': 'time',
                        'values': ts
                    } )

                    #** build value part...
                    value_part.update( {
                        'name': 'Value',
                        'type': 'number',
                        'values': values
                    } )
                    if 'alias' in target:
                        name = target['alias']
                        # add vars:
                        # 'm' with value "metric name"
                        # 'col' with value "column name"
                        self.symbols_vars.update( {
                            'm': serie['name'],
                            'col': serie['columns'][1],
                        } )

                    labels = None
                    if 'tags' in serie:
                        value_part.update({
                            'labels': serie['tags'],
                        })
                        labels = serie['tags']

                    if name is None:
                        if labels is not None:
                            name = list(labels.values())[0]
                        else:
                            ####
                            # WARNING: take the name of the last serie : why but why not ?
                            ####
                            name = '{0}.{1}'.format(serie['name'], serie['columns'][1])

                    #* name could contain vars to instanciate $m $col $var
                    name = self.buildDisplayName( name, labels )
                    value_part['config']['displayNameFromDS'] = name

                    #** build snapshotDataObj
                    snapshotDataObj['fields']=[ ts_part, value_part]
                    snapshotDataObj['name'] = name

                    if 'query' in target:
                        snapshotDataObj['meta'] = { 'executedQueryString': target['query'] }
                    else:
                        snapshotDataObj['meta'] = { 'executedQueryString': 'unknown' }
                    if 'refId' in target:
                        snapshotDataObj['refId'] = target['refId']
                    else:
                        snapshotDataObj['refId'] = '?'

                    self.panel.set_overrides( snapshotDataObj )
                    snapshotData.append( snapshotDataObj )

        # format is table : received results are same than for time_series
        # but they must be formatted differently :
        elif self.format == 'table':
            pass

        snapshotData = self.panel.set_transformations( snapshotData )

        return snapshotData
    #***********************************************
    def buildDisplayName( self, name, labels ):

        # /!\ special form "$tag_$var" meaning [[tag_$var]]
        if labels is not None:
            for m in re.finditer( resultsInfluxDB.var_tagfinder, name ):
                var = m.group(2)
                # if var is a label (not a $var!) should be substituted directly.
                if var in labels:
                    val = labels[var]
                    name = name.replace( m.group(1), val )
                # var is probably a $var, it would be substituted in two passes: [[tag_$var]], then tag value
                else:
                    name = name.replace( m.group(1), '[[tag_{0}]]'.format(var) )

        #* call parent method.
        name = resultsBase.buildDisplayName(self, name, labels)

        #** collect all tag_name from expression
        if labels is not None:
            for m in re.finditer( resultsInfluxDB.tagfinder, name ):
                var = m.group(2)
                if var in labels:
                    val = labels[var]
                    name = name.replace( m.group(1), val )

        return name

#***********************************************************************************************