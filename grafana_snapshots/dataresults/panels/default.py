#!/usr/bin/python3
# -*- coding: utf-8 -*-
#**********************************************************************************

import copy, re

#**********************************************************************************
class DefaultPanel:
    #***********************************************
    def __init__( *args, **kwargs ) -> None:

        self = args[0]
        self.panel = kwargs.get('panel')
        self.ts_fields = [
        ]

        self.value_fields = [
        ]

    #***********************************************
    def _get_target_attributes(self, attributes: str) -> dict:
        target = {}
        (attrs) = attributes.split('.')
        if not 'fieldConfig' in self.panel:
            return target
        target = self.panel['fieldConfig']
        for attr in attrs:
            if attr not in target:
                target = None
                break
            target = target[attr]
        return target

    #***********************************************
    def get_FieldConfig( self, fields: dict, results: dict, ) -> list:
        config_elmt = {} 
        for field in fields:

            # add new attributes
            if field['type'] == 'static':
                config_elmt[field['name']] = field['value']

            # copy attributes without conditions
            elif field['type'] == 'copy_all':
                fieldConfig = self._get_target_attributes( field['value'] )
                if fieldConfig is not None:
                    config_elmt[field['name']] = fieldConfig

            # copy attributes with conditions
            elif field['type'] == 'copy':
                fieldConfig = self._get_target_attributes( field['value'] )
                if fieldConfig is not None:
                    # build empty attributes
                    config_elmt[field['name']] = {}
                    # check for all attributes if are included or excluded

                    for key in fieldConfig.keys():
                        if 'exclude' in field and key in field['exclude']:
                            continue
                        if 'include' not in field or \
                            ( 'include' in field and key in field['include']):
                            config_elmt[field['name']][key] = copy.deepcopy(fieldConfig[key])

                # if field['value'] == 'defaults':
                #     if 'defaults' in fieldConfig and fieldConfig['defaults'] is not None \
                #         and field['name'] in fieldConfig['defaults']:
                #         config_elmt[field['name']] = fieldConfig['defaults'][field['name']]
                # elif field['value'] == 'defaults.custom':
                #     if 'defaults' in fieldConfig and fieldConfig['defaults'] is not None \
                #         and 'custom' in fieldConfig['defaults'] \
                #         and field['name'] in fieldConfig['defaults']['custom']:
                #         config_elmt[field['name']] = fieldConfig['defaults']['custom'][field['name']]
        return config_elmt

    #***********************************************
    def get_FieldsConfig(*args, **kwargs) -> list:
        self = args[0]
        results = args[1]

        return [
            { 'config': self.get_FieldConfig(self.ts_fields, results) },
            { 'config': self.get_FieldConfig(self.value_fields, results) },
        ]

    #***********************************************
    def _set_target_attributes(self, attributes: str, value: any, source: dict=None) -> None:
        target = None
        (attrs) = attributes.split('.')
        if source is None:
            return
        target = source
        for idx in range(0, len(attrs)):
            attr = attrs[idx]
            if attr not in target:
                target = None
                break
            if idx == len(attrs) -1:
                target[attr] = copy.deepcopy(value)
            else:
                target = target[attr]
        return

    #***********************************************
    def _check_matcher(self, matcher: dict, field: dict, refId: str) -> bool:
        """
        Matcher has two attributes (id, options)
        id: test to perform
           - byName; options contains exact column name
           - byRegexp; options contains regexp to check
           - byType; options contains type of columns : label: "string", timestamp: "time", value: "number", ?: "boolean"
           - byFrameRefID; options contains the refId name ; if column name is comming from refId the check is true

        options: value to check
        """
        res = False
        if matcher['id'] == 'byName':
            if 'name' in field and field['name'] == matcher['options']:
                res = True
        elif matcher['id'] == 'byType':
            if 'type' in field and field['type'] == matcher['options']:
                res = True
        elif matcher['id'] == 'byRegexp' and 'name' in field:
            if re.match(matcher['options'], field['name']):
                res = True
        elif matcher['id'] == 'byFrameRefID' and refId is not None \
            and refId == matcher['options']:
            res = True

        return res

    #***********************************************
    def set_overrides(self, snapshotDataElmt: dict) -> None:
        """
        an override is an object that selects fields from results and updates theirs properties

        {
            "matcher": {
                "id": "byName",
                "options": "Time"
            },
            "properties": [
                {
                    "id": "custom.width",
                    "value": 210
                }
            ]
        },
        {
            "matcher": {
                "id": "byType",
                "options": "time"
            },
            "properties": [
                {
                    "id": "custom.filterable",
                    "value": true
                }
            ]
        }
        """
        if snapshotDataElmt is None or \
            (snapshotDataElmt is not None and 'fields' not in snapshotDataElmt):
            return

        if 'fieldConfig' not in self.panel \
            or ( 'fieldConfig' in self.panel and 'overrides' not in self.panel['fieldConfig']):
            return

        refId = snapshotDataElmt.get('refId', None)

        for override in self.panel['fieldConfig']['overrides']:
            if 'matcher' in override and override['matcher']:
            #  byName; options contains exact column name
            #  byRegexp; options contains regexp to check
            #  byType; options contains type of columns : label: "string", timestamp: "time", value: "number", ?: "boolean"
                for field in snapshotDataElmt['fields']:
                    if self._check_matcher(override['matcher'], field, refId):
                        for property in override['properties']:
                            self._set_target_attributes(property['id'], property['value'], source=field['config'])

#**********************************************************************************
