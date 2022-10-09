#!/usr/bin/python3
# -*- coding: utf-8 -*-

from dataresults import resultsBase

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
        fields = []
        return fields

#***************************************************
