#!/usr/bin/python3
# -*- coding: utf-8 -*-

#***************************************************
class dataresults(object):
    #***********************************************
    def __init__( *args, **kwargs ):
        self = args[0]

        self.type = kwargs('type', 'prometheus')
        if self.type == "prometheus":
            klass = resultsFrame
        elif self.type in ('mssql', 'mysql', "postgres", "oracle"):
            klass = resultsSQL
        elif self.type == "influxdb":
            klass = resultsInflux
        elif self.type == "loki":
            klass = resultsStream
        elif self.type == "graphite":
            klass = resultsGrafite
        else:
            raise NotImplementedError('datasource type {0} not implemented.'.format(self.type))

        self.results = klass(kwargs('results'))

    #***********************************************
    def get_snapshotData(self, panel: dict)-> list:
        fields = self.results.get_snapshotData(panel)
        return fields

#***************************************************
class resultsBase(object):
    #***********************************************
    def __init__( *args, **kwargs ):
        self = args[0]

        self.results = kwargs('result', None)
        if self.results is None:
            raise ValueError("results not set!")

    #***********************************************
    def results(self):
        return self.results

#***************************************************
class resultsFrame(resultsBase):
    """
    response contains a result with frames:
    Prometheus

    "response": {
        "results": {
            "[refId]": {
                "frames": [

                ],
                "refId": "[refId]"
            }
        }
    }
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
    def get_snapshotData(self, panel: dict)-> list:
        fields = []
        return fields

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
    def get_snapshotData(self, panel: dict)-> list:
        fields = []
        return fields

#***************************************************
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
    def get_snapshotData(self, panel: dict)-> list:
        fields = []
        return fields

#***************************************************
class resultsGrafite(resultsBase):
    """
    response contains an array of results:
    e.g.: Graphite
    "response": [
        {
            "target": "<query...>",
            "datapoints": [
                [ <values>, timestamp ],
                [ ... ]
            ]
        }
    ]
    """
    #***********************************************
    def get_snapshotData(self, panel: dict)-> list:
        fields = []
        return fields

#***************************************************
class resultsInflux(resultsBase):
    """
    response contains an array of results:
    e.g.: Graphite
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
        "columns": [
            "time", "<others columns names>",
        ],
        "values":[
            [ timestamp_1, value_1],
            [ timestamp_2, value_2],
            [ ..., ...]
        ]
    }
    """
    #***********************************************
    def get_snapshotData(self, panel: dict)-> list:
        fields = []
        return fields
