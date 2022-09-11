#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 1 2020

@author: jfpik

Suivi des modifications :
    V 0.0.0 - 2020/09/16 - JF. PIK - initial version
    V 0.0.1 - 2020/10/16 - JF. PIK - switch to grafana-api
    V 0.2.0 - 2022/02/12 - JF. PIK - switch to grafana_client

"""
#***********************************************************************************************
#
#
# TODO:
#***********************************************************************************************

from grafana_snapshots.constants import (PKG_NAME, PKG_VERSION, CONFIG_NAME)

import argparse, datetime, json, os, re, sys, traceback, unicodedata, yaml

import grafana_client.client as GrafanaApi
import grafana_snapshots.grafana as Grafana

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
def save_snapshot(config, args, base_path, dashboard_name, params, action):

    output_file = base_path 
    if 'output_path' in config['general']:
       output_file = os.path.join(output_file, config['general']['output_path'])
    file_name = Grafana.remove_accents_and_space( dashboard_name )
    output_file = os.path.join(output_file, file_name + '.json')
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
 
#***********************************************************************************************
def main():
   #******************************************************************
   # get command line arguments

   parser = argparse.ArgumentParser(description='play with grafana snapshots.')
   parser.add_argument('-b', '--base_path'
                           , help='set base directory to find default files.')
   parser.add_argument('-c', '--config_file'
                           , help='path to config files.')

   parser.add_argument('-d', '--dashboard_name'
                           , help='name of dashboard to export or generate.')

   parser.add_argument('-F', '--grafana_folder'
                  			, help='the folder name where to export/import from/into Grafana.')

   parser.add_argument('-f', '--time_from'
                           , help='start_time of data; format is iso date or string containg now-xF. default is \'now-5m\'.')

   parser.add_argument('-g', '--grafana_label'
                  			, help='label in the config file that represents the grafana to connect to.'
                           , default='default')

   parser.add_argument('-i', '--import_file'
                           , help='path to the file to import as a snapshot. File as to e previously exported by this tool.')

   parser.add_argument('-o', '--context_name'
                           , help='name of the context set in configuration file to use to generate the data. By default the dashboard_name is used as context_name.')

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

   base_path = '.'
   if args.base_path is not None:
      base_path = inArgs.base_path

   config_file = os.path.join(base_path, CONFIG_NAME)
   if args.config_file is not None:
      if not re.search(r'^(\.|\/)?/', config_file):
         config_file = os.path.join(base_path,args.config_file)
      else:
         config_file = args.config_file

   config = None
   try:
      with open(config_file, 'r') as cfg_fh:
         try:
            config = yaml.safe_load(cfg_fh)
         except yaml.scanner.ScannerError as exc:
            mark = exc.problem_mark
            print("Yaml file parsing unsuccessul : %s - line: %s column: %s => %s" % (config_file, mark.line+1, mark.column+1, exc.problem) )
   except Exception as exp:
      print('ERROR: config file not read: %s' % str(exp))

   if config is None:
      sys.exit(1)

   if args.verbose is None:
      if 'debug' in config['general']:
         args.verbose = config['general']['debug']
      else:
         args.verbose = False
   else:
      config['general']['debug'] = args.verbose
   
   datasources = {}
   context = { 'vars': {} }

   if args.dashboard_name is None:
      args.dashboard_name = 'Oracle Overview'

   # collect info from configuration file
   context_name = args.dashboard_name
   if args.context_name is not None:
      context_name = args.context_name

   config['general']['dashboard_name'] = context_name

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
#************
   config['check_folder'] = False
   if args.grafana_folder is not None:
      config['general']['grafana_folder'] = args.grafana_folder
      config['check_folder'] = True

#************
   if not args.grafana_label in config['grafana']:
      print("ERROR: invalid grafana config label has been specified (-g {0}).".format(args.grafana_label))
      sys.exit(1)
   
   #** init default conf from grafana with set label.
   config['grafana'] = config['grafana'][args.grafana_label]

#************
   if not 'token' in config['grafana']:
      print("ERROR: no token has been specified in grafana config label '{0}'.".format(args.grafana_label))
      sys.exit(1)

   params = {
      'host': config['grafana'].get('host', 'localhost'),
      'protocol': config['grafana'].get('protocol', 'http'),
      'port': config['grafana'].get('port', '3000'),
      'token': config['grafana'].get('token'),
      'verify_ssl': config['grafana'].get('verify_ssl', True),
      'search_api_limit': config['grafana'].get('search_api_limit', 5000),
      'folder': config['general'].get('grafana_folder', 'General'),
   }

   try:
      grafana_api = Grafana.Grafana( **params )
   except Exception as e:
      print("ERROR: {} - message: {}".format(e) )
      sys.exit(1)

   if args.action == 'generate' or args.action == 'export':
      try:
         dashboard = grafana_api.export_dashboard(config['general']['dashboard_name'])
      except Grafana.GrafanaNotFoundError:
         print("KO: dashboard name not found '{0}'".format(config['general']['dashboard_name']))
         sys.exit(1)
      except Exception as exp:
         print("error: dashboard '{0}' export exception '{1}'".format(config['general']['dashboard_name'], traceback.format_exc()))
         sys.exit(1)

      # dashboard = get_dashboard_content(config, grafana_api, args.dashboard_name)
      # if dashboard is None:
      #    print( "dashboard not found !")
      #    sys.exit(0)

      try:
         dtsrcs = grafana_api.list_datasources()
      except Exception as e:
         print("error: {} - message: {}".format(e.status_code, e.message) )
         sys.exit(2)

      for dtsrc in dtsrcs:
         if 'uid' not in dtsrc:
            datasources[dtsrc['name']] = dtsrc['id']
            if 'isDefault' in dtsrc and dtsrc['isDefault']:
               datasources['default'] = dtsrc['id']
         else:
            datasources[dtsrc['uid']] = {
               'id': dtsrc['id'],
               'name': dtsrc['name'],
            }

      if args.verbose:
         print('datasources OK.')

      context['url'] = dashboard['meta']['url']
      params = {
         'api': grafana_api.grafana_api,
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
      dashboard_name = config['general']['dashboard_name']
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
         # create new snapshot
         try:
            res = grafana_api.insert_snapshot( **params )
            if res:
               print("OK: new snapshot '{0}' created.".format(dashboard_name))
            else:
               print("KO: snapshot '{0}' not created.".format(dashboard_name))
         except Exception as e:
            print("error: {}".format(traceback.format_exc()) )
            print("can't create new snapshot !");

      else: # action is export
         save_snapshot(config, args, base_path, dashboard_name, params, 'exported')
         # end if action == export 

   # end if action == generate|export 
   #***********************************************************
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
      #	   'dashboard': dashboard['dashboard'],
      #	   'name': dashboard_name
      #   }

      if 'dashboard' in params and 'name' in params:
         dashboard_name= params['name']
         try:
            res = grafana_api.insert_snapshot( **params )
            if res:
               print("OK: snapshot '{}' imported.".format(dashboard_name))
            else:
               print("KO: snapshot '{0}' not imported.".format(dashboard_name))
         except Exception as e:
            print("error: {}".format(traceback.format_exc()) )
            print("can't import snapshot !");
   # end if action == import

   #***********************************************************
   elif args.action == 'extract':
      try:
         extracted_snap = grafana_api.get_snapshot_by_name(args.snapshot_name)
      except Exception as e:
         print("error: {}".format(traceback.format_exc()) )
         print("can't remove existing snapshot");
         sys.exit(2)
      
      if extracted_snap is None:
         print( "can't find {} in existing snapshots".format(args.snapshot_name) )
         sys.exit(2)

      save_snapshot(config, args, base_path, args.snapshot_name, extracted_snap, 'extracted')
 
# end main...
#***********************************************************************************************

if __name__  == '__main__':
   main()

#***********************************************************************************************
# over