# Grafana Snapshots

Create Grafana snapshots **including data(!)**.

The application uses the [Grafana HTTP API] and its Python client [grafana-client].

The aim of this tool is to:

1. Easily build snapshots from existing Grafana dashboard.
1. Export the snapshots to a local storage in JSON format so it can be sent, imported an visualized to a remote Grafana.
1. Import a snapshot in JSON format to a Grafana.

The development of this tool began when we discovered that there was no solution to automate the creation of snapshots from Grafana; only the functionality from the GUI was operational.
That was a sticking point for us since it prevented us from being able to provide reports other than manually build dashboards with statics screenshots.
With this tool, we are able to build static dashboards, also called snapshots, that can be shared and visualized in grafana.
It can be also used to store particular situation even if the data window is out of the scope of the retention of the datasource.

## Install package

Install from PyPI.

```bash
pip3 install grafana-snapshots
```

Install from repository.

```bash
pip install git+https://github.com/grafana-toolbox/grafana-snapshots.git
```

## Requirements

* bash
* python >3.6
* python modules:

  * python_dateutil
  * setuptool
  * PyYaml
  * jinja2
  * grafana-client 2.0.0 what will pull the dependencies
    * requests
    * idna
    * urllib3
    * certifi
    * chardet
* Access to a Grafana API server.
* A `Token` of an `Admin` role (grafana APIKey).

## Configuration

The configuration is stored in a YAML file.

It contains 3 parts:

* **general**: for script env.
  * **debug**: enable verbose (debug) trace (for dev only...)
  * **snapshot_suffix**: when generating or exporting a dashboard to snapshot, append that suffix to the snapshot name or file name. The suffix can contain plain text and pattern that is translated with strftime command.
  * **output_path**: where to store the exported snapshots.
* **grafana**: for grafana access settings
  * **label**: a label to refer a grafana server. There must be at least 'default' label. It is used to reference several Grafana server so you can generate from one and to import to another using different 'label'.
    * **protocol**, **host**, **port**: use to build the access url
    * **verify_ssl**: to check ssl certificate or not
    * **token**: APIKEY with admin right from Grafana to access the REST API.
    * **search_api_limit**: the maximum element to retrieve on search over API.
* **context**: to define default values for dashboards, time_from, time_to and values for variables that the data exposed in the dashboard are depending from. It is an object. Add a sub-object identified by the dashboard name, for each dashboard you want to add default value.
  Each object can contain:
  * **time_from** and **time_to**
  * an object called **vars**: the definitions of each variable with it's corresponding value.

## Usages

build a directory structure:

* grafana-snapshots/
  * conf/grafana-snapshots.json
    where your main configuration file is
  * snapshots/
    where your exported snapshots will be stored.

**usage**:

```bash
grafana-snapshots -h
usage: grafana-snapshots [-h] [-b BASE_PATH] [-c CONFIG_FILE]
                         [-d DASHBOARD_NAME] [-F GRAFANA_FOLDER]
                         [-f TIME_FROM] [-g GRAFANA_LABEL] [-i IMPORT_FILE]
                         [-o CONTEXT_NAME] [-p] [-s SNAPSHOT_NAME]
                         [-t TIME_TO] [-v] [-V]
                         [ACTION]
```

then enter into your directory and type in you commands.

***Example:***

* **generate** a snapshot for the dashboard 'My dashboard' with default values for 'from' (now - 5 min) to 'now':

```bash
$ grafana-snapshots -d "My dashboard"
OK: new snapshot 'My_dashboard_202010241750.json' created.
```

then you can go into Grafana Gui and find the snapshot in dashboard/Manage/Snapshots part.

* **export** the dashboard 'My dashboard' with data from: 'now-1d' to 'now':

```bash
$ grafana-snapshots -d "My dashboard" -f "now-1d" export
OK: snapshot exported to './snapshots/My_dashboard_202010241750.json' exported.
```

then you can find the created file in the "snapshots" dir.

* **import** the file './snapshots/My_dashboard_202010241750.json' into Grafana

```bash
$ grafana-snapshots -i './snapshots/My_dashboard_202010241750.json' import
OK: snapshot './snapshots/My_dashboard_202010241750.json' imported.
```

then you can go into Grafana Gui and find the snapshot in dashboard/Manage/Snapshots part.

* **extract** the snapshot "My Snapshot" from grafana and dump it to json file:

```bash
$ grafana-snapshots -s "My Snapshot"  extract
level="INFO" date="2026-07-29 11:06:48,693" source="grafana-snapshots[26669]" file="cli.py:73" function="save_snapshot" msg="OK: snapshot extracted to '/tmp/Random_Walk.json'."
```

## ⚠️ BREAKING CHANGE

Since Grafana v11, creating API snapshots of a non-existing dashboard is no longer supported (see issue [#98448](https://github.com/grafana/grafana/issues/98448)).

As a result, importing snapshots into a Grafana instance is not possible starting from this version unless the underlying dashboard UID exists in the Grafana database.

To work around this issue, the application checks if the Grafana version is **11.0 or higher**. If so, it creates a fallback dashboard and uses its UID to import all snapshots.

These three parameters are managed in the configuration file using the following variables:

* `default_dashboard_uid`: The default dashboard UID used for snapshot generation. If set to an existing dashboard UID, no dashboard will be created. Otherwise (default: `"____DEFAULT_UID_SNAPSHOTS____"`), an empty dashboard using this UID will be generated.
* `default_dashboard_title`: The title of the generated dashboard (default: `"_DEFAULT_DASHBOARD_FOR_SNAPSHOTS_"`).
* `default_dashboard_folder`: The folder where the generated dashboard will be placed (default: `"Draft"`).

## TODO - Known Limitations

* actual snapshots can only contain a single set of variables/values.
* currently snapshots for Table doesn't work.
* repeat is not supported
* overrides are not used to modify values !
* changes with new version of Grafana (>7.5) have several impacts on the rendering of panels; a code review is required to improve the result.

[grafana-client]: https://github.com/grafana-toolbox/grafana-client
[Grafana HTTP API]: https://grafana.com/docs/grafana/latest/http_api/
