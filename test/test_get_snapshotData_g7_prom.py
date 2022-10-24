import pytest
from distutils.version import LooseVersion

from grafana_snapshots.dataresults.dataresults import dataresults

datasource_type = 'prometheus'
api_version = LooseVersion('7.5.11')

#***************************************************************************************
def test_data_ts_range_panel_ts(build_config):
    # read the datasource
    content = build_config.readResponse('queries/grafana_7/prometheus/timeseries_5m.json')
    format = 'time_series'
    # read the panel
    panel = build_config.readPanel('panels/grafana_7/timeseries.json')
    # build a target
    # if 'targets' in panel and len(panel['targets'])>0:
    #     target = panel['targets'][0]
    #     target['refId'] = 'A'
    # else:
    #     raise Exception("can' build target from panel")

    dataRes = dataresults( 
        type=datasource_type,
        format=format,
        results=content,
        version=api_version,
        panel=panel)
    snapshotData = dataRes.get_snapshotData(panel['targets'])

    assert snapshotData is not None, "invalid data"
    # only one result
    assert len(snapshotData) == 1 , 'invalid snapshot data length wanted 1 but is {}'.format(len(snapshotData))
    # two fields in result: ts and value
    assert len(snapshotData[0]['fields']) == 2 , 'invalid snapshot data fields length wanted 2 but is {}'.format(len(snapshotData))

    # check data length
    # length = content['data']['result'][0]['values']
    assert len(content['data']['result'][0]['values']) == len(snapshotData[0]['fields'][0]['values']), 'invalid snapshot data ts length'
    # mock_data = mocker.patch("grafana_snapshots.")