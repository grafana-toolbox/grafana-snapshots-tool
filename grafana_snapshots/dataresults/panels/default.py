#!/usr/bin/python3
# -*- coding: utf-8 -*-

#***************************************************
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
                            config_elmt[field['name']][key] = fieldConfig[key]

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

#***************************************************