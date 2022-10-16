#!/usr/bin/python3
# -*- coding: utf-8 -*-

from grafana_snapshots.dataresults.panels.default import DefaultPanel

#***************************************************
class TablePanel(DefaultPanel):
    """
    """
    #***********************************************
    def __init__( *args, **kwargs ) -> None:

        self = args[0]
        DefaultPanel.__init__(self, **kwargs)

        self.ts_fields.extend( [
            { 'name': 'color', 'type': 'copy_all', 'value': 'defaults.color', },
            { 'name': 'custom', 'type': 'copy', 'value': 'defaults.custom', 'exclude': [ 'axisLabel', 'scaleDistribution', 'spanNulls', 'stacking'], },
            { 'name': 'links', 'type': 'copy_all', 'value': 'defaults.links', },
            { 'name': 'thresholds', 'type': 'copy_all', 'value': 'defaults.thresholds', },
            { 'name': 'unit', 'type': 'copy_all', 'value': 'defaults.unit', },
            { 'name': 'noValue', 'type': 'copy_all', 'value': 'defaults.noValue', },
        ] )

        self.value_fields.extend( [
            { 'name': 'color', 'type': 'copy_all', 'value': 'defaults.color', },
            { 'name': 'custom', 'type': 'copy_all', 'value': 'defaults.custom', },
            { 'name': 'decimals', 'type': 'copy_all', 'value': 'defaults.decimals', },
            { 'name': 'displayName', 'type': 'copy_all', 'value': 'defaults.displayName', },
            { 'name': 'links', 'type': 'copy_all', 'value': 'defaults.links', },
            { 'name': 'mappings', 'type': 'copy_all', 'value': 'defaults.mappings', },
            { 'name': 'max', 'type': 'copy_all', 'value': 'defaults.max', },
            { 'name': 'min', 'type': 'copy_all', 'value': 'defaults.min', },
            { 'name': 'noValue', 'type': 'copy_all', 'value': 'defaults.noValue', },
            { 'name': 'thresholds', 'type': 'copy_all', 'value': 'defaults.thresholds', },
            { 'name': 'unit', 'type': 'copy_all', 'value': 'defaults.unit', },
        ] )

    #***********************************************
    def get_FieldsConfig(*args, **kwargs) -> list:
        self = args[0]
        results = args[1]

        fields = kwargs.get('fields', [] )
        res = []
        for field in fields:
            if 'type' in field and field['type'] == 'timestamp':
                config = self.get_FieldConfig(self.ts_fields, results)
            else:
                config = self.get_FieldConfig(self.value_fields, results)
            if 'config' in field['value']:
                field['value']['config'].update( config )
            else:
                field['value']['config'] = config
            res.append(field['value'])

        if len(res) == 0:
            res = [
                { 'config': self.get_FieldConfig(self.ts_fields, results) },
                { 'config': self.get_FieldConfig(self.value_fields, results) },
            ]

        return res

#***************************************************
