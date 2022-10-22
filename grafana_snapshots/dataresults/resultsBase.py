#!/usr/bin/python3
# -*- coding: utf-8 -*-
#**********************************************************************************
import re
from jinja2 import Template

from grafana_snapshots.dataresults.panels.dispatcher import PanelDispatcher

#**********************************************************************************
class resultsBase(object):
    #***********************************************
    def __init__( *args, **kwargs ):
        self = args[0]

        self.results = kwargs.get('results', None)
        if self.results is None:
            raise ValueError("results not set!")

        self.format = kwargs.get('format', 'time_series')

        self.symbols_vars = kwargs.get('vars', {})

        self.debug = kwargs.get('debug', False)
        self.panel = PanelDispatcher(
            version = kwargs.get('version'),
            panel = kwargs.get('panel'),
        )

    #***********************************************
    def results(self):
        return self.results

    #***********************************************
    def get_snapshotData(self, target: dict)-> list:
        raise NotImplementedError('method not implemented')

    #***********************************************
    def buildDisplayName( self, name, labels ):

        if re.match(r'{{', name):
            tm = Template( name )
            name = tm.render( labels )
        if re.match(r'\$', name):
        #** replace all variables name with values in expr
            for var in self.symbols_vars:
                name = name.replace( '$' + var, self.symbols_vars[var] )
    #      if self.debug:
    #         print('buildDisplayName::result displayName="{0}"'.format(name))

        return name

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
    def get_snapshotData(self, target: dict)-> list:
        fields = []
        return fields

#**********************************************************************************
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

#**********************************************************************************
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

#**********************************************************************************