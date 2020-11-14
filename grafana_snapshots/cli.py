#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 1 2020

@author: jfpik

Suivi des modifications :
    V 0.0.0 - 2020/09/16 - JF. PIK - initial version
    V 0.0.1 - 2020/10/16 - JF. PIK - switch to grafana-api

"""
#***********************************************************************************************
#
#
# TODO:
#***********************************************************************************************


from grafana_snapshots.constants import (PKG_NAME, PKG_VERSION, JSON_CONFIG_NAME)

import argparse, json, sys, os, re, socket, logging, subprocess
import datetime, dateutil.parser, dateutil.relativedelta
import unicodedata, traceback

from grafana_api.grafana_face import GrafanaFace

from grafana_snapshots.jsonConfig import jsonConfig
from grafana_snapshots.grafanaData import GrafanaData

#******************************************************************************************
config = None
#******************************************************************************************
class myArgs:
  attrs = [ 'pattern'
                , 'base_path', 'config_file'
                , 'dashboard_name'
                , 'time_from', 'time_to'
                , 'verbose'
                ]
  def __init__(self):

    for attr in myArgs.attrs:
        setattr(self, attr, None)

  def __repr__(self):
    obj = {}
    for attr in myArgs.attrs:
        val = getattr(self, attr)
        if not val is None:
           obj[attr] = val
    return json.dumps(obj)

#******************************************************************************************
def remove_accents_and_space(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    res = u"".join([c for c in nfkd_form if not unicodedata.combining(c)])
    res = re.sub('\s+', '_', res)
    return res

#******************************************************************************************
def get_dashboard_content(config, grafana_api, dashboard_name):

   try:
      res = grafana_api.search.search_dashboards(
	type_='dash-db'
	, limit=config['grafana']['search_api_limit']
	)
   except Exception as e:
      print("error: {}".format(traceback.format_exc()) )
#      print("error: {} - message: {}".format(e.__doc__, e.message) )
      return None
   dashboards = res
   board = None
   b_found = False
   if args.verbose:
      print("There are {0} dashboards:".format(len(dashboards)))
   for board in dashboards:
      if board['title'] == dashboard_name:
         b_found = True
         if args.verbose:
            print("dashboard found")
         break
   if b_found and board:
      try:
         board = grafana_api.dashboard.get_dashboard(board['uid'])
      except Exception as e:
         print("error: {}".format(traceback.format_exc()) )
   else:
      board = None

   return board

#******************************************************************************************
def save_snapshot(config, args, base_path, dashboard_name, params, action):

    output_file = base_path + '/'
    if 'output_path' in config['general']:
       output_file += config['general']['output_path'] + '/'
    file_name = remove_accents_and_space( dashboard_name )
    output_file += file_name + '.json'
    try:
       output = open(output_file, 'w')
    except OSError as e:
       print('File {0} error: {1}.'.format(output_file, e.strerror))
       sys.exit(2)

    content = None
    if args.pretty:
       content = json.dumps( params, sort_keys=True, indent=2 )
    else:
       content = json.dumps( params )
    output.write( content )
    output.close()
    print("OK: snapshot {1} to '{0}'.".format(output_file, action))
 
#******************************************************************************************
# get command line arguments

parser = argparse.ArgumentParser(description='play with grafana snapshots.')
parser.add_argument('-b', '--base_path'
                        , help='set base directory to find default files.')
parser.add_argument('-c', '--config_file'
                        , help='path to config files.')

parser.add_argument('-d', '--dashboard_name'
                        , help='name of dashboard to export or generate.')

parser.add_argument('-f', '--time_from'
                        , help='start_time of data; format is iso date or string containg now-xF. default is \'now-5m\'.')

parser.add_argument('-i', '--import_file'
                        , help='path to the file to import as a snapshot. File as to e previously exported by this tool.')

parser.add_argument('-o', '--context_name'
                        , help='name of the context form configuration file to use to generate the data. Default is the dashbord_name.')

parser.add_argument('-p', '--pretty'
                        , action='store_true'
                        , help='use JSON indentation when exporting or extraction snapshot.')

parser.add_argument('-s', '--snapshot_name'
                        , help='name of snapshot to extract from Grafana.')

parser.add_argument('-t', '--time_to'
                        , help='end_time of data; format is iso date or string containg now-xF. default is \'now\'.')

parser.add_argument('-v ', '--verbose'
                        , action='store_true'
                        , help='verbose mode; display log message to stdout.')

parser.add_argument('-V', '--version'
			, action='version', version='{0} {1}'.format(PKG_NAME, PKG_VERSION)
                        , help='display program version and exit..')

parser.add_argument('action', metavar='ACTION'
			, nargs='?'
			, choices=['generate', 'import', 'export', 'extract']
			, default='generate'
                        , help='action to perform on snapshot. Is one of \'generate\' (default), \'export\', \'extract\' or, \'import\'.\ngenerate: generate snapshot and publish it into Grafana.\nexport: generate snapshot and dump it to local file.\nimport: import a local snapshoot (previously exported) to Grafana.\nextract: get snapshoot from Grafana and dump it to local file.')

inArgs = myArgs()
args = parser.parse_args(namespace=inArgs)

#***********************************************************************************************
def main():
   base_path = '.'
#   base_path = os.path.dirname(os.path.abspath(__file__))
   if args.base_path is not None:
      base_path = inArgs.base_path

   config_file = base_path + '/' + JSON_CONFIG_NAME
   if args.config_file is not None:
      config_file = inArgs.config_file

   confObj = jsonConfig(config_file)
   if confObj is None:
       print( 'init config failure !')
       sys.exit(2)
   config = confObj.load()
   if config is None:
       print( confObj.err_msg )
       sys.exit(2)

   if args.verbose is None:
      if 'debug' in config['general']:
         args.verbose = config['general']['debug']
      else:
         args.verbose = False
   
   #print( json.dumps(config, sort_keys=True, indent=4) )

   datasources = {}
   context = { 'vars': {} }

   if args.dashboard_name is None:
      args.dashboard_name = 'Oracle Overview'

   # collect info from configuration file
   context_name = args.dashboard_name
   if args.context_name is not None:
      context_name = args.context_name

   if 'contexts' in config and context_name in config['contexts']:
      cur_cont = config['contexts'][context_name]
      if 'vars' in cur_cont:
         context['vars'].update(cur_cont['vars'])
      if 'time_from' in cur_cont and args.time_from is None:
         args.time_from = cur_cont['time_from']
      if 'time_to' in cur_cont and args.time_to is None:
         args.time_to = cur_cont['time_to']

   if args.time_from is None:
      args.time_from = 'now-5m'
   if args.time_to is None:
      args.time_to = 'now'

   grafana_api = GrafanaFace(
	auth=config['grafana']['token']
	, host=config['grafana']['host']
	, protocol=config['grafana']['protocol']
	, port=config['grafana']['port']
	, verify=config['grafana']['verify_ssl']
   )
   try:
      res = grafana_api.health.check()
      if res['database'] != 'ok':
         print("grafana health_check is not KO.")
         sys.exit(2)
      elif args.verbose:
         print("grafana health_check is OK.")
   except e:
      print("error: {} - message: {}".format(status_code, e.message) )
      sys.exit(2)

   if args.action == 'generate' or args.action == 'export':
      dashboard = get_dashboard_content(config, grafana_api, args.dashboard_name)
      if dashboard is None:
         print( "dashboard not found !")
         sys.exit(0)

      try:
         dtsrcs = grafana_api.datasource.list_datasources()
      except e:
         print("error: {} - message: {}".format(status_code, e.message) )
         sys.exit(2)

      for dtsrc in dtsrcs:
         datasources[dtsrc['name']] = dtsrc['id']
         if 'isDefault' in dtsrc and dtsrc['isDefault']:
            datasources['default'] = dtsrc['id']
      if args.verbose:
         print('datasources OK.')

      context['url'] = dashboard['meta']['url']
      params = {
	   'api': grafana_api,
	   'dashboard': dashboard['dashboard'],
	   'datasources': datasources,
	   'time_to': args.time_to,
	   'time_from': args.time_from,
	   'context': context,
	   'debug': args.verbose
      }

      #**********************************************************************************
      #*** collect the data from datasources to populate the snapshot
      data_api = GrafanaData( params );
      res = data_api.get_dashboard_data()
      if res is None or not res:
         print("can't obtain dashboard data... snapshot canceled!")
         sys.exit(2)

      #**********************************************************************************
      #*** build the dashboard name
      dashboard_name = args.dashboard_name
      if 'snapshot_suffix' in config['general'] and config['general']['snapshot_suffix'] :
         dashboard_name += datetime.datetime.today().strftime(config['general']['snapshot_suffix'])

      #**********************************************************************************
      # init element for new snapshot

      time_from = data_api.context['time_from']
      if time_from is None:
         #** 'now-5m'
         time_from = datetime.datetime.now().timestamp()
         time_from = datetime.datetime.fromtimestamp(time_from - 300).isoformat()
      else:
         time_from = datetime.datetime.fromtimestamp(time_from).isoformat()

      time_to = data_api.context['time_to']
      if time_to is None:
         #** 'now'
         time_to = datetime.datetime.now().isoformat()
      else:
         time_to = datetime.datetime.fromtimestamp(time_to).isoformat()
      if args.verbose:
         print('time_from = {0} - time_to = {1}'.format(time_from, time_to))

      raw = dashboard['dashboard']['time']
      dashboard['dashboard']['time'] = { 'from': time_from, 'to': time_to, 'raw': raw }

      params = {
	'dashboard': dashboard['dashboard'],
	'name': dashboard_name
      }

      if args.action == 'generate':
         #**********************************************************************************
         #*** check if snapshot name is already present in list
         res = []
         try:
            res = grafana_api.snapshots.get_dashboard_snapshots()
         except:
            print("can't list existing snapshot")

         snapshots = res
         old_snap = False
         del_snap = False
         for snap in snapshots:
            #print(snap)
            if dashboard_name == snap['name']:
               old_snap = True
               try:
                  res = grafana_api.snapshots.delete_snapshot_by_key(snap['key'])
                  del_snap = True
               except:
                  print("can't remove existing snapshot");
      #         print( resp)
                  break
         if args.verbose:
            if old_snap and del_snap:
               print("old snapshot was found and removed.")
            elif old_snap:
               print("old snapshot was found but not removed.")
            else:
               print("old snapshot was not found.")

         #**********************************************************************************
         # create new snapshot
         try:
            res = grafana_api.snapshots.create_new_snapshot( **params )
            print("OK: new snapshot '{}' created.".format(dashboard_name))
         except Exception as e:
            print("error: {}".format(traceback.format_exc()) )
            print("can't create new snapshot !");

      else: # action is export

         output_file = base_path + '/'
         if 'output_path' in config['general']:
            output_file += config['general']['output_path'] + '/'
         file_name = remove_accents_and_space( dashboard_name )
         output_file += file_name + '.json'
         try:
            output = open(output_file, 'w')
         except OSError as e:
            print('File {0} error: {1}.'.format(output_file, e.strerror))
            sys.exit(2)

         content = None
         if args.pretty:
            content = json.dumps( params, sort_keys=True, indent=2 )
         else:
            content = json.dumps( params )
         output.write( content )
         output.close()
         print("OK: snapshot exported to '{}' exported.".format(output_file))
      # end if action == export 

   # end if action == generate|export 

   elif args.action == 'import':
      if args.import_file is None:
         print('no file to import provided!')
         sys.exit(2)
      import_file = args.import_file
      if not re.search(r'^/', args.import_file):
         import_path = base_path + '/'
         if 'output_path' in config['general']:
            import_path += config['general']['output_path'] + '/'
      import_path += import_file
      try:
         input = open(import_path, 'r')
      except OSError as e:
         print('File {0} error: {1}.'.format(import_path, e.strerror))
         sys.exit(2)

      data = input.read()
      input.close()

      try:
         params = json.loads(data)
      except json.JSONDecodeError as e:
         print("error reading '{}': {}".format(import_path, e))
         sys.exit(2)

#* format for exported snapshots is:
#   params = {
#	'dashboard': dashboard['dashboard'],
#	'name': dashboard_name
#   }

      if 'dashboard' in params and 'name' in params:
         dashboard_name= params['name']

         data_api = GrafanaData( { 'api': grafana_api, } );
         res = data_api.insert_snapshot( **params )
         if res:
            print("OK: snapshot '{}' imported.".format(dashboard_name))
         else:
            print("can't create new snapshot !");

   # end if action == import
   elif args.action == 'extract':
      #**********************************************************************************
      #*** check if snapshot name is already present in list
      res = []
      try:
         res = grafana_api.snapshots.get_dashboard_snapshots()
      except:
         print("can't find existing snapshot")

      snapshots = res
      extracted_snap = None
      for snap in snapshots:
         #print(snap)
         if args.snapshot_name == snap['name']:
            try:
               extracted_snap = grafana_api.snapshots.get_snapshot_by_key(snap['key'])
            except Exception as e:
               print("error: {}".format(traceback.format_exc()) )
               print("can't remove existing snapshot");
            break
      if extracted_snap is None:
         print( "can't find {} in existing snapshots".format(args.snapshot_name) )
         sys.exit(2)

      save_snapshot(config, args, base_path, args.snapshot_name, extracted_snap, 'extracted')
 
# end main...


if __name__  == '__main__':
   main()
