#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .resultsBase import resultsBase
from typing import Union

#***************************************************
class resultsSQL(resultsBase):
    """
    response contains a result with series or table:
    Oracme, Postgres, Mysql, MSSQL

    "response": {
        "results": {
            "refId": {
                "meta": {
                    "executedQueryString": "<sql>",
                    "rowCount": X,
                    "transformation": [
                        liste of transformations
                    ]
                },
                "series": [
                    if type is timeseries or null,
                    list of timeseries

                ],
                "tables": [
                    if type is table or null
                ],
                "dataframes": [ list or null ]
            }
        }
    }

    Defitions:

    timeserie: {
        "name": "<name of the timeseries>",
        "points": [
            [ value1, timestamp_ms_1],
            [ value2, timestamp_ms_2],
            [ ... ]
        ]
    }

    table: {
        "columns": [ liste of object { "<type>": "<column_name>" } ],
        "rows": [
            [ liste of values of row 0],
            [ ... row 1 ],
            [ ... ]
        ],
        "type": "table",
        "refId": "[refId]",
        "mata": { same meta object again },
    }
    """
    #***********************************************
    def get_snapshotData(self, targets: Union[list, dict])-> list:
        snapshotData = list()
        if self.logger is not None:
            self.logger.warning("results Stream not implemented!")
        return snapshotData

        snapshotDataObj = {}
        (ts_part, value_part) = ( None, None)

        if not self.results or 'status' not in self.results \
            or self.results['status'] != 'success':
            return snapshotData

        if targets is None:
            targets = []
        if isinstance(targets, dict):
            targets = [ targets ]

        # NOT YET IMPLEMENTED

        snapshotData = self.panel.set_transformations( snapshotData )

        return snapshotData

#***************************************************
