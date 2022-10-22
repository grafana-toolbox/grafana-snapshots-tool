import pytest
from distutils.version import LooseVersion

from grafana_snapshots.dataresults.dataresults import dataresults

datasource_type = 'prometheus'
api_version = LooseVersion('9.2.1')

#***************************************************************************************
def test_ts_ts(build_config):
    # read the datasource
    content = build_config.readResponse('queries/grafana_9/prometheus/two_timeseries_5m.json')
    format = 'time_series'
    # read the panel
    panel = build_config.readPanel('panels/grafana_9/two_timeseries.json')
    target = None
    dataRes = dataresults( 
        type=datasource_type,
        format=format,
        results=content,
        version=api_version,
        panel=panel)
    snapshotData = dataRes.get_snapshotData(target)

    assert snapshotData is not None, "invalid data"
    # two ts results
    assert len(snapshotData) == 2 , 'invalid snapshot data length wanted 2 but is {}'.format(len(snapshotData))
    # two fields in result: ts and value
    assert len(snapshotData[0]['fields']) == 2 , 'invalid snapshot data fields length wanted 2 but is {}'.format(len(snapshotData))

    # check data length
    # length = content['data']['result'][0]['values']
    assert len(content['results']['A']['frames'][0]['data']['values'][0]) == len(snapshotData[0]['fields'][0]['values']), 'invalid snapshot data ts length'
    assert len(content['results']['B']['frames'][0]['data']['values'][0]) == len(snapshotData[1]['fields'][0]['values']), 'invalid snapshot data value length'

#***************************************************************************************
def test_ts_instant_ts(build_config):
    # read the datasource
    content = build_config.readResponse('queries/grafana_9/prometheus/timeseries_instant.json')
    format = 'time_series'
    # read the panel
    panel = build_config.readPanel('panels/grafana_9/timeseries_instant.json')
    target = None
    dataRes = dataresults( 
        type=datasource_type,
        format=format,
        results=content,
        version=api_version,
        panel=panel)
    snapshotData = dataRes.get_snapshotData(target)

    assert snapshotData is not None, "invalid data"
    # two ts results
    assert len(snapshotData) == 3 , 'invalid snapshot data length wanted 2 but is {}'.format(len(snapshotData))
    # two fields in result: ts and value
    assert len(snapshotData[0]['fields']) == 2 , 'invalid snapshot data fields length wanted 2 but is {}'.format(len(snapshotData))

    # check data length
    # length = content['data']['result'][0]['values']
    assert len(content['results']['A']['frames'][0]['data']['values'][0]) == len(snapshotData[0]['fields'][0]['values']), 'invalid snapshot data ts length'
