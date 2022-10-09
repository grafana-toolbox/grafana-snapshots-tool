#!/usr/bin/python3
# -*- coding: utf-8 -*-

from dataresults import dataresults
from dataresults.panels.timeseries import TimeSeriesPanel
from dataresults.panels.graph import GraphPanel
from dataresults.panels.stat import StatPanel
from dataresults.panels.table import TablePanel

#***************************************************
class PanelDispatcher:
    """
    ## Panel definition
    ### from FieldConfig defaults

    #### color
    #### custom
    #### mappings
    #### thresholds
    """
    #***********************************************
    def __init__( *args, **kwargs ) -> None:

        self = args[0]

        panel = kwargs.get('panel')
        if panel is None:
            raise Exception("panel not set")

        self.version = kwargs.get('version')

        if panel["type"] == 'timeseries':
            klass = TimeSeriesPanel
        if panel["type"] == 'graph':
            klass = GraphPanel
        elif panel["type"] == 'stat':
            klass = StatPanel
        elif panel["type"] == 'table':
            klass = TablePanel
        else:
            if self.version < dataresults.version_8:
                klass = GraphPanel
            else:
                klass = TimeSeriesPanel

        self.panel = klass(panel)

    #***********************************************

#***************************************************
class DefaultPanel:
    #***********************************************
    def __init__( *args, **kwargs ) -> None:

        self = args[0]
        self.panel = kwargs.get('panel')
        self.ts_fields = [
        ]

        self.value_fields = [
        ]

    #***********************************************
    def get_FieldConfig( self, fields: dict, results: dict, ) -> list:
        config_elmt = {} 
        for field in fields:
            if field['type'] == 'static':
                config_elmt[field['name']] = field['value']
            elif field['type'] == 'copy':
                fieldConfig = self.panel['fieldConfig']
                if field['value'] == 'defaults':
                    if 'defaults' in fieldConfig and fieldConfig['defaults'] is not None \
                        and field['name'] in fieldConfig['defaults']:
                        config_elmt[field['name']] = fieldConfig['defaults'][field['name']]
                elif field['value'] == 'defaults.custom':
                    if 'defaults' in fieldConfig and fieldConfig['defaults'] is not None \
                        and 'custom' in fieldConfig['defaults'] \
                        and field['name'] in fieldConfig['defaults']['custom']:
                        config_elmt[field['name']] = fieldConfig['defaults']['custom'][field['name']]
        return config_elmt

    #***********************************************
    def get_FieldsConfig( self, results: dict ) -> list:
        return [
            { 'config': self.get_FieldConfig(self.ts_fields, results) },
            { 'config': self.get_FieldConfig(self.value_fields, results) },
        ]

#***************************************************