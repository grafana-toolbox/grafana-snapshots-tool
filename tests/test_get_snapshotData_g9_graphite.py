from verlib2 import Version

from grafana_snapshots.dataresults.dataresults import dataresults

datasource_type = 'graphite'
api_version = Version('9.2.1')

#***************************************************************************************
#***************************************************************************************
# TIMESERIES QUERIES
#***************************************************************************************
#***************************************************************************************
def test_data_ts_range_panel_ts(build_config):
    # read the datasource
    content = build_config.readResponse('queries/grafana_9/graphite/data_range_5m.json')
    format = None
    # read the panel
    panel = build_config.readPanel('panels/grafana_9/two_timeseries.json')
    targets = build_config.targets
    if len(targets) == 0:
        targets = panel['targets']

    dataRes = dataresults( 
        type=datasource_type,
        format=format,
        results=content,
        version=api_version,
        panel=panel)
    snapshotData = dataRes.get_snapshotData(targets)

    assert snapshotData is not None, "invalid data"
    # two ts results
    assert len(snapshotData) == 2 , 'invalid snapshot data length wanted 2 but is {}'.format(len(snapshotData))
    # two fields in result: ts and value
    assert len(snapshotData[0]['fields']) == 2 , 'invalid snapshot data fields length wanted 2 but is {}'.format(len(snapshotData))

    # check data length
    # length = content['data']['result'][0]['values']
    assert len(snapshotData[0]['fields'][0]['values']) == len(content[0]['datapoints']), 'invalid snapshot data ts length'
    assert len(snapshotData[1]['fields'][0]['values']) == len(content[1]['datapoints']) == len(snapshotData[1]['fields'][0]['values']), 'invalid snapshot data value length'
