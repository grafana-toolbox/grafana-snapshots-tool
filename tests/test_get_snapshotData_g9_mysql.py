from verlib2 import Version

from grafana_snapshots.dataresults.dataresults import dataresults

datasource_type = 'mysql'
api_version = Version('9.2.1')

#***************************************************************************************
#***************************************************************************************
# TIMESERIES QUERIES
#***************************************************************************************
#***************************************************************************************
def test_data_table_range_panel_table_filter_pattern(build_config):
    # read the datasource
    content = build_config.readResponse('queries/grafana_9/mysql/table_timeless_transf_filter.json')
    format = "table"
    # read the panel
    panel = build_config.readPanel('panels/grafana_9/mysql_table_transformation.json')
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
    # one serie
    assert len(snapshotData) == 1 ,\
        'invalid snapshot data length wanted 1 but is {}'.format(len(snapshotData))
    # one field in result: "IsOfficial" match pattern /al/
    assert len(snapshotData[0]['fields']) == 1 , \
     'invalid snapshot data fields length wanted 1 but is {}'.format(len(snapshotData[0]['fields']))

    # check data length
    # length = content['data']['result'][0]['values']
    assert len(snapshotData[0]['fields'][0]['values']) \
        == len(content['results']['A']['frames'][0]['data']['values'][0]), \
        'invalid snapshot data ts length'

#***************************************************************************************
def test_data_table_range_panel_table_filter_column(build_config):
    # read the datasource
    content = build_config.readResponse('queries/grafana_9/mysql/table_timeless_transf_filter.json')
    format = "table"
    # read the panel
    panel = build_config.readPanel('panels/grafana_9/mysql_table_transformation.json')

    # set specific transformation
    panel["transformations"]= [ {
            "id": "filterFieldsByName",
            "options": {
                "include": {
                    "names": [
                        "Language",
                        "CountryCode",
                        "Percentage"
                    ]
                }
            }
        } ]
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
    # one serie
    assert len(snapshotData) == 1 ,\
        'invalid snapshot data length wanted 1 but is {}'.format(len(snapshotData))
    # three fields in result: those filtered by name
    assert len(snapshotData[0]['fields']) == 3 ,\
        'invalid snapshot data fields length wanted 3 but is {}'.format(len(snapshotData[0]['fields']))

    # check data length
    # length = content['data']['result'][0]['values']
    assert len(snapshotData[0]['fields'][0]['values']) \
        == len(content['results']['A']['frames'][0]['data']['values'][0]), \
        'invalid snapshot data ts length'

#***************************************************************************************
def test_data_table_range_panel_table_organize_column(build_config):
    # read the datasource
    content = build_config.readResponse('queries/grafana_9/mysql/table_timeless_transf_filter.json')
    format = "table"
    # read the panel
    panel = build_config.readPanel('panels/grafana_9/mysql_table_transformation.json')

    # set specific transformation
    panel["transformations"]= [ {
        "id": "organize",
        "options": {
            "excludeByName": {},
            "indexByName": {
                "CountryCode": 1,
                "Language": 2,
                "Percentage": 0
            },
            "renameByName": {
                "Percentage": "%"
            }
        }
    } ]
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
    # one serie
    assert len(snapshotData) == 1 ,\
        'invalid snapshot data length wanted 1 but is {}'.format(len(snapshotData))
    # three fields in result: those filtered by name
    assert len(snapshotData[0]['fields']) == 3 ,\
        'invalid snapshot data fields length wanted 3 but is {}'.format(len(snapshotData[0]['fields']))

    # check data length
    # check rename and order col 1
    config = snapshotData[0]['fields'][0]
    assert config['config']['displayName'] == '%',\
         'invalid data name column 0'
    assert len(snapshotData[0]['fields'][0]['values']) \
        == len(content['results']['A']['frames'][0]['data']['values'][0]), \
        'invalid snapshot data ts length'
    # check rename and order col 2
    config = snapshotData[0]['fields'][2]
    assert config['name'] == 'Language',\
        'invalid data name column 0'

#***************************************************************************************
def test_data_table_2queries_panel_table_raw(build_config):
    # read the datasource
    content = build_config.readResponse('queries/grafana_9/mysql/table_timeless_2_queries_raw.json')
    format = "table"
    # read the panel
    panel = build_config.readPanel('panels/grafana_9/mysql_table_transformation.json')
    # set no specific transformation
    panel["transformations"]= [ ]

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
    # 2 queries : two series
    assert len(snapshotData) == 2 ,\
        'invalid snapshot data length wanted 2 but is {}'.format(len(snapshotData))
    # three fields in result: those filtered by name
    assert len(snapshotData[0]['fields']) == 4 ,\
        'invalid snapshot data fields length wanted 4 but is {}'.format(len(snapshotData[0]['fields']))
    assert len(snapshotData[1]['fields']) == 3 ,\
        'invalid snapshot data fields length wanted 3 but is {}'.format(len(snapshotData[1]['fields']))

#***************************************************************************************
def test_data_table_2queries_panel_table_merge(build_config):
    # read the datasource
    content = build_config.readResponse('queries/grafana_9/mysql/table_timeless_2_queries_raw.json')
    format = "table"
    # read the panel
    panel = build_config.readPanel('panels/grafana_9/mysql_table_transformation.json')
    # set no specific transformation
    panel["transformations"]= [ {
      "id": "merge",
      "options": {}
    } ]

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
    # 2 queries : two series, merge into one
    assert len(snapshotData) == 1 ,\
        'invalid snapshot data length wanted 1 but is {}'.format(len(snapshotData))
    # four fields in results of query 1; three fiels in query2: merge on 1 field
    assert len(snapshotData[0]['fields']) == 6 ,\
        'invalid snapshot data fields length wanted 6 but is {}'.format(len(snapshotData[0]['fields']))

#***************************************************************************************
def test_data_table_2queries_panel_table_merge_sort(build_config):
    # read the datasource
    content = build_config.readResponse('queries/grafana_9/mysql/table_timeless_2_queries_raw.json')
    format = "table"
    # read the panel
    panel = build_config.readPanel('panels/grafana_9/mysql_table_transformation.json')
    # set no specific transformation
    panel["transformations"]= [
        {
            "id": "merge",
            "options": {}
        },
        { "id": "sortBy",
            "options": {
                "fields": {},
                "sort": [
                    {
                        "field": "Language",
                        "desc": True,
                    }
                ]
            }
        }
    ]

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
    # 2 queries : two series, merge into one
    assert len(snapshotData) == 1 ,\
        'invalid snapshot data length wanted 1 but is {}'.format(len(snapshotData))
    # four fields in results of query 1; three fiels in query 2: merge on 1 field
    assert len(snapshotData[0]['fields']) == 6 ,\
        'invalid snapshot data fields length wanted 6 but is {}'.format(len(snapshotData[0]['fields']))
    # reverse sort on Language: first value is 'Vietnamese'
    assert snapshotData[0]['fields'][1]['values'][0] == 'Vietnamese', \
        "invalid snapshot data value wanted 'Vietnamese'  is {}".format(snapshotData[0]['fields'][1]['values'][0])

#***************************************************************************************
def test_data_table_2queries_panel_table_merge_sort_float(build_config):
    # read the datasource
    content = build_config.readResponse('queries/grafana_9/mysql/table_timeless_2_queries_raw.json')
    format = "table"
    # read the panel
    panel = build_config.readPanel('panels/grafana_9/mysql_table_transformation.json')
    # set no specific transformation
    panel["transformations"]= [
        {
            "id": "merge",
            "options": {}
        },
        { "id": "sortBy",
            "options": {
                "fields": {},
                "sort": [
                    {
                        "field": "Percentage",
                        "desc": False,
                    }
                ]
            }
        }
    ]

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
    # 2 queries : two series, merge into one
    assert len(snapshotData) == 1 ,\
        'invalid snapshot data length wanted 1 but is {}'.format(len(snapshotData))
    # four fields in results of query 1; three fiels in query 2: merge on 1 field
    assert len(snapshotData[0]['fields']) == 6 ,\
        'invalid snapshot data fields length wanted 6 but is {}'.format(len(snapshotData[0]['fields']))
    # sort on float value Percentage: first value is 0
    assert snapshotData[0]['fields'][3]['values'][0] == 0, \
        "invalid snapshot data value wanted 0.0  is {}".format(snapshotData[0]['fields'][3]['values'][0])