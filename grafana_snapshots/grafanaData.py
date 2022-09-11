import sys, json, re, urllib.parse
import datetime, dateutil.parser, dateutil.relativedelta
from jinja2 import Template


#**********************************************************************************
def get_time(time_str):

    now = datetime.datetime.now() 
    ts = None

    if time_str is None:
        time_str = now

    if type(time_str) is datetime.datetime:
        ts = int(time_str.timestamp())
    elif type(time_str) is int:
        # it must be an unix timestamp
        ts = time_str
    elif type(time_str) is str:
        p = re.compile(r'^now(?:-(\d+)([dhmMyw]))?$')
        m =  p.search(time_str)
        if m:
            factor = 0
            ts = now
            if m.group(1) and m.group(2):
               val = int(m.group(1))
               if m.group(2) == 'm':
                  dt = dateutil.relativedelta.relativedelta(minutes=val)
               elif m.group(2) == 'h':
                  dt = dateutil.relativedelta.relativedelta(hours=val)
               elif m.group(2) == 'd':
                  dt = dateutil.relativedelta.relativedelta(days=val)
               elif m.group(2) == 'w':
                  dt = dateutil.relativedelta.relativedelta(weeks=val)
               elif m.group(2) == 'M':
                  dt = dateutil.relativedelta.relativedelta(months=val)
               elif m.group(2) == 'y':
                  dt = dateutil.relativedelta.relativedelta(years=val)
               ts = ts - dt
            ts = int( ts.timestamp() )
        else:
            time_str = dateutil.parser.parse(time_str)
            ts = int(time_str.timestamp())
    else:
        time_str = now
        ts = int(time_str.timestamp())

#    print('get_time(\'{0}\') = {1}'.format(time_str, ts) )
    return ts

#**********************************************************************************
def get_step(ts_from, ts_to):
    # compute step value
    # last 5 min: step 15 (300 : 15: 20 )
    # last 15 min: step 15 (900 : 15: 60 )
    # last 1 hour: step 15 (3600 : 15: 240 )
    # last 3 hours: step 15 (3*3600 : 15: 720 )
    # last 6 hours: step 15 (6*3600 : 15: 1440 )
    # last 12 hours: step 30 (12*3600 : 30: 1440 )
    # last 1 days => step = 120 : 720
    # last 2 days => step = 300 : 576
    # last 7 days => step = 900 : 672
    # last 30 days => step = 1800 : 
    # last 45 days => step = 3600 : 
    # last 90 days => step = 7200 : 
    # last 6 months => step = 10800 : 
    # last 1 year => step = 21600 : 
    # last 2 years => step = 43200 : 
    # last 5 years => step = 86400 : 
    steps = [ 15, 20,30, 120, 300, 900, 1800, 3600, 7200, 10800, 21600, 43200, 864000 ]
    MAX_RESOLUTION = 2500
#    STEP_INTERVAL = 15
    #MAX_RESOLUTION_POINT = 11000
    #* maximum resolution of 11,000 points
    # actual screen size are max 3000 pixel, so it is useless to have more than this value of data,
    # meaning one value for each pixel
    delta = int(ts_to - ts_from)
#    print( 'delta={0}'.format(delta) )
# notsimilar to grafana behavior
#    step = STEP_INTERVAL * (int(int(ts_to - ts_from) / ( MAX_RESOLUTION_POINT * STEP_INTERVAL)) + 1)
#    step = STEP_INTERVAL * (int(delta) / ( MAX_RESOLUTION_POINT * STEP_INTERVAL)) + 1)
    for step in steps:
      if int( delta / step ) < MAX_RESOLUTION:
         break

#    print('step={0}'.format(step))
    return step

#**********************************************************************************
def safe_remove_key(dict_elmt, keys):
   if isinstance( keys, str ):
      keys = [ str ]
   for key in keys:
      if key in dict_elmt:
         del dict_elmt[key]

#***************************************************
def check_filters( filters, name ):
   """
    filter format is:
       {'include': {'names': ['ifAlias', 'ifDescr', 'ifName', 'Value']}}
   """

   #** if not filter defined: keep the field
   if len(filters) == 0:
      return True

   for filter in filters:
      if 'include' in filter:
          if name in filter['include']['names']:
             return True
   return False

#***************************************************
def check_transformations( *args ):
   """
    transformation format is:
	[
	{'id': 'filterFieldsByName', 
		'options': {'include': {'names': ['ifAlias', 'ifDescr', 'ifName', 'Value']}}}
	{'id': 'merge', 'options': {}}
	{'id': 'organize', 'options': {'excludeByName': {}, 'indexByName': {'Value #A': 4, 'Value #B': 5, 'Value #C': 6, 'ifAlias': 0, 'ifDescr': 1, 'ifName': 2, 'ifType': 3}, 'renameByName': {'Value': '', 'Value #C': 'MTU'}}}
	]
   # displayName is compute according to transformation organize option renameByName :
   # 'renameByName': {'Value': '', 'Value #C': 'MTU'}
   """
   res = { 'status': False }

   params = args[0]
   action = params.get('action', 'pre')
   transformations = params.get('transformations')
   if transformations is None:
      return None

   name = None
   refId = None
   snapshotData = None
   
   if action == 'pre':
      name = params.get('name')
      refId = params.get('refId')
      if name is None or refId is None:
         return res
   else:
      snapshotData = params.get('snapshotData')
      if snapshotData is None:
         return res

   filter_found = False
   for trans in transformations:
      if action == 'pre':
         if trans['id'] == 'filterFieldsByName':
            filter_found = True
            if 'include' in trans['options']:
               ref_name = name + ' #' + refId
               if name in trans['options']['include']['names'] \
			            or ref_name in trans['options']['include']['names']:
                  res['status'] = True
                  break
      elif action == 'post':
         if trans['id'] == 'merge':
            #** we receive a list of snapshotDataObj: have to merge fields with same name
            #**   into a sigle snapshotDataObj containing all fields.
            # the list must contain at least 2 elements to merge something
            if len(snapshotData) < 2:
               res['status'] = True
               res['snapshotData'] = snapshotData
            else:
               #** we will merge all contents in the first snapshotDataObj
               snapshot = snapshotData[0] 
               del snapshotData[0]
               #** build a dict on fields name
               field_names = {}
               for field in snapshot['fields']:
                  name = field['name']
                  if name == 'Value':
                     name += ' #' + snapshot['refId']
                     field['name'] = name
                     field['config']['displayName'] = name
                  field_names[name] = 1
               #** now loop on field to determine those that are not currently in the list
               for snapshotDataObj in snapshotData:
                  for field in snapshotDataObj['fields']:
                     name = field['name']
                     if name == 'Value':
                        name += ' #' + snapshotDataObj['refId']
                        field['name'] = name
                        field['config']['displayName'] = name
                     #** if field name not found in the existing fields: add it.
                     if name not in field_names:
                        #** add in known fields list
                        field_names[name] = 1
                        #** add in snapshot fields
                        snapshot['fields'].append(field)
               #** remove all snapshots: subsistute with snapshot
               del snapshot['refId']
               snapshotData = [ snapshot ]
               res['status'] = True
               res['snapshotData'] = snapshotData

         elif trans['id'] == 'organize':
            #** only consider the first element of snapshotData
            snapshot = snapshotData[0]

            #** get columns ordered
            if 'indexByName' in trans['options']:
               sorted_cols = sorted(trans['options']['indexByName']
         			, key=trans['options']['indexByName'].get)

               #** only sort if some colunm names are provided
               if len(sorted_cols) > 0:
                  fields = []
                  for col_name in sorted_cols:
                     f_found = False
                     for field in snapshot['fields']:
                        if field['name'] == col_name:
                           fields.append(field)
                           f_found = True
                           break;
                     if not f_found:
                        print( "field '{}' not found!".format(col_name) )
                  #** subsitute new fields list in snapshot
                  snapshot['fields'] = fields;

            #** get columns rename
            if 'renameByName' in trans['options']:
               for cur_name in trans['options']['renameByName'].keys():
                  new_name = trans['options']['renameByName'][cur_name]
                  if new_name == '':
                     continue
                  for field in snapshot['fields']:
                     name = field['name']
                     if name == cur_name:
                        if 'config' not in field:
                           field['config']={
                              'custom': {},
                              'displayName': new_name,
                              'filterable': True,
                              'mappings': []
                           }
                        else:
                           field['config']['displayName']=new_name
               res['status'] = True

            res['status'] = True
            res['snapshotData'] = snapshotData

   #** if not filter defined: keep the field
   if action == 'pre' and not filter_found:
      res['status'] = True
      return res

   return res

#**********************************************************************************
class GrafanaData(object):
   #***********************************************
   def __init__( *args ):
      self = args[0]
      kwargs = {}
      if len(args) > 1:
         kwargs = args[1]
      self.api = kwargs.get('api')
      self.dashboard = kwargs.get('dashboard')
      self.datasources = kwargs.get('datasources')
      self.time_to = get_time( kwargs.get('time_to') )
      self.time_from = get_time(kwargs.get('time_from'))
      self.context = kwargs.get('context')
      self.debug = kwargs.get('debug')
      if self.debug is None:
         self.debug = False

      self.varfinder = re.compile(r'\$([a-zA-Z0-9_]+)')
     
   #***********************************************
   def get_dashboard_data(self):

      panel_url = None
      if self.context is not None and 'url' in self.context:
         panel_url = self.context['url']
      if panel_url is None:
        panel_url='xXx'

      self.context['time_from'] = self.time_from
      self.context['time_to'] = self.time_to

      snapshotData = None
      res_status = False

      if 'panels' in self.dashboard:
         for panel in self.dashboard['panels']:
            if self.debug:
               print('panel: %s' % (panel) )
            dtsrc = 'default'
            target = None
            if 'datasource' in panel and panel['datasource'] is not None:
               dtsrc = panel['datasource']
               if self.debug:
                  print("dtsrc: %s" % (dtsrc))
        
            if 'targets' in panel and panel['targets'] is not None:
               targets = panel['targets']
               if self.debug:
                  print("target: %s" % (targets))
            else:
               #** row panel... probably
               targets = None
               if self.debug and 'type' in panel and panel['type'] == 'row':
                  print("target-type is 'row': skipped")
               continue

            if isinstance(dtsrc, dict):
               dtsrc = dtsrc['uid']
            # else:
            #    ff
            if (dtsrc in self.datasources or dtsrc == '-- Mixed --' ) and targets is not None:

#              print('dt: {0}'.format(datasources[dtsrc]))
               for target in targets:
                  # don't collect data for disabled queries
                  if 'hide' in target and target['hide']:
                     continue

                  # check query method: timeseries or table
                  query_type = 'query_range'
                  if 'format' in target and target['format'] == 'table':
                     query_type = 'query'

                  # check if expr is defined or and unconfigurated query
                  if 'expr' not in target:
                     print("target expr is not defined: skipped!")
                     continue

                  # check if target expr contains variable ($var)
                  expr = target['expr']
                  m =  self.varfinder.search(expr)
                  if m:
                      expr = self.extract_vars(expr)

                  # params = None
                  # if query_type == 'query_range':
                  #     # compute step value
                  #    step = get_step(self.time_from, self.time_to)

                  #    params = {
                  #       'query_type': query_type,
                  #       'expr': urllib.parse.quote(expr),
                  #       'start': self.time_from,
                  #       'end': self.time_to,
                  #       'step': step
                  #    }
                  # else:
                  #    params = {
                  #       'query_type': query_type,
                  #       'expr': urllib.parse.quote(expr),
                  #       'time': self.time_to
                  #    }
                  if self.debug:
                     print("query GET datasource proxy uri: {0}".format(self.api.client.url))
                  # determine datasource name if global name is 'mixed'
                  if dtsrc == '-- Mixed --' and 'datasource' in target:
                     datasource_name = target['datasource']
                     # datasource set in panel is in new format { 'uid': ..., 'type':... }
                     if isinstance(datasource_name, dict):
                        datasource_name = datasource_name['uid']
                     # datasource is in old format: str; so have to find name in datasource list
                     else:
                        for uid,source in self.datasources.items():
                           if source['name'] == datasource_name:
                              datasource_name = uid
                              break
                  else:
                     datasource_name = dtsrc

                  if not datasource_name in self.datasources:
                     print("datasource '{0}' was not found".format(datasource_name))
                     continue
                  else:
                     if isinstance(self.datasources[datasource_name], dict):
                        datasource_id = str(self.datasources[datasource_name]['id'])
                     else:
                        datasource_id = str(self.datasources[datasource_name])

                  try:
                     if query_type == 'query_range':
                        content = self.api.datasource.query_range(
                           datasource_id,
                           expr,
                           self.time_from,
                           self.time_to,
                           # compute step value
                           get_step(self.time_from, self.time_to)
                        )
                     else:
                        content = self.api.datasource.query(
                           datasource_id,
                           expr,
                           self.time_to,
                        )

                     # content = self.api.datasource.get_datasource_proxy_data( datasource_id, **params )
                  except Exception as e:
                     print('invalid results...')
                     return False

                  if self.debug:
                      print("query GET datasource proxy uri: {0}".format(self.api.client.url))

                  if query_type == 'query_range':
                     snapshotData = self.build_timeseries_snapshotData( target, content['data'], panel['fieldConfig'] )
                  else:
                     snapshotData = self.build_table_snapshotData( target, content['data'], panel )
                  if self.debug:
                     print('#***************************************************************')
                     print( 'snapshot[{0}]: {1}'.format(target['refId'], snapshotData ))
                  if 'snapshotData' not in panel:
                     panel['snapshotData'] = snapshotData
                  else:
                     for elmt in snapshotData:
                        panel['snapshotData'].append(elmt)
               # end for targets
               if panel['type'] == 'table' :
                  res = check_transformations( {
                     'action': 'post'
                     , 'transformations': panel['transformations']
                     , 'snapshotData': panel['snapshotData']
                  } )
                  if res['status']:
                     panel['snapshotData'] = res['snapshotData']
#               del panel['targets']
               safe_remove_key( panel, [ 'targets', 'scopedVars' ])
            else:
               print("either datasource or target was not found")
         # end for panel

         #** remove the target element
         #** e.g.: url..
#/d/000000133/oracle-overview?orgId=1\u0026refresh=30s\u0026var-database=X3D00\u0026var-dbinstance=All\u0026from=now-2d\u0026to=now"
         self.dashboard['snapshot'] = {
            'originalUrl': self.api.client.url + panel_url + '?from=' + str(self.time_from * 1000) 
               + '&to=' +  str(self.time_to * 1000),
            'timestamp': datetime.datetime.now().isoformat(),
         }
         for anno in self.dashboard['annotations']['list']:
            del anno['datasource']

         #** remove autorefresh for snapshots
         self.dashboard['refresh'] = ''
         res_status = True

         #** update vars : user has provided values or we choose one.
         #**    set selected value as current, an remove others choises
         for var_name in self.context['vars'].keys():
            self.update_var_template_into_dashboard( var_name, self.context['vars'][var_name] )
      else:
         print("no panel found!")

      return res_status

   #**********************************************************************************
   def buildDisplayName( self, name, labels ):

      if re.match(r'{{', name):
         tm = Template( name )
         name = tm.render( labels )
      if re.match(r'\$', name):
      #** replace all variables name with values in expr
         for var in self.context['vars']:
            name = name.replace( '$' + var, self.context['vars'][var] )
#      if self.debug:
#         print('buildDisplayName::result displayName="{0}"'.format(name))

      return name

   #**********************************************************************************
   def get_var_value_from_dashboard( self, var_name):
      #** init value to varname: if not found will display the unset var!
      value = '$' + var_name

#      if self.debug:
#         print('get_var_value_from_dashboard::looking for default value for {0}'.format(var_name))
#         print('get_var_value_from_dashboard::looking for default value templating{0}'.format(self.dashboard['templating']['list']))
      for tpl_list in self.dashboard['templating']['list']:
         if self.debug and 'name' in tpl_list:
            print('get_var_value_from_dashboard::check name {0}'.format(tpl_list['name']))
         if 'name' not in tpl_list or tpl_list['name'] != var_name:
            continue
#      #** if all can be set use 'all'
#      if 'includeAll' in tpl_list and tpl_list['includeAll']:
#         value = '.*'
#      else:
         if 'value' in tpl_list['current']:
            cur_val = tpl_list['current']['value']
            if isinstance(cur_val, list) and len(cur_val)>0:
               value = cur_val[0]
            else:
               value = cur_val
            break
      if self.debug:
         print('get_var_value_from_dashboard::value {0}'.format(value))
      return value

   #**********************************************************************************
   def update_var_template_into_dashboard(self, var_name, value ):
      for var_elmt in self.dashboard['templating']['list']:
         if 'name' not in var_elmt or var_elmt['name'] != var_name:
            continue

         val_name = value
         if value == '$__all':
            val_name = 'All'
         var_elmt['current'] = {
		      'selected': True,
            'text': val_name,
            'value': value
         }
         #** have to remove all options so user can't choose an other value for which no
         #** data was collected
         safe_remove_key( var_elmt, [ 
            'datasource'
            , 'definition'
            , 'refresh'
            , 'sort'
            , 'tagValueQuery'
            , 'tags'
            , 'tagsQuery'
         ] )
         var_elmt['query'] = val_name
         var_elmt['options'] = [ var_elmt['current'] ]
         var_elmt['type'] = 'custom'
         break

   #**********************************************************************************
   def build_timeseries_snapshotData( self, target, data, fieldConfig ):
      snapshotData = list()
      snapshotDataObj = {}
      # one snapshotDataObj is a result from query_range
      # it is composed from 2 fields :
      #    one with series of timestamp values 
      #    one with series of queried values

      def_unit = None
      if 'unit' in fieldConfig['defaults']:
         def_unit = fieldConfig['defaults']['unit']

      def_decimals = None
      if 'decimals' in fieldConfig['defaults']:
         def_decimals = fieldConfig['defaults']['decimals']

      def_thresholds = None
      if 'thresholds' in fieldConfig['defaults']:
         def_thresholds = fieldConfig['defaults']['thresholds']

      def_min = None
      if 'min' in fieldConfig['defaults']:
         def_min = fieldConfig['defaults']['min']

      def_max = None
      if 'max' in fieldConfig['defaults']:
         def_max = fieldConfig['defaults']['max']

      def_mappings = None
      if 'mappings' in fieldConfig['defaults']:
         def_mappings = fieldConfig['defaults']['mappings']
      for result in data['result']:
         snapshotDataObj = {}
         labels = {}

         #*** split list of [ (ts,val),...] from values into 2 lists of (ts, tsx,...) (val, valx,...)
         ts=list()
         values=list()
         min = None
         if def_min is not None:
            min = def_min
         max = None
         if def_max is not None:
            max = def_max
         for value_pair in result['values']:
            if self.debug:
               print('ts={0} - val={1}'.format(value_pair[0], value_pair[1]))
            ts.append(int(value_pair[0]) * 1000)
            value = value_pair[1]
            if value is None or value == 'NaN':
               value = None
            else:
               value = float( value )

            if def_min is None and (min is None or min > value):
               min = value
            if def_max is None and (max is None or max < value):
               max = value
            values.append(value)
            if self.debug:
               print('ts={} - value={} - min: {} - max {}'.format(value_pair[0], value, min, max))

         #** build timestamp list
         part_one = {
            'config': { 'unit': 'time:YYYY-MM-DD HH:mm:ss' },
            'name': 'Time',
            'type': 'time',
            'values': ts
         }

         for key in result['metric'].keys():
            if key == '__name__':
               continue
            else:
               labels[key] = result['metric'][key]

         name = ''
         displayName = ''
         #** old panel version has not this attribute
         if not 'legendFormat' in target:
            target['legendFormat'] = ''
         if target['legendFormat'] is None or target['legendFormat'] == '':
            #** if expr is a simple metric use its name
            #** else use label of metrics
            if re.match(r'^[a-zA-Z0-9_]+$', target['expr']):
               name = target['expr']
            name = name + json.dumps(labels)
         else:
#** TO DO build name on template
            name = target['legendFormat']
            displayName = self.buildDisplayName( name, labels )

         labels['displayName'] = name
 
         part_two = {
  	      	'config': {
               'displayName': displayName,
               'max': max,
               'min': min,
               'decimals': def_decimals,
               'unit': def_unit,
               'mappings': def_mappings,
               'thresholds': def_thresholds,
            },
            'labels': labels,
            'name': 'Value',
            'type': 'number',
            'values': values
         }

         if def_decimals is None:
            del part_two['config']['decimals']
         if def_thresholds is None:
            del part_two['config']['thresholds']
         if def_unit is None:
            del part_two['config']['unit']
         if def_mappings is None:
            del part_two['config']['mappings']

         #** build snapshotDataObj
         snapshotDataObj['fields']=[ part_one, part_two]
         snapshotDataObj['meta'] = { 'preferredVisualisationType': 'graph' }
         # snapshotDataObj['name'] = name
         snapshotDataObj['name'] = displayName
         snapshotDataObj['refId'] = target['refId']
         # if self.debug:
         #    print( 'build_timeseries_snapshotData::snapshot[{0}]: {1}'.format(target['refId'], snapshotDataObj ))
         snapshotData.append( snapshotDataObj )

      return snapshotData

   #**********************************************************************************
   def build_table_snapshotData( self, target, data, panel ):
      snapshotData = list()

      # one snapshotDataObj is a result from query
      # it is composed from 2 fields :
      #    metrics
      #    value (timestamp, value) 
      #** mappings seems to be the panel['fieldConfig']['defaults']['mappings']
      def_mappings = panel['fieldConfig']['defaults']['mappings']

      def_unit = None
      if 'unit' in panel['fieldConfig']['defaults']:
         def_unit = panel['fieldConfig']['defaults']['unit']

      def_decimals = None
      if 'decimals' in panel['fieldConfig']['defaults']:
         def_decimals = panel['fieldConfig']['defaults']['decimals']

      def_thresholds = None
      if 'thresholds' in panel['fieldConfig']['defaults']:
         def_thresholds = panel['fieldConfig']['defaults']['thresholds']

      if panel['type'] == 'table':
         #** have to build a list of object on metrics attr / value with metrics
         # obj { config: {}, type: "string", name: "[metric]", values: [ metric_val / result ]
         # __name__ => type: "number", name: "Value #[refId]", values: [ vetric_val /result]

         snapshotDataObj = { }
         dataObj = { }
         fields = list()
         #** first initialize the column to store

         if len( data['result']) > 0:
            result = data['result'][0]
            #** add special column 'time' with value result['value'][1]
            result['metric']['__time__'] = 'Time'
            result['metric']['__value__'] = 'Value'
            for metric in result['metric'].keys():
               if metric == '__value__' or  metric == '__time__':
                  metric_name = result['metric'][metric]
               else:
                  metric_name = metric
               if self.debug:
                  print( 'build_table_snapshotData::snapshot[{0}]: check transformation on metric {1}'.format(target['refId'], metric_name ))
               res = check_transformations( {
                  'action': 'pre',
                  'transformations': panel['transformations'],
                  'name': metric_name,
                  'refId': target['refId']
         		} )
               # if not check_filters( filter_list, metric_name ):
               if res is not None and not res['status']:
                  if self.debug:
                     print( 'build_table_snapshotData::snapshot[{0}]: metric {1} filtered'.format(target['refId'], metric_name ))
                  continue
#               metric_displayed_name = res['display_name']
               if 'name' in res:
                  metric_name = res['name']

               if metric not in dataObj:
                  dataObj[metric] = {
                     'config': {
                        'custom': {},
                        'displayName': metric_name,
                        'filterable': True,
                        'mappings': []
                     },
                     'name': metric_name,
                     'type': 'string',
                     'values': [ ]
                  }
                  fields.append( dataObj[metric] )

         for result in data['result']:
            for metric in dataObj.keys():
               if metric == '__value__':
                  metric_val = result['value'][1]
               elif metric == '__time__':
                  metric_val = result['value'][0]
               else:
                  metric_val = result['metric'][metric]
               dataObj[metric]['values'].append( metric_val )

         #** build snapshotDataObj
         snapshotDataObj['refId'] = target['refId']
         snapshotDataObj['fields'] = fields
         snapshotDataObj['meta'] = { }
      else:
         for result in data['result']:
            snapshotDataObj = { }
            fields = list()
            value_pair = result['value']
            # print('ts={0} - val={1}'.format(value_pair[0], value_pair[1]))
            ts = int(value_pair[0]) * 1000
            value = value_pair[1]
            if value is None or value == 'NaN':
               value = None
            else:
               value = float( value )

            #** build timestamp field
            fields.append({
               'config': { 
                  'mappings': def_mappings,
                  'unit': 'time:YYYY-MM-DD HH:mm:ss'
               },
               'name': 'Time',
               'type': 'time',
               'values': [ ts ]
            })
            #** build value field
            field = {
               'config': {
                  'mappings': def_mappings,
                  'decimals': def_decimals,
                  'unit': def_unit,
                  'thresholds': def_thresholds,
                  'max': value,
                  'min': value,
               },
               'name': 'Value',
               'type': 'number',
               'values': [ value ]
            }
            if def_decimals is None:
               del field['config']['decimals']
            if def_thresholds is None:
               del field['config']['thresholds']
            if def_unit is None:
               del field['config']['unit']
            fields.append( field )

            for metric in result['metric'].keys():
               fields.append({
                  'config': { 
                     'mappings': def_mappings,
                     'filterable': True
                  },
                  'name': metric,
                  'type': 'string',
                  'values': [ result['metric'][metric] ]
   	         })

         #** build snapshotDataObj
         snapshotDataObj['refId'] = target['refId']
         snapshotDataObj['fields'] = fields
         snapshotDataObj['meta'] = { 'preferredVisualisationType': 'table' }
      #** end else graph panel
      if self.debug:
         print( 'build_table_snapshotData::snapshot[{0}]: {1}'.format(target['refId'], snapshotDataObj ))
      snapshotData.append( snapshotDataObj )

      return snapshotData

   #**********************************************************************************
   def extract_vars( self, expr ):

      vl = list()
      #** collect all var_name from expression
      for m in re.finditer( self.varfinder, expr ):
         var = m.group(1)
         #** check if the context (user args) provides a value for thee variable
         #** else use the  current value from dashboard templating list
         if var not in self.context['vars']:
             self.context['vars'][var] = self.get_var_value_from_dashboard( var )
         if self.debug:
            print( 'found variable ${0} => "{1}"'.format(var, self.context['vars'][var]) )
         vl.append(var)

      #** replace all variables name with values in expr
      for var in vl:
         val = self.context['vars'][var]
         if val == '$__all':
            val = '.*'
         expr = expr.replace( '$' + var, val )

      if self.debug:
         print('extract_vars::result expr="{0}"'.format(expr))
      return expr

