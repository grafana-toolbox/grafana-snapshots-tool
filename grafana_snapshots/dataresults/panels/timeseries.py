#!/usr/bin/python3
# -*- coding: utf-8 -*-

from dataresults import dataresults
from grafana_snapshots.dataresults.panels import DefaultPanel

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
        DefaultPanel.__init__(self, kwargs)

    #***********************************************
    def get_FieldConfig( self, results ) -> list:

        # Panel.__init__(self, **{ 'type': 'timeseries'} )


        # fields: timestamp part
        #   config:
        #       color
        #       custom
        #       interval ?
        #       thresholds

        # fields: value part
        #   config:
        #       color
        return list()
#***************************************************
