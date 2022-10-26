#!/usr/bin/python3
# -*- coding: utf-8 -*-
#***************************************************************************************
import grafana_snapshots.grafana as Grafana
from grafana_snapshots.grafanaData import GrafanaData

#***************************************************************************************
def test_getdata_influxdb_flux(build_config):

    grafana_api = Grafana.Grafana( url="https://play.grafana.org/" )

    data_api = GrafanaData(
        api=grafana_api,
        context= { 'vars': {} },
    )
    panel = build_config.readPanel('panels/grafana_9/flux_timeseries_5m.json')

    data_api.dashboard = {
        'panels': [ panel ],
    }
    res = data_api.get_dashboard_data()

    assert res is not None, "snapshot not generated"

#***************************************************************************************
