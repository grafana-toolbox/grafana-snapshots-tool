#!/usr/bin/python3
# -*- coding: utf-8 -*-
#***************************************************************************************
from urllib.parse import urlencode

#***************************************************************************************
def test_getRequest_influxdb_influxQL_with_var(build_config):

    build_config.buildGrafanaData(
        context= { 'vars': {
            'host': 'server1',
        } },
        time_from= '2022-10-28T12:00:00',
        time_to= '2022-10-28T13:00:00',
    )

    panel = build_config.readPanel('panels/grafana_9/influxQL_timeseries_vars_range.json')

    request = build_config.getRequest(panel)

    assert request is not None, "request not generated"
    assert request['data']['q'] == \
        'SELECT mean("value") FROM "logins.count" WHERE ("hostname" = \'server1\') AND time >= \'2022-10-28T10:00:00+00:00\' AND time <= \'2022-10-28T11:00:00+00:00\' GROUP BY time(10m), "hostname"', \
        'invalid query'

#***************************************************************************************
def test_getRequest_influxdb_flux_simple(build_config):

    build_config.buildGrafanaData(
        context= { 'vars': { } },
    )

    panel = build_config.readPanel('panels/grafana_9/flux_timeseries_novar_5m.json')

    request = build_config.getRequest(panel)

    assert request is not None, "request not generated"
    assert request['data']['queries'][0]['query'] == \
        'from(bucket: "HyperEncabulator")\r\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\r\n  |> filter(fn: (r) => r["_measurement"] == "TemperatureData")\r\n  |> filter(fn: (r) => r["MeasType"] == "actual")\r\n\r\n  |> filter(fn: (r) => r["_field"] == "Temperature")\r\n  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)\r\n  |> yield(name: "mean")', \
        'invalid query'

#***************************************************************************************
def test_getRequest_influxdb_flux_with_var(build_config):

    build_config.buildGrafanaData(
        context= { 'vars': { 'Tank': 'B4'} },
    )

    panel = build_config.readPanel('panels/grafana_9/flux_timeseries_vars_5m.json')

    request = build_config.getRequest(panel)

    assert request is not None, "request not generated"
    assert request['data']['queries'][0]['query'] == \
        'from(bucket: "HyperEncabulator")\r\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\r\n  |> filter(fn: (r) => r["_measurement"] == "TemperatureData")\r\n  |> filter(fn: (r) => r["MeasType"] == "setpoint" or r["MeasType"] == "actual")\r\n  |> filter(fn: (r) => r["Tank"] == "B4")\r\n  |> filter(fn: (r) => r["_field"] == "Temperature")\r\n  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)\r\n  |> yield(name: "mean")', \
        'invalid query'

#***************************************************************************************

#***************************************************************************************
def test_getRequest_graphite_with_vars(build_config):

    build_config.buildGrafanaData(
        context= { 'vars': {
            'app': 'backend',
            'server': ['backend_01', 'backend_02', 'backend_03'],
        } },
        time_from= '2022-10-28T12:00:00',
        time_to= '2022-10-28T13:00:00',
    )

    panel = build_config.readPanel('panels/grafana_9/graphite_timeseries_vars_range.json')

    request = build_config.getRequest(panel)

    assert request is not None, "request not generated"
    params = urlencode(request['data'])
    verify = urlencode( {
        'target': "groupByNode(movingAverage(apps.backend.{backend_01,backend_02,backend_03}.counters.requests.count, 10), 2, 'sum')",
        'from': 1666951200,
        'until': 1666954800,
        'format': 'json',
        'maxDataPoints': 300,
    })

    assert params == verify, 'invalid query'
