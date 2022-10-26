#!/usr/bin/python3
# -*- coding: utf-8 -*-

from distutils.version import LooseVersion
from typing import Union

from .resultsBase import resultsStream
from grafana_snapshots.dataresults.resultsMatrix import resultsMatrix
from grafana_snapshots.dataresults.resultsSQL import resultsSQL
from grafana_snapshots.dataresults.resultsFrame import resultsFrame
from grafana_snapshots.dataresults.resultsGraphite import resultsGraphite
from grafana_snapshots.dataresults.resultsInfluxDB import resultsInfluxDB

#***************************************************
class dataresults(object):
    # prometheus query change in v 8
    version_8 = LooseVersion('8')
    version_9 = LooseVersion('9')

    #***********************************************
    def __init__( *args, **kwargs ):
        self = args[0]

        self.type = kwargs.get('type', 'prometheus')
        version = kwargs.get('version')
        if version is None:
            version = dataresults.version_9
            kwargs['version'] = version

        if self.type == "prometheus":
            if version >= dataresults.version_8:
                klass = resultsFrame
            else:
                klass = resultsMatrix

        elif self.type in ('mssql', 'mysql', "postgres", "oracle"):
            klass = resultsSQL

        elif self.type == "influxdb":
            dialect = kwargs.get('dialect', None)
            if dialect == 'Flux':
                klass = resultsFrame
            else:
                klass = resultsInfluxDB

        elif self.type == "loki":
            klass = resultsStream

        elif self.type == "graphite":
            klass = resultsGraphite

        else:
            raise NotImplementedError('datasource type {0} not implemented.'.format(self.type))

        self.results = klass(**kwargs)

    #***********************************************
    def get_snapshotData(self, targets: Union[list, dict])-> list:
        fields = self.results.get_snapshotData(targets)
        return fields

#***************************************************