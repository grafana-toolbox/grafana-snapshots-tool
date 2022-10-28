from distutils.version import LooseVersion

from grafana_snapshots.dataresults.dataresults import dataresults

datasource_type = 'loki'
api_version = LooseVersion('9.2.1')

#***************************************************************************************
#***************************************************************************************
# TIMESERIES QUERIES
#***************************************************************************************
#***************************************************************************************
def test_data_ts_range_panel_ts(build_config):
    # read the datasource
    content = build_config.readResponse('queries/grafana_9/loki/timeseries_range_5m.json')
    format = "time_series"
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
    assert len(snapshotData) == 1 , 'invalid snapshot data length wanted 2 but is {}'.format(len(snapshotData))
    # two fields in result: ts and value
    assert len(snapshotData[0]['fields']) == 2 , 'invalid snapshot data fields length wanted 2 but is {}'.format(len(snapshotData))

    # check data length
    # length = content['data']['result'][0]['values']
    assert len(snapshotData[0]['fields'][0]['values']) \
        == len(content['results']['A']['frames'][0]['data']['values'][0]), \
        'invalid snapshot data ts length'
