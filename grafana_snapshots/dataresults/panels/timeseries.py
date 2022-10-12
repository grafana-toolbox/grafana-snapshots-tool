#!/usr/bin/python3
# -*- coding: utf-8 -*-

from grafana_snapshots.dataresults.panels.default import DefaultPanel

#***************************************************
class TimeSeriesPanel(DefaultPanel):
    """
    ## 2 fields
    1. timestamp part:
        - config ts
        - name
        - type
        - values
    2. value part:
        * config value
        * name    #***********************************************
    def __init__( *args, **kwargs ) -> None:

        self = args[0]
        self.panel = kwargs('panel')
        * type
        * values
    ## config ts:
        - color from fieldConfig.defaults.color
        - custom:
            axisCenteredZero, axisColorMode, axisPlacement, barAlignment,
            drawStyle, fillOpacity, gradientMode, hideFrom, lineInterpolation,
            lineWidth, pointSize, showPoints, thresholdsStyle
            => fieldConfig.defaults.custom except: [
                axisLabel, scaleDistribution, spanNulls, stacking
            ]
        - interval: ?
        - thresholds: fieldConfig.defaults.thresholds
    ## config val:
        - color from fieldConfig.defaults.color
        - custom:
            axisCenteredZero, axisColorMode, axisLabel, axisPlacement, barAlignment,
            drawStyle, fillOpacity, gradientMode, hideFrom, lineInterpolation,
            lineWidth, pointSize, scaleDistribution, showPoints, spanNulls, stacking, thresholdsStyle
            => fieldConfig.defaults.custom 
        - displayNameFromDS: ?
        - mappings: [],
        - thresholds: fieldConfig.defaults.thresholds

    """
    #***********************************************
    def __init__( *args, **kwargs ) -> None:

        self = args[0]
        DefaultPanel.__init__(self, **kwargs)

        self.ts_fields.extend( [
            { 'name': 'color', 'type': 'copy_all', 'value': 'defaults.color', },
            { 'name': 'custom', 'type': 'copy', 'value': 'defaults.custom', 'exclude': [ 'axisLabel', 'scaleDistribution', 'spanNulls', 'stacking'], },
            { 'name': 'thresholds', 'type': 'copy_all', 'value': 'defaults.thresholds', },
        ] )

        self.value_fields.extend( [
            { 'name': 'color', 'type': 'copy_all', 'value': 'defaults.color', },
            { 'name': 'custom', 'type': 'copy_all', 'value': 'defaults.custom', },
            { 'name': 'mappings', 'type': 'copy_all', 'value': 'defaults.mappings', },
            { 'name': 'thresholds', 'type': 'copy_all', 'value': 'defaults.thresholds', },
        ] )

#***************************************************
