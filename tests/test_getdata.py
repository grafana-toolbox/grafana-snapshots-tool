#!/usr/bin/python3
# -*- coding: utf-8 -*-
#***************************************************************************************
import grafana_snapshots.grafana as Grafana
from grafana_snapshots.grafanaData import GrafanaData

#***************************************************************************************
#   .
#  /|\ theses tests only work when host is connected to internet and has access to https://play.grafana.org/
# /_._\
#***************************************************************************************
#***************************************************************************************
def test_getdata_influxdb_influxQL(build_config):

    grafana_api = Grafana.Grafana( url="https://play.grafana.org/" )

    data_api = GrafanaData(
        api=grafana_api,
        context= { 'vars': {
             'host': 'server2',
             'host2': '(10\.1\.100\.1|10\.1\.100\.10)',
            } },
        time_from = 'now-1h',
    )
    panel = build_config.readPanel('panels/grafana_9/influxQL_timeseries_vars_range.json')

    data_api.dashboard = {
        'panels': [ panel ],
    }
    res = data_api.get_dashboard_data()

    assert res, "snapshot not generated"
    assert len(data_api.dashboard['panels'][0]['snapshotData']) == 4, 'invalid snapshot data length'
    # serie A
    serie = data_api.dashboard['panels'][0]['snapshotData'][0]
    assert serie['name'] == 'logins.count.mean server1', 'invalid name for metric of serie 0'
    assert len(serie['fields'][0]['values']) in [7, 8], 'invalid snapshot data length for serie 0'
    # serie B
    serie = data_api.dashboard['panels'][0]['snapshotData'][1]
    assert serie['name'] == 'logins.count.mean server2', 'invalid name for metric of serie 0'
    assert len(serie['fields'][0]['values']) in [7, 8], 'invalid snapshot data length for serie 0'
    # serie C
    serie = data_api.dashboard['panels'][0]['snapshotData'][2]
    assert serie['name'] == 'logins.count.mean 10.1.100.1', 'invalid name for metric of serie 0'
    # serie D
    serie = data_api.dashboard['panels'][0]['snapshotData'][3]
    assert serie['name'] == 'logins.count.mean 10.1.100.10', 'invalid name for metric of serie 0'

#***************************************************************************************
def test_getdata_influxdb_flux(build_config):

    grafana_api = Grafana.Grafana( url="https://play.grafana.org/" )

    data_api = GrafanaData(
        api=grafana_api,
        context= { 'vars': { 'Tank': 'B4'} },
        time_from = 'now-5m',
    )
    panel = build_config.readPanel('panels/grafana_9/flux_timeseries_vars_5m.json')

    data_api.dashboard = {
        'panels': [ panel ],
    }
    res = data_api.get_dashboard_data()

    assert res is not None, "snapshot not generated"

#***************************************************************************************
