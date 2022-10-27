#!/usr/bin/python3
# -*- coding: utf-8 -*-
#***************************************************************************************
import grafana_snapshots.grafana as Grafana
from grafana_snapshots.grafanaData import GrafanaData

#***************************************************************************************
#   ^
#  /!\ theses tests only work when host is connected to internet and has access to https://play.grafana.org/
# /___\
##***************************************************************************************
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
