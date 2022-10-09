#!/usr/bin/python3
# -*- coding: utf-8 -*-

from distutils.version import LooseVersion
from grafana_snapshots.dataresults.panels import PanelDispatcher

from resultsMatrix import resultsMatrix
from resultsSQL import resultsSQL
from resultsFrame import resultsFrame

#***************************************************
class dataresults(object):
    # prometheus query change in v 8
    version_8 = LooseVersion('8')
    version_9 = LooseVersion('9')

    #***********************************************
    def __init__( *args, **kwargs ):
        self = args[0]

        self.type = kwargs.get('type', 'prometheus')
        version = kwargs.get('version')
        if version is None:
            version = dataresults.version_9
            kwargs['version'] = version

        if self.type == "prometheus":
            if version >= dataresults.version_8:
                klass = resultsFrame
            else:
                klass = resultsMatrix

        elif self.type in ('mssql', 'mysql', "postgres", "oracle"):
            klass = resultsSQL

        elif self.type == "influxdb":
            klass = resultsInflux

        elif self.type == "loki":
            klass = resultsStream

        elif self.type == "graphite":
            klass = resultsGraphite

        else:
            raise NotImplementedError('datasource type {0} not implemented.'.format(self.type))

        self.results = klass(kwargs)

    #***********************************************
    def get_snapshotData(self, target: dict)-> list:
        fields = self.results.get_snapshotData(target)
        return fields

#***************************************************
class resultsBase(object):
    #***********************************************
    def __init__( *args, **kwargs ):
        self = args[0]

        self.results = kwargs.get('result', None)
        if self.results is None:
            raise ValueError("results not set!")

        self.debug = kwargs.get('debug', False)
        self.panel = PanelDispatcher(kwargs('panel'))

    #***********************************************
    def results(self):
        return self.results

    #***********************************************
    def get_snapshotData(self, target: dict)-> list:
        raise NotImplementedError('method not implemented')

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
    def get_snapshotData(self, target: dict)-> list:
        fields = []
        return fields

#***************************************************
class resultsGraphite(resultsBase):
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
    def get_snapshotData(self, target: dict)-> list:
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
    def get_snapshotData(self, target: dict)-> list:
        fields = []
        return fields
