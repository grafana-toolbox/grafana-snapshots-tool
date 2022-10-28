#!/usr/bin/python3
# -*- coding: utf-8 -*-
#**********************************************************************************
from .resultsBase import resultsBase
from typing import Union

#**********************************************************************************
class resultsStream(resultsBase):
    """
    response contains a result with streams:
    e.g.: Loki
    "response": {
        "status": "success",
        "data": {
            "resultType": "streams",
            "result": [ // liste of streams
                { a stream }
            ],
            "stats": {
                stats...
            }
        }
    }

    Definition:
    stream: {
        "stream": {
            "<label_names>": "label_values",
            e.g
            ...
            "job": "...",
            "filename": "...",
            "host": "...",
            ...
        },
        "values": [
            ["timestamp nano", "message line"],
        ]
    }
    """
    #***********************************************
    def get_snapshotData(self, targets: list)-> list:
        snapshotData = list()
        snapshotDataObj = {}
        (ts_part, value_part, ref_id) = ( None, None, None)

        if not self.results or 'results' not in self.results \
            or len(self.results['results']) <= 0:
            return snapshotData

        if targets is None:
            targets = []
        if isinstance(targets, dict):
            targets = [ targets ]

        return snapshotData

#**********************************************************************************