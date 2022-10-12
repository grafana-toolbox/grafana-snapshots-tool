#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .resultsBase import resultsBase

#***************************************************
class resultsFrame(resultsBase):
    """
    response contains a result with frames:
    e.g. Prometheus with Grafana server 9.x

    ## Response
    "response": {
        "results": {
            "[refId]": {
                "frames": [
                    "{frame_1}",
                    "{... frame_X ...}",
                ],
                "refId": "[refId]"
            }
        }
    }

    ## definitions:
    frame: {
        "schema": {
            "refId": "[val]"
            "meta" :{
                "type": ...,
                "executedQueryString": "expr...",
                "step": "[step value]",
                "custom": {
                    "resultType": "matrix",
                }
            },
            // one object by timeseries
            "fields": [
                //0: timestamp part
                {
                    "name": "Time",
                    "type": "time",
                    "typeInfo": {...},
                    "config": {
                        "interval": <val>
                    }

                },
                //1: value part
                {
                    "name": "Value",
                    "type": "number",
                    "typeInfo": {...},
                    "config": {
                        "displayNameFromDS": <val: localhost:9090>
                    },
                    "labels": {
                        "__name__":"up",
                        "instance": "localhost:9090",
                        "job": "prometheus",
                    }

                }

            ]
        },
        "data": {
            "values": [
                // 0: timestamp
                [
                    ts1,
                    ts2,
                    ...
                ],
                // 1: values
                [
                    val1,
                    val2,
                    ...
                ]
            ]
        }
    }
    """

    #***********************************************
    def get_snapshotData(self, target: dict)-> list:
        snapshotData = list()
        snapshotDataObj = {}
        (ts_part, value_part) = ( None, None)

        if not self.results or 'results' not in self.results \
            or len(self.results['results']) <= 0:
            return snapshotData

        for _, refId in self.results['results'].items():
            snapshotDataObj = {}

            for frame in refId['frames']:
                ts = frame['data']['values'][0]
                values = frame['data']['values'][1]

                (ts_part, value_part) = self.panel(frame, values)
                #** build timestamp list
                ts_part.update( {
                    'name': 'Time',
                    'type': 'time',
                    'values': ts
                })

                values_info = frame['schema']['fields'][1]

                value_part.update( {
                    'labels': values_info['labels'],
                    'name': values_info['name'],
                    'type': values_info['type'],
                    'values': values
                } )

                name = values_info['config']['displayNameFromDS']
                value_part['config']['displayNameFromDS'] = name
 

            #** build snapshotDataObj
            if ts_part is not None and value_part is not None:
                snapshotDataObj['fields']=[ ts_part, value_part]
                snapshotDataObj['meta'] = frame['schema']['meta']
                # snapshotDataObj['name'] = name
                snapshotDataObj['name'] = name
                snapshotDataObj['refId'] = target['refId']

            snapshotData.append( snapshotDataObj )

        return snapshotData

#***************************************************
