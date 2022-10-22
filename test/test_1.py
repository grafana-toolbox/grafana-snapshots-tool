import pytest, json
from distutils.version import LooseVersion

from grafana_snapshots.dataresults.dataresults import dataresults

datasource_type = 'prometheus'
api_version = LooseVersion('7.5.11')

json_str = """
{
    "status": "success",
    "data": {
        "resultType": "matrix",
        "result": [
            {
                "metric": {
                    "__name__": "cpu_usage_percent",
                    "instance": "private_host",
                    "job": "private"
                },
                "values": [
                    [
                        1664697840,
                        "2"
                    ],
                    [
                        1664697855,
                        "2"
                    ],
                    [
                        1664697870,
                        "1.8"
                    ],
                    [
                        1664697885,
                        "1.8"
                    ],
                    [
                        1664697900,
                        "2"
                    ],
                    [
                        1664697915,
                        "2"
                    ],
                    [
                        1664697930,
                        "1.9"
                    ],
                    [
                        1664697945,
                        "1.9"
                    ],
                    [
                        1664697960,
                        "1.9"
                    ],
                    [
                        1664697975,
                        "1.9"
                    ],
                    [
                        1664697990,
                        "1.9"
                    ]
                ]
            }
        ]
    }
}
"""

panel_str = """
{
  "id": 2,
  "gridPos": {
    "h": 9,
    "w": 12,
    "x": 0,
    "y": 0
  },
  "type": "timeseries",
  "title": "test",
  "datasource": {
    "type": "datasource",
    "uid": "-- Mixed --"
  },
  "fieldConfig": {
    "defaults": {
      "custom": {
        "drawStyle": "line",
        "lineInterpolation": "linear",
        "barAlignment": 0,
        "lineWidth": 1,
        "fillOpacity": 0,
        "gradientMode": "none",
        "spanNulls": false,
        "showPoints": "auto",
        "pointSize": 5,
        "stacking": {
          "mode": "none",
          "group": "A"
        },
        "axisPlacement": "auto",
        "axisLabel": "",
        "axisColorMode": "text",
        "scaleDistribution": {
          "type": "linear"
        },
        "axisCenteredZero": false,
        "hideFrom": {
          "tooltip": false,
          "viz": false,
          "legend": false
        },
        "thresholdsStyle": {
          "mode": "off"
        }
      },
      "color": {
        "mode": "palette-classic"
      },
      "mappings": [],
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {
            "color": "green",
            "value": null
          },
          {
            "color": "red",
            "value": 80
          }
        ]
      }
    },
    "overrides": []
  },
  "options": {
    "tooltip": {
      "mode": "single",
      "sort": "none"
    },
    "legend": {
      "showLegend": true,
      "displayMode": "list",
      "placement": "bottom",
      "calcs": []
    }
  },
  "targets": [
    {
      "datasource": {
        "type": "prometheus",
        "uid": "h8KkCLt7z"
      },
      "editorMode": "code",
      "expr": "up",
      "hide": false,
      "interval": "60s",
      "legendFormat": "{{ instance }}",
      "range": true,
      "refId": "A"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "h8KkCLt7z"
      },
      "editorMode": "code",
      "expr": "1-up",
      "hide": false,
      "interval": "60s",
      "legendFormat": "{{ instance }}",
      "range": true,
      "refId": "B"
    }
  ]
}
"""
def test_data(mocker):
    content = json.loads(json_str)
    format = 'time_series'
    panel = json.loads(panel_str)
 
    dataRes = dataresults( 
        type=datasource_type,
        format=format,
        results=content,
        version=api_version,
        panel=panel)
    snapshotData = dataRes.get_snapshotData(None)
    # mock_data = mocker.patch("grafana_snapshots.")