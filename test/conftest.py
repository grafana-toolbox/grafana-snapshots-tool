#!/usr/local/bin/pytest
# -*- coding: utf-8 -*-

import json, os, pytest, re

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
        self.panel = {}
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
        if response is not None and 'response' in response:
            self.response = response['response']
            self.response_name = filepath
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

#******************************************************************************************

@pytest.fixture
def build_config():
    config = ConfigReader(base='test/conf')
    return config

#******************************************************************************************