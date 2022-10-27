#!/usr/bin/python3
# -*- coding: utf-8 -*-
#***************************************************************************************

#***************************************************************************************
def test_getdata_influxdb_flux_simple(build_config):

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
def test_getdata_influxdb_flux_with_var(build_config):

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
