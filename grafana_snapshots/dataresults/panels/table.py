#!/usr/bin/python3
# -*- coding: utf-8 -*-

from grafana_snapshots.dataresults.panels.default import DefaultPanel

#***************************************************
class TablePanel(DefaultPanel):
    """
    """
    #***********************************************
    def __init__( *args, **kwargs ) -> None:

        self = args[0]
        DefaultPanel.__init__(self, **kwargs)

        self.ts_fields.extend( [
            { 'name': 'color', 'type': 'copy_all', 'value': 'defaults.color', },
            { 'name': 'custom', 'type': 'copy', 'value': 'defaults.custom', 'exclude': [ 'axisLabel', 'scaleDistribution', 'spanNulls', 'stacking'], },
            { 'name': 'links', 'type': 'copy_all', 'value': 'defaults.links', },
            { 'name': 'thresholds', 'type': 'copy_all', 'value': 'defaults.thresholds', },
            { 'name': 'unit', 'type': 'copy_all', 'value': 'defaults.unit', },
            { 'name': 'noValue', 'type': 'copy_all', 'value': 'defaults.noValue', },
        ] )

        self.value_fields.extend( [
            { 'name': 'color', 'type': 'copy_all', 'value': 'defaults.color', },
            { 'name': 'custom', 'type': 'copy_all', 'value': 'defaults.custom', },
            { 'name': 'decimals', 'type': 'copy_all', 'value': 'defaults.decimals', },
            { 'name': 'displayName', 'type': 'copy_all', 'value': 'defaults.displayName', },
            { 'name': 'links', 'type': 'copy_all', 'value': 'defaults.links', },
            { 'name': 'mappings', 'type': 'copy_all', 'value': 'defaults.mappings', },
            { 'name': 'max', 'type': 'copy_all', 'value': 'defaults.max', },
            { 'name': 'min', 'type': 'copy_all', 'value': 'defaults.min', },
            { 'name': 'noValue', 'type': 'copy_all', 'value': 'defaults.noValue', },
            { 'name': 'thresholds', 'type': 'copy_all', 'value': 'defaults.thresholds', },
            { 'name': 'unit', 'type': 'copy_all', 'value': 'defaults.unit', },
        ] )

    #***********************************************
    # def get_FieldsConfig(*args, **kwargs) -> list:
    #     self = args[0]
    #     results = args[1]

    #     fields = kwargs.get('fields', [] )
    #     res = []
    #     for field in fields:
    #         if 'type' in field and field['type'] == 'timestamp':
    #             config = self.get_FieldConfig(self.ts_fields, results)
    #         else:
    #             config = self.get_FieldConfig(self.value_fields, results)
    #         if 'config' in field['value']:
    #             field['value']['config'].update( config )
    #         else:
    #             field['value']['config'] = config
    #         res.append(field['value'])

    #     if len(res) == 0:
    #         res = [
    #             { 'config': self.get_FieldConfig(self.ts_fields, results) },
    #             { 'config': self.get_FieldConfig(self.value_fields, results) },
    #         ]

    #     return res

    #***********************************************
    def set_transformations(self, snapshotDataElmt: dict) -> None:
        """
        a transformation is an object that modify fields from the result
    	[
	        {'id': 'filterFieldsByName', 
		        'options': {'include': {'names': ['ifAlias', 'ifDescr', 'ifName', 'Value']}}}
        	{'id': 'merge', 'options': {}}
	        {'id': 'organize', 'options': {'excludeByName': {}, 'indexByName': {'Value #A': 4, 'Value #B': 5, 'Value #C': 6, 'ifAlias': 0, 'ifDescr': 1, 'ifName': 2, 'ifType': 3}, 'renameByName': {'Value': '', 'Value #C': 'MTU'}}}
	    ]
        """
        if snapshotDataElmt is None or \
            (snapshotDataElmt is not None and 'fields' not in snapshotDataElmt):
            return

        if 'fieldConfig' not in self.panel \
            or ( 'fieldConfig' in self.panel and 'transformations' not in self.panel['fieldConfig']):
            return

        for trans in self.panel['fieldConfig']['transformations']:
            pass


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

#***************************************************
