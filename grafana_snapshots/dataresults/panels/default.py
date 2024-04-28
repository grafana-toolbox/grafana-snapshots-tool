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
    def get_FieldConfig( self, fields: dict, results: dict ) -> list:
        config_elmt = {} 
        for field in fields:

            # add new attributes
            if field['type'] == 'static':
                config_elmt[field['name']] = field['value']

            # copy attributes without conditions
            elif field['type'] == 'copy_all':
                fieldConfig = self._get_target_attributes( field['value'] )
                if fieldConfig is not None:
                    config_elmt[field['name']] = copy.deepcopy(fieldConfig)

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
        format = kwargs.get("format", "timeseries")

        if format == "timeseries":
            return [
                { 'config': self.get_FieldConfig(self.ts_fields, results) },
                { 'config': self.get_FieldConfig(self.value_fields, results) },
            ]
        elif format == "table":
            fields = kwargs.get("fields", None)
            res_fields = []
            for field in fields:
                new_field = field["value"]
                if field["type"] == "timestamp":
                    new_field["config"] = self.get_FieldConfig(self.ts_fields, results)
                elif field["type"] == "value":
                    new_field["config"] = self.get_FieldConfig(self.value_fields, results)
                res_fields.append( new_field )

            return res_fields
        else:
            return []

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
                target[attr] = value
            else:
                # check if we can climb the tree (attribute exists)
                if attr not in target:
                    target = None
                    break
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

    #***********************************************
    def set_transformations(self, snapshotData: list) -> list:
        """
        a transformation is an object that modify fields from the results data
    	[
        ### Select Fields to display
	        {'id': 'filterFieldsByName', 
		        'options': {'include': {
                    'names': 
                        ['ifAlias', 'ifDescr', 'ifName', 'Value']
                    }
                }
                or
                "options": {
                    "include": {
                    "pattern": "/age/"
                }
            }
        ### merge series
        	{'id': 'merge', 'options': {}}
        ### order and rename fields
	        {'id': 'organize', 
                'options': {
                    'excludeByName': {},
                    'indexByName': {
                        'Value #A': 4,
                        'Value #B': 5,
                        'Value #C': 6,
                        'ifAlias': 0, 'ifDescr': 1, 'ifName': 2, 'ifType': 3
                    },
                    'renameByName': {
                        'Value': '', 
                        'Value #C': 'MTU'
                    }
                }
            }
        ### merge series on a field, 
          inner: keep only lines with egals values
          outer: keep all lines with empty value for line that do not match
            { "id": "joinByField",
                "options": {
                    "byField": "CountryCode",
                    "mode": "inner" | "outer"
                }
            }
        ### sort by field (only one)
            { "id": "sortBy",
                "options": {
                    "fields": {},
                    "sort": [
                        {
                            "field": "Language",
                            "desc": true | false,
                        }
                    ]
                }
            }
	    ]
        """
        if snapshotData is None or \
            (snapshotData is not None and not isinstance(snapshotData, list)):
            return snapshotData

        if 'transformations' not in self.panel:
            return snapshotData

        for trans in self.panel['transformations']:

            #*******************************
            if trans['id'] == 'filterFieldsByName':
                for snapshotDataElmt in snapshotData:
                    refId = snapshotDataElmt['refId']
                    new_fields = []

                    for idx,field in enumerate(snapshotDataElmt['fields']):
                        name = field['name']

                        #* check the names' list of the transformation
                        if 'names' in trans['options']['include']:
                            ref_name = name + ' #' + refId
                            if name in trans['options']['include']['names'] \
                                or  ref_name in trans['options']['include']['names']:
                                # name present in list : add field into new_list list
                                new_fields.append(field)

                        #* check the pattern matching of the transformation
                        elif 'pattern' in trans['options']['include']:
                            pattern = trans['options']['include']['pattern'].replace('/', '')
                            if re.search(pattern, name):
                                # name matches the pattern : add field into new_list list
                                new_fields.append(field)
                    #* substitute the original list with the new one
                    snapshotDataElmt['fields'] = new_fields
    
            #*******************************
            elif trans['id'] == 'merge':
                #** we receive a list of snapshotDataObj: have to merge fields with same name
                #**   into a sigle snapshotDataObj containing all fields.
                # the list must contain at least 2 elements to merge something
                if len(snapshotData) < 2:
                    return snapshotData

                #** we will merge all contents in the first snapshotDataObj
                snapshot = snapshotData[0] 
                del snapshotData[0]

                #** build a dict on fields name
                fields_names = {}
                for field in snapshot['fields']:
                    name = field['name']
                    if name == 'Value':
                        name += ' #' + snapshot['refId']
                        field['name'] = name
                        field['config']['displayName'] = name
                    fields_names[name] = 1
                #** now loop on field to determine those that are not currently in the list
                for snapshotDataObj in snapshotData:
                    for field in snapshotDataObj['fields']:
                        name = field['name']
                        if name == 'Value':
                            name += ' #' + snapshotDataObj['refId']
                            field['name'] = name
                            field['config']['displayName'] = name
                        #** if field name not found in the existing fields: add it.
                        if name not in fields_names:
                            #** add in known fields list
                            fields_names[name] = 1
                            #** add in snapshot fields
                            snapshot['fields'].append(field)
                #** remove all snapshots: subsistute with snapshot
                del snapshot['refId']
                snapshotData = [ snapshot ]

            #*******************************
            elif trans['id'] == 'organize':
                #** get columns ordered
                if 'indexByName' in trans['options']:
                    sorted_cols = sorted(trans['options']['indexByName']
                        , key=trans['options']['indexByName'].get)

                #** only sort if some colunm names are provided
                if len(sorted_cols) > 0:
                    for snapshotDataElmt in snapshotData:
                        new_fields = []
                        for col_name in sorted_cols:
                            for field in snapshotDataElmt['fields']:
                                if field['name'] == col_name:
                                    new_fields.append(field)
                                    break
                        #* substitute the original list with the new one
                        snapshotDataElmt['fields'] = new_fields

                #** get columns rename
                if 'renameByName' in trans['options']:
                    for cur_name in trans['options']['renameByName'].keys():
                        new_name = trans['options']['renameByName'][cur_name]
                        if new_name == '':
                            continue
                        for snapshotDataElmt in snapshotData:
                            for field in snapshotDataElmt['fields']:
                                # we have found the field: add new nane
                                if field['name'] == cur_name:
                                    if 'config' not in field:
                                        field['config'] = {
                                            'displayName': new_name,
                                        }
                                    else:
                                        field['config']['displayName'] = new_name
                                    break
    
            #*******************************
            elif trans['id'] == 'sortBy':

                #* get the name to sort on
                reverse_order = False
                if 'sort' in trans['options'] and len(trans['options']['sort']) > 0\
                    and 'field' in trans['options']['sort'][0]:
                    sort_name = trans['options']['sort'][0]['field']
                    if 'desc' in trans['options']['sort'][0]:
                        reverse_order = trans['options']['sort'][0]['desc']
                if sort_name is None:
                    return snapshotData

                # have to find the column to sort in each snapshotData element
                # column name may be present in several snapshot elements (without a merge transformation by example)
                for snapshotDataElmt in snapshotData:
                    unordered_field = {}
                    for field in snapshotDataElmt['fields']:
                        # we have found the field: add new nane
                        if field['name'] == sort_name:
                            for idx, val in enumerate(field['values']):
                                unordered_field[val] = idx
                            break

                    # we have a column to sort, proceed
                    if len(unordered_field) >0:
                        # sort the column value, with idx as value
                        ordered_field = dict(sorted(unordered_field.items(), reverse=reverse_order))
                        # now sort each field with previously defined order
                        for field in snapshotDataElmt['fields']:
                            ordered_values = []
                            for idx in ordered_field.values():
                                if idx < len(field['values']):
                                    ordered_values.append(field['values'][idx])
                                else:
                                    ordered_values.append(None)
                            field['values'] = ordered_values

            else:
                raise NotImplementedError('transformation not implemented')

        return snapshotData


# def check_transformations( *args ):
#    """
#     transformation format is:
# 	[
# 	{'id': 'filterFieldsByName', 
# 		'options': {'include': {'names': ['ifAlias', 'ifDescr', 'ifName', 'Value']}}}
# 	{'id': 'merge', 'options': {}}
# 	{'id': 'organize', 'options': {'excludeByName': {}, 'indexByName': {'Value #A': 4, 'Value #B': 5, 'Value #C': 6, 'ifAlias': 0, 'ifDescr': 1, 'ifName': 2, 'ifType': 3}, 'renameByName': {'Value': '', 'Value #C': 'MTU'}}}
# 	]
#    """
#    res = { 'status': False }

#    params = args[0]
#    action = params.get('action', 'pre')
#    transformations = params.get('transformations')
#    if transformations is None:
#       return None

#    name = None
#    refId = None
#    snapshotData = None
   
#    if action == 'pre':
#       name = params.get('name')
#       refId = params.get('refId')
#       if name is None or refId is None:
#          return res
#    else:
#       snapshotData = params.get('snapshotData')
#       if snapshotData is None:
#          return res

#    filter_found = False
#    for trans in transformations:
#       if action == 'pre':
#          if trans['id'] == 'filterFieldsByName':
#             filter_found = True
#             if 'include' in trans['options']:
#                ref_name = name + ' #' + refId
#                if name in trans['options']['include']['names'] \
# 			            or ref_name in trans['options']['include']['names']:
#                   res['status'] = True
#                   break
#       elif action == 'post':
#          if trans['id'] == 'merge':
#             #** we receive a list of snapshotDataObj: have to merge fields with same name
#             #**   into a sigle snapshotDataObj containing all fields.
#             # the list must contain at least 2 elements to merge something
#             if len(snapshotData) < 2:
#                res['status'] = True
#                res['snapshotData'] = snapshotData
#             else:
#                #** we will merge all contents in the first snapshotDataObj
#                snapshot = snapshotData[0] 
#                del snapshotData[0]
#                #** build a dict on fields name
#                field_names = {}
#                for field in snapshot['fields']:
#                   name = field['name']
#                   if name == 'Value':
#                      name += ' #' + snapshot['refId']
#                      field['name'] = name
#                      field['config']['displayName'] = name
#                   field_names[name] = 1
#                #** now loop on field to determine those that are not currently in the list
#                for snapshotDataObj in snapshotData:
#                   for field in snapshotDataObj['fields']:
#                      name = field['name']
#                      if name == 'Value':
#                         name += ' #' + snapshotDataObj['refId']
#                         field['name'] = name
#                         field['config']['displayName'] = name
#                      #** if field name not found in the existing fields: add it.
#                      if name not in field_names:
#                         #** add in known fields list
#                         field_names[name] = 1
#                         #** add in snapshot fields
#                         snapshot['fields'].append(field)
#                #** remove all snapshots: subsistute with snapshot
#                del snapshot['refId']
#                snapshotData = [ snapshot ]
#                res['status'] = True
#                res['snapshotData'] = snapshotData

#          elif trans['id'] == 'organize':
#             #** only consider the first element of snapshotData
#             snapshot = snapshotData[0]

#             #** get columns ordered
#             if 'indexByName' in trans['options']:
#                sorted_cols = sorted(trans['options']['indexByName']
#          			, key=trans['options']['indexByName'].get)

#                #** only sort if some colunm names are provided
#                if len(sorted_cols) > 0:
#                   fields = []
#                   for col_name in sorted_cols:
#                      f_found = False
#                      for field in snapshot['fields']:
#                         if field['name'] == col_name:
#                            fields.append(field)
#                            f_found = True
#                            break;
#                      if not f_found:
#                         print( "field '{}' not found!".format(col_name) )
#                   #** subsitute new fields list in snapshot
#                   snapshot['fields'] = fields;

#             #** get columns rename
#             if 'renameByName' in trans['options']:
#                for cur_name in trans['options']['renameByName'].keys():
#                   new_name = trans['options']['renameByName'][cur_name]
#                   if new_name == '':
#                      continue
#                   for field in snapshot['fields']:
#                      name = field['name']
#                      if name == cur_name:
#                         if 'config' not in field:
#                            field['config']={
#                               'custom': {},
#                               'displayName': new_name,
#                               'filterable': True,
#                               'mappings': []
#                            }
#                         else:
#                            field['config']['displayName']=new_name
#                res['status'] = True

#             res['status'] = True
#             res['snapshotData'] = snapshotData

#    #** if not filter defined: keep the field
#    if action == 'pre' and not filter_found:
#       res['status'] = True
#       return res

#    return res

#**********************************************************************************