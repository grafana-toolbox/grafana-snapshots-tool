#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .resultsBase import resultsBase

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
    def get_snapshotData(self, target: dict)-> list:
        fields = []
        return fields

#***************************************************
