#!/usr/bin/python3
# -*- coding: utf-8 -*-

from grafana_snapshots.dataresults.panels.default import DefaultPanel

#***************************************************
class GraphPanel(DefaultPanel):
    """
    """
    #***********************************************
    def __init__( *args, **kwargs ) -> None:

        self = args[0]
        DefaultPanel.__init__(self, kwargs)
        self.ts_fields.extend( [
            { 'name': 'unit', 'type': 'static', 'value': 'time:YYYY-MM-DD HH:mm:ss', }
        ] )
        self.value_fields.extend( [
            { 'name': 'decimals', 'type': 'copy_all', 'value': 'defaults', },
            { 'name': 'mappings', 'type': 'copy_all', 'value': 'defaults', },
            { 'name': 'thresholds', 'type': 'copy_all', 'value': 'defaults', },
            { 'name': 'unit', 'type': 'copy_all', 'value': 'defaults', },
        ] )

    #***********************************************
    def get_FieldsConfig(*args, **kwargs  ) -> list:
        self = args[0]
        results = args[1]

        values = kwargs.get('values', list() )
        (ts_part, value_part) = DefaultPanel.get_FieldsConfig(self, results)
        fieldConfig = self.panel['fieldConfig']

        def_min = None
        if 'min' in fieldConfig['defaults']:
            def_min = fieldConfig['defaults']['min']

        def_max = None
        if 'max' in fieldConfig['defaults']:
            def_max = fieldConfig['defaults']['max']

        labels = {}
        min = None
        if def_min is not None:
            min = def_min
        max = None
        if def_max is not None:
            max = def_max
        for value in values:
            if def_min is None and (min is None or min > value):
                min = value
            if def_max is None and (max is None or max < value):
                max = value

        value_part['config'].update( {
            'max': max,
            'min': min,
        } )

        return [ ts_part, value_part]
#***************************************************