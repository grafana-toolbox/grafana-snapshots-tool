#!/usr/local/bin/pytest
# -*- coding: utf-8 -*-

import json, os, pytest, re

from grafana_snapshots.grafanaData import GrafanaData

#******************************************************************************************
class ConfigReader(object):
    panel_fields = [
        'datasource',
        'fieldConfig',
        'options',
        'targets',
        'type',
    ]
    #***********************************************
    def __init__(self, **kwargs) -> None:
        self.response = {}
        self.targets = []
        self.panel = {}
        self.datasources = {}
        self.base_path = kwargs.get('base', None)

    #***********************************************
    def _readFile(self, filepath: str) -> dict:
        result = None
        if not re.match(r'^\.?/', filepath):
            filepath = os.path.join(self.base_path, filepath)

        try:
            with open(filepath, 'r') as file_fh:
                try:
                    result = json.load(file_fh)
                except Exception as exp:
                    raise
        except Exception as exp:
            raise

        return result

    #***********************************************
    def readResponse(self, filepath: str) -> dict:
        response = self._readFile(filepath)
        if response is not None:
            if 'response' in response:
                self.response = response['response']
                self.response_name = filepath
            if 'targets' in response:
                self.targets = response['targets']

        return self.response

    #***********************************************
    def readPanel(self, filepath: str) -> dict:
        panel = self._readFile(filepath)
        if panel is not None:
            for field in ConfigReader.panel_fields:
                if field not in panel:
                    raise Exception("field '{}' not found in panel definition".format(field))

            self.panel = panel
            self.panel_name = filepath
        return self.panel

    #***********************************************
    def readDatasources(self, filepath: str) -> dict:
        datasources = self._readFile(filepath)
        if datasources is not None:
            self.datasources = datasources
        return self.datasources

    #***********************************************
    def buildGrafanaData(self, context: dict) -> GrafanaData:

        datasources = self.readDatasources('datasources.json')

        data_api = GrafanaData(
            api= dict(),
            datasources=datasources,
            context= context,
            time_from = 'now-5m',
        )
        if data_api is not None:
            self.data_api = data_api
        return data_api

    #***********************************************
    def getRequest(self, panel: dict) -> str:

        if not hasattr(self, 'data_api'):
            return None

        request = None
        dtsrc = 'default'
        target = None
        if 'datasource' in panel and panel['datasource'] is not None:
            dtsrc = panel['datasource']
            if isinstance(dtsrc, dict) and 'uid' in dtsrc and dtsrc['uid'] == '-- Mixed --':
                dtsrc = '-- Mixed --'

            if 'targets' in panel and panel['targets'] is not None:
                targets = panel['targets']
            else:
                #** row panel... probably
                targets = None
                raise "invali panel"

            datasource = self.data_api.get_datasource(dtsrc)
            if (datasource is not None or dtsrc == '-- Mixed --' ) and targets is not None:

                for target in targets:
                    # don't collect data for disabled queries
                    if 'hide' in target and target['hide']:
                        continue

                    if dtsrc == '-- Mixed --' and 'datasource' in target:
                        datasource = self.data_api.get_datasource(target['datasource'])

                    if not datasource:
                        continue

                    request = self.data_api.get_query_from_datasource(datasource, target)
                    break

        return request

#******************************************************************************************

@pytest.fixture
def build_config():
    config = ConfigReader(base='test/conf')
    return config

#******************************************************************************************