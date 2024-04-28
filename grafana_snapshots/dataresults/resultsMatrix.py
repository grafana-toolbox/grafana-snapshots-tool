#!/usr/bin/python3
# -*- coding: utf-8 -*-
#***********************************************************************************************
import json, re

from .resultsBase import resultsBase
from typing import Union

#***********************************************************************************************
class resultsMatrix(resultsBase):
    """
    response contains a result with matrix:
    e.g.: Prometheus with Grafana server v 7.x
    "response": {
        "status": "success",
        "data": {
            "resultType": "matrix",
            "result": [ // liste of metrics
                { a matrix }
            ]
        }
    }

    Definition:
    matrix: {
        "metric": {
            "<label_names>": "label_values",
            e.g
            ...
            "__name__": "<metric_name>"
            "job": "...",
            "instance": "...",
            "host": "...",
            ...
        },
        "values": [
            ["timestamp in second", "value_1"],
            ...
            ["timestamp in second", "value_N"]
        ]
    }
    """
    #***********************************************
    def get_snapshotData(self, targets: Union[list, dict])-> list:
        """
        one snapshotDataObj is a result from query_range
        it is composed from 2 fields :
          * one with series of timestamp values 
          * one with series of queried values
        """
        snapshotData = list()
        snapshotDataObj = {}
        (ts_part, value_part) = ( None, None)

        if not self.results or 'status' not in self.results \
            or self.results['status'] != 'success':
            return snapshotData

        if targets is None:
            targets = []
        if isinstance(targets, dict):
            targets = [ targets ]

        # required format is time_series:
        if self.format == 'time_series':

            for idx, result in enumerate(self.results['data']['result']):
                snapshotDataObj = {}
                labels = {}


                if len(targets)> idx:
                    target = targets[idx]
                else:
                    target = {}
                #*** split list of [ (ts,val),...] from values into 2 lists of (ts, tsx,...) (val, valx,...)
                ts=list()
                values=list()

                # min = None
                # if def_min is not None:
                #     min = def_min
                # max = None
                # if def_max is not None:
                #     max = def_max

                for value_pair in result['values']:
                    if self.debug:
                        self.logger.debug("ts={0} - val={1}".format(value_pair[0], value_pair[1]))
                    ts.append(int(value_pair[0]) * 1000)
                    value = value_pair[1]
                    if value is None or value == 'NaN':
                        value = None
                    else:
                        value = float( value )

                    # if def_min is None and (min is None or min > value):
                    #     min = value
                    # if def_max is None and (max is None or max < value):
                    #     max = value

                    values.append(value)
                    if self.debug:
                        self.logger.debug("ts={} - value={} - min: {} - max {}".format(value_pair[0], value, min, max))

                (ts_part, value_part) = self.panel.get_FieldsConfig(result, None, values=values)
                #** build timestamp list
                ts_part.update( {
                    'name': 'Time',
                    'type': 'time',
                    'values': ts
                })

                for key in result['metric'].keys():
                    if key == '__name__':
                        continue
                    else:
                        labels[key] = result['metric'][key]

                name = ''
                displayName = ''
                #** old panel version has not this attribute
                if not 'legendFormat' in target:
                    target['legendFormat'] = ''
                if target['legendFormat'] is None or target['legendFormat'] == '':
                    #** if expr is a simple metric use its name
                    #** else use label of metrics
                    if 'expr' in target:
                        if re.match(r'^[a-zA-Z0-9_]+$', target['expr']):
                            name = target['expr']
                    name = name + json.dumps(labels)
                else:
    #** TO DO build name on template
                    name = target['legendFormat']
                    displayName = self.buildDisplayName( name, labels )

                labels['displayName'] = name
    
                value_part.update( {
                    'labels': labels,
                    'name': 'Value',
                    'type': 'number',
                    'values': values
                } )
                value_part['config']['displayName'] = displayName

                #** build snapshotDataObj
                if ts_part is not None and value_part is not None:
                    snapshotDataObj['fields']=[ ts_part, value_part]
                    snapshotDataObj['meta'] = { 'preferredVisualisationType': 'graph' }
                    # snapshotDataObj['name'] = name
                    snapshotDataObj['name'] = displayName
                    if 'refId' in target:
                        snapshotDataObj['refId'] = target['refId']
                    else:
                        snapshotDataObj['refId'] = '?'
                # if self.debug:
                #    self.logger.debug("build_timeseries_snapshotData::snapshot[{0}]: {1}".format(target['refId'], snapshotDataObj ))

                snapshotData.append( snapshotDataObj )

        # format is table : received results are same than for time_series
        # but they must be formatted differently :
        elif self.format == 'table':
            if self.logger is not None:
                self.logger.warning("result MATRIX table not implemented!")

        snapshotData = self.panel.set_transformations( snapshotData )

        return snapshotData

#***************************************************
