#!/usr/bin/python3
# -*- coding: utf-8 -*-
#**********************************************************************************
import re
from jinja2 import Template
from typing import Union

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
        self.logger = kwargs.get('logger')
        if self.logger is None:
            self.debug = False

        self.panel = PanelDispatcher(
            version = kwargs.get('version'),
            panel = kwargs.get('panel'),
        )

    #***********************************************
    def results(self):
        return self.results

    #***********************************************
    def get_snapshotData(self, targets: Union[list, dict])-> list:
        raise NotImplementedError('method not implemented')

    #***********************************************
    def buildDisplayName( self, name:str, labels: dict ):

        if labels is not None and re.search(r'{{', name):
            tm = Template( name )
            name = tm.render( labels )

        #** replace all variables name with values in expr
        if re.search(r'\$', name):
            for var in self.symbols_vars:
                name = name.replace( '$' + var, self.symbols_vars[var] )

        # if self.debug and self.logger is not None:
        #     self.logger.debug("buildDisplayName::result displayName=\"{0}\"}".format(name))

        return name

    #***********************************************
    def buildLegend(self, labels: dict)->str:
        """
        generate legend String from labels
        => "{ label_key=\"label_value\"}"

        FORMAT: 
        labels: dict

        RETURN:
         str: "{ label_key=\"label_value\",}"
        """
        res = []
        for key,val in labels.items():
            res.append( "{0}=\"{1}\"".format(key, val))
        return "{%s}" % ', '.join(res)

#**********************************************************************************