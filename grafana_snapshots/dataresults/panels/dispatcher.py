#!/usr/bin/python3
# -*- coding: utf-8 -*-
#**********************************************************************************
from distutils.version import LooseVersion

from grafana_snapshots.dataresults.panels.timeseries import TimeSeriesPanel
from grafana_snapshots.dataresults.panels.graph import GraphPanel
from grafana_snapshots.dataresults.panels.stat import StatPanel
from grafana_snapshots.dataresults.panels.table import TablePanel

#**********************************************************************************
class PanelDispatcher:
    """
    ## Panel definition
    ### from FieldConfig defaults

    #### color
    #### custom
    #### mappings
    #### thresholds
    """
    # prometheus query change in v 8
    version_8 = LooseVersion('8')
    version_9 = LooseVersion('9')

    #***********************************************
    def __init__( *args, **kwargs ) -> None:

        self = args[0]

        panel = kwargs.get('panel')
        if panel is None:
            raise Exception("panel not set")

        self.version = kwargs.get('version')

        if panel["type"] == 'timeseries':
            klass = TimeSeriesPanel
        elif panel["type"] == 'graph':
            klass = GraphPanel
        elif panel["type"] == 'stat':
            klass = StatPanel
        elif panel["type"] == 'table':
            klass = TablePanel
        else:
            if self.version < PanelDispatcher.version_8:
                klass = GraphPanel
            else:
                klass = TimeSeriesPanel

        self.panelObj = klass(panel=panel)

    #***********************************************
    # def __call__(*args, **kwargs) -> list:
    #     self = args[0]
    #     results = args[1]
    #     return self.panelObj.get_FieldsConfig(results, **kwargs)

    #***********************************************
    def get_FieldsConfig(*args, **kwargs) -> list:
        self = args[0]
        return self.panelObj.get_FieldsConfig(*args[1:], **kwargs)

    #***********************************************
    def set_overrides(self, snapshotDataElmt) -> None:
        self.panelObj.set_overrides(snapshotDataElmt)


    #***********************************************
    def set_transformations(self, snapshotData) -> None:
        self.panelObj.set_transformations( snapshotData )

    #***********************************************
    # def __getattr__(*args, **kwargs) -> list:
    #     self = args[0]
    #     results = args[1]
    #     return self.panel.get_FieldsConfig(results, **kwargs)
    # def __getattr__(self, item, results, **kwargs) -> list:
    #     if item == 'get_FieldsConfig':
    #         return self.panel.get_FieldsConfig(results, **kwargs)
    #     else:
    #         return list()

#**********************************************************************************