#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .resultsBase import resultsBase
from typing import Union

#***************************************************
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
                    if 'tags' in serie:
                        name = list(serie['tags'].values())[0]
                        value_part.update({
                            'labels': serie['tags'],
                        })
                    elif 'alias' in target:
                        name = target['alias']
                    else:
                        ####
                        # WARNING: take the name of the last serie : why but why not ?
                        ####
                        name = '{0}.{1}'.format(serie['name'], serie['columns'][1])

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

        return snapshotData

#***************************************************
