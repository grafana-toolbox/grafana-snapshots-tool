#!/usr/bin/python3
# -*- coding: utf-8 -*-

from dataresults import dataresults
from grafana_snapshots.dataresults.panels import DefaultPanel

#***************************************************
class StatPanel(DefaultPanel):
    """
    """
    #***********************************************
    def __init__( *args, **kwargs ) -> None:

        self = args[0]
        DefaultPanel.__init__(self, kwargs)

    #***********************************************
    def get_FieldConfig( self, results ) -> list:

        return list()
#***************************************************