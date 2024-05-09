#!/usr/bin/python3
# -*- coding: utf-8 -*-
#**********************************************************************************
from grafana_snapshots.dataresults.panels.default import DefaultPanel

#**********************************************************************************
class GraphPanel(DefaultPanel):
    """
    """
    #***********************************************
    def __init__( *args, **kwargs ) -> None:

        self = args[0]
        DefaultPanel.__init__(self, **kwargs)
        self.ts_fields.extend( [
            { 'name': 'unit', 'type': 'static', 'value': 'time:YYYY-MM-DD HH:mm:ss', }
        ] )
        self.value_fields.extend( [
            { 'name': 'decimals', 'type': 'copy_all', 'value': 'defaults.decimals', },
            { 'name': 'mappings', 'type': 'copy_all', 'value': 'defaults.mappings', },
            { 'name': 'thresholds', 'type': 'copy_all', 'value': 'defaults.thresholds', },
            { 'name': 'unit', 'type': 'copy_all', 'value': 'defaults.unit', },
        ] )

    #***********************************************
    def get_FieldsConfig(*args, **kwargs  ) -> list:
        self = args[0]
        results = args[1]

        (ts_part, value_part) = DefaultPanel.get_FieldsConfig(self, results)

        return [ ts_part, value_part]

#**********************************************************************************