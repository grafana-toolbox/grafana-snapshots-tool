# import pytest
from verlib2 import Version

from grafana_snapshots.dataresults.dataresults import dataresults

datasource_type = 'prometheus'
api_version = Version('9.2.1')

#***************************************************************************************
#***************************************************************************************
# TIMESERIES QUERIES
#***************************************************************************************
#***************************************************************************************
# def test_data_ts_range_panel_ts(build_config):
#     # read the datasource
#     content = build_config.readResponse('queries/grafana_9/prometheus/two_timeseries_5m.json')
#     format = 'time_series'
#     # read the panel
#     panel = build_config.readPanel('panels/grafana_9/two_timeseries.json')
#     # build a target
#     # if 'targets' not in panel or len(panel['targets'])<2:
#     #     raise Exception("can' build target from panel")

#     dataRes = dataresults( 
#         type=datasource_type,
#         format=format,
#         results=content,
#         version=api_version,
#         panel=panel)
#     snapshotData = dataRes.get_snapshotData(build_config.targets)

#     assert snapshotData is not None, "invalid data"
#     # two ts results
#     assert len(snapshotData) == 2 , 'invalid snapshot data length wanted 2 but is {}'.format(len(snapshotData))
#     # two fields in result: ts and value
#     assert len(snapshotData[0]['fields']) == 2 , 'invalid snapshot data fields length wanted 2 but is {}'.format(len(snapshotData))

#     # check data length
#     # length = content['data']['result'][0]['values']
#     assert len(content['results']['A']['frames'][0]['data']['values'][0]) == len(snapshotData[0]['fields'][0]['values']), 'invalid snapshot data ts length'
#     assert len(content['results']['B']['frames'][0]['data']['values'][0]) == len(snapshotData[1]['fields'][0]['values']), 'invalid snapshot data value length'

#***************************************************************************************
# def test_data_ts_instant_panel_ts(build_config):
#     # read the datasource
#     content = build_config.readResponse('queries/grafana_9/prometheus/timeseries_instant.json')
#     format = 'time_series'
#     # read the panel
#     panel = build_config.readPanel('panels/grafana_9/timeseries_instant.json')

#     dataRes = dataresults( 
#         type=datasource_type,
#         format=format,
#         results=content,
#         version=api_version,
#         panel=panel)
#     snapshotData = dataRes.get_snapshotData(build_config.targets)

#     assert snapshotData is not None, "invalid data"
#     # two ts results
#     assert len(snapshotData) == 3 , 'invalid snapshot data length wanted 3 but is {}'.format(len(snapshotData))
#     # two fields in result: ts and value
#     assert len(snapshotData[0]['fields']) == 2 , 'invalid snapshot data fields length wanted 2 but is {}'.format(len(snapshotData))

#     # check data length
#     # length = content['data']['result'][0]['values']
#     assert len(content['results']['A']['frames'][0]['data']['values'][0]) == len(snapshotData[0]['fields'][0]['values']), 'invalid snapshot data ts length'

#***************************************************************************************
# def test_data_ts_range_panel_ts_overwrite(build_config):
#     # read the datasource
#     content = build_config.readResponse('queries/grafana_9/prometheus/timeseries_range.json')
#     format = 'time_series'
#     # read the panel
#     panel = build_config.readPanel('panels/grafana_9/timeseries_overwrites.json')

#     dataRes = dataresults( 
#         type=datasource_type,
#         format=format,
#         results=content,
#         version=api_version,
#         panel=panel)
#     snapshotData = dataRes.get_snapshotData(build_config.targets)

#     assert snapshotData is not None, "invalid data"
#     # one ts results
#     assert len(snapshotData) == 1 , 'invalid snapshot data length wanted 1 but is {}'.format(len(snapshotData))
#     # two fields in result: ts and value
#     assert len(snapshotData[0]['fields']) == 2 , 'invalid snapshot data fields length wanted 2 but is {}'.format(len(snapshotData))

#     # check overwrites
#     config = snapshotData[0]['fields'][1]['config']
#     assert config['displayName'] == 'test_display_name', 'invalid snapshot default display {}'.format(config['displayName'])
#     assert config['links'][0]['title'] == 'test', 'invalid snapshot default link title Name {}'.format(config['links'][0]['title'])
#     assert config['min'] == 1e-5, 'invalid snapshot default min'.format(config['min'])
#     assert config['max'] == 1e-2, 'invalid snapshot default max'.format(config['max'])
#     assert config['unit'] == 'percentunit', 'invalid snapshot default unit'.format(config['unit'])

#***************************************************************************************
def test_data_ts_range_panel_stat(build_config):
    # read the datasource
    content = build_config.readResponse('queries/grafana_10/prometheus/timeseries_range.json')
    format = 'time_series'
    # read the panel
    panel = build_config.readPanel('panels/grafana_10/stat_range_up.json')

    dataRes = dataresults( 
        type=datasource_type,
        format=format,
        results=content,
        version=api_version,
        panel=panel)
    snapshotData = dataRes.get_snapshotData(build_config.targets)

    assert snapshotData is not None, "invalid data"
    # one ts results
    assert len(snapshotData) == 4 , 'invalid snapshot data length wanted 1 but is {}'.format(len(snapshotData))
    # two fields in result: ts and value
    assert len(snapshotData[0]['fields']) == 2 , 'invalid snapshot data fields length wanted 2 but is {}'.format(len(snapshotData))

#***************************************************************************************
# def test_data_ts_range_panel_gauge(build_config):
#     # read the datasource
#     content = build_config.readResponse('queries/grafana_10/prometheus/timeseries_range.json')
#     format = 'time_series'
#     # read the panel
#     panel = build_config.readPanel('panels/grafana_9/gauge_std.json')

#     dataRes = dataresults( 
#         type=datasource_type,
#         format=format,
#         results=content,
#         version=api_version,
#         panel=panel)
#     snapshotData = dataRes.get_snapshotData(build_config.targets)

#     assert snapshotData is not None, "invalid data"
#     # one ts results
#     assert len(snapshotData) == 1 , 'invalid snapshot data length wanted 1 but is {}'.format(len(snapshotData))
#     # two fields in result: ts and value
#     assert len(snapshotData[0]['fields']) == 2 , 'invalid snapshot data fields length wanted 2 but is {}'.format(len(snapshotData))

#***************************************************************************************
# def test_data_ts_range_panel_bargauge(build_config):
#     # read the datasource
#     content = build_config.readResponse('queries/grafana_9/prometheus/timeseries_range.json')
#     format = 'time_series'
#     # read the panel
#     panel = build_config.readPanel('panels/grafana_9/bargauge_std.json')

#     dataRes = dataresults( 
#         type=datasource_type,
#         format=format,
#         results=content,
#         version=api_version,
#         panel=panel)
#     snapshotData = dataRes.get_snapshotData(build_config.targets)

#     assert snapshotData is not None, "invalid data"
#     # one ts results
#     assert len(snapshotData) == 1 , 'invalid snapshot data length wanted 1 but is {}'.format(len(snapshotData))
#     # two fields in result: ts and value
#     assert len(snapshotData[0]['fields']) == 2 , 'invalid snapshot data fields length wanted 2 but is {}'.format(len(snapshotData))

#     # check default field value
#     config = snapshotData[0]['fields'][1]['config']
#     assert config['min'] == 0, 'invalid snapshot default min'.format(config['min'])
#     assert config['max'] == 100, 'invalid snapshot default max'.format(config['max'])
#     assert config['unit'] == 'percent', 'invalid snapshot default unit'.format(config['unit'])

#***************************************************************************************
# def test_data_ts_range_panel_piechart(build_config):
#     # read the datasource
#     content = build_config.readResponse('queries/grafana_9/prometheus/timeseries_range.json')
#     format = 'time_series'
#     # read the panel
#     panel = build_config.readPanel('panels/grafana_9/piechart.json')

#     dataRes = dataresults( 
#         type=datasource_type,
#         format=format,
#         results=content,
#         version=api_version,
#         panel=panel)
#     snapshotData = dataRes.get_snapshotData(build_config.targets)

#     assert snapshotData is not None, "invalid data"
#     # one ts results
#     assert len(snapshotData) == 1 , 'invalid snapshot data length wanted 1 but is {}'.format(len(snapshotData))
#     # two fields in result: ts and value
#     assert len(snapshotData[0]['fields']) == 2 , 'invalid snapshot data fields length wanted 2 but is {}'.format(len(snapshotData))

#     # check default field value
#     config = snapshotData[0]['fields'][1]['config']
#     assert config['min'] == 0, 'invalid snapshot default min'.format(config['min'])
#     assert config['max'] == 100, 'invalid snapshot default max'.format(config['max'])
#     assert config['unit'] == 'none', 'invalid snapshot default unit'.format(config['unit'])

#***************************************************************************************
#***************************************************************************************
# TABLE QUERIES
#***************************************************************************************
#***************************************************************************************
# def test_data_table_instant_panel_table(build_config):
#     # read the datasource
#     content = build_config.readResponse('queries/grafana_9/prometheus/table_instant.json')
#     format = 'table'
#     # read the panel
#     panel = build_config.readPanel('panels/grafana_9/table_overwrite.json')

#     dataRes = dataresults( 
#         type=datasource_type,
#         format=format,
#         results=content,
#         version=api_version,
#         panel=panel)
#     snapshotData = dataRes.get_snapshotData(build_config.targets)

#     assert snapshotData is not None, "invalid data"
#     # one results
#     assert len(snapshotData) == 1 , 'invalid snapshot data length wanted 2 but is {}'.format(len(snapshotData))
#     # 6 fields in result: ts and value and 4 labels
#     assert len(snapshotData[0]['fields']) == 6 , 'invalid snapshot data fields length wanted 2 but is {}'.format(len(snapshotData))

#     # check data length
#     # length = content['data']['result'][0]['values']
#     # assert len(snapshotData[0]['fields'][0]['values']) == len(content['results']['A']['frames']), 'invalid snapshot data ts length'
#     assert len(snapshotData[0]['fields'][0]['values']) == len(content['results']['A']['frames']) * len(content['results']['A']['frames'][0]['data']['values'][0]), 'invalid snapshot data ts length'

#     # check overwrites
#     # ts column width set to 210
#     config = snapshotData[0]['fields'][0]['config']
#     assert config['custom']['width'] == 210, 'invalid snapshot ts colunm width'
#     # code column width set to 123, displayMode 'gradient...
#     config = snapshotData[0]['fields'][1]['config']
#     assert config['custom']['width'] == 123, 'invalid snapshot code colunm width'
#     assert config['custom']['displayMode'] == 'gradient-gauge', 'invalid snapshot code displayMode'
#     assert config['min'] == 100, 'invalid snapshot code min'
#     assert config['max'] == 500, 'invalid snapshot code max'
#     assert config['thresholds']['steps'][2]['value'] == 500, 'invalid snapshot threshold max'
#     # check default field value
#     config = snapshotData[0]['fields'][4]['config']
#     assert config['custom']['width'] == 123, 'invalid snapshot default colunm width'
#     assert config['custom']['align'] == 'center', 'invalid snapshot default colunm alignment'
#     assert config['min'] == -1, 'invalid snapshot default colunm min'

#***************************************************************************************
# def test_data_table_range_panel_table(build_config):
#     # read the datasource
#     content = build_config.readResponse('queries/grafana_9/prometheus/table_range_2m.json')
#     format = 'table'
#     # read the panel
#     panel = build_config.readPanel('panels/grafana_9/table_overwrite.json')
#     targets = build_config.targets
#     if len(targets) == 0:
#         targets = panel['targets']

#     dataRes = dataresults( 
#         type=datasource_type,
#         format=format,
#         results=content,
#         version=api_version,
#         panel=panel)
#     snapshotData = dataRes.get_snapshotData(targets)

#     assert snapshotData is not None, "invalid data"
#     # one results
#     assert len(snapshotData) == 1 , 'invalid snapshot data length wanted 1 but is {}'.format(len(snapshotData))
#     # 6 fields in result: ts and value and 4 labels
#     assert len(snapshotData[0]['fields']) == 6 , 'invalid snapshot data fields length wanted 2 but is {}'.format(len(snapshotData))

#     # check data length
#     # length = content['data']['result'][0]['values']
#     assert len(snapshotData[0]['fields'][0]['values']) == len(content['results']['A']['frames']) * len(content['results']['A']['frames'][0]['data']['values'][0]), 'invalid snapshot data ts length'

#     # check overwrites
#     # ts column width set to 210
#     config = snapshotData[0]['fields'][0]['config']
#     assert config['custom']['width'] == 210, 'invalid snapshot ts colunm width'
#     # code column width set to 123, displayMode 'gradient...
#     config = snapshotData[0]['fields'][1]['config']
#     assert config['custom']['width'] == 123, 'invalid snapshot code colunm width'
#     assert config['custom']['displayMode'] == 'gradient-gauge', 'invalid snapshot code displayMode'
#     assert config['min'] == 100, 'invalid snapshot code min'
#     assert config['max'] == 500, 'invalid snapshot code max'
#     assert config['thresholds']['steps'][2]['value'] == 500, 'invalid snapshot threshold max'
#     # check default field value
#     config = snapshotData[0]['fields'][4]['config']
#     assert config['custom']['width'] == 123, 'invalid snapshot default colunm width'
#     assert config['custom']['align'] == 'center', 'invalid snapshot default colunm alignment'
#     assert config['min'] == -1, 'invalid snapshot default colunm min'
    
#***************************************************************************************
# def test_data_table_range_panel_stat(build_config):
#     # read the datasource
#     content = build_config.readResponse('queries/grafana_9/prometheus/table_range_2m.json')
#     format = 'table'
#     # read the panel
#     panel = build_config.readPanel('panels/grafana_9/stat_range_specific_field.json')
#     targets = build_config.targets
#     if len(targets) == 0:
#         targets = panel['targets']

#     dataRes = dataresults( 
#         type=datasource_type,
#         format=format,
#         results=content,
#         version=api_version,
#         panel=panel)
#     snapshotData = dataRes.get_snapshotData(targets)

#     assert snapshotData is not None, "invalid data"
#     # one results
#     assert len(snapshotData) == 1 , 'invalid snapshot data length wanted 1 but is {}'.format(len(snapshotData))
#     # 6 fields in result: ts and value and 4 labels
#     assert len(snapshotData[0]['fields']) == 6 , 'invalid snapshot data fields length wanted 2 but is {}'.format(len(snapshotData))

#     # check data length
#     # length = content['data']['result'][0]['values']
#     assert len(snapshotData[0]['fields'][0]['values']) == len(content['results']['A']['frames']) * len(content['results']['A']['frames'][0]['data']['values'][0]), 'invalid snapshot data ts length'

    #***************************************************************************************