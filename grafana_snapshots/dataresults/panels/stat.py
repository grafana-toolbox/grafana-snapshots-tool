#!/usr/bin/python3
# -*- coding: utf-8 -*-

from grafana_snapshots.dataresults.panels.default import DefaultPanel

#***************************************************
class StatPanel(DefaultPanel):
    """
    """
    #***********************************************
    def __init__( *args, **kwargs ) -> None:

        self = args[0]
        DefaultPanel.__init__(self, **kwargs)

        self.ts_fields.extend( [
            { 'name': 'color', 'type': 'copy_all', 'value': 'defaults.color', },
            { 'name': 'links', 'type': 'copy_all', 'value': 'defaults.links', },
            { 'name': 'thresholds', 'type': 'copy_all', 'value': 'defaults.thresholds', },
            { 'name': 'unit', 'type': 'copy_all', 'value': 'defaults.unit', },
            { 'name': 'noValue', 'type': 'copy_all', 'value': 'defaults.noValue', },
        ] )

        self.value_fields.extend( [
            { 'name': 'color', 'type': 'copy_all', 'value': 'defaults.color', },
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

#***************************************************
