#!/usr/bin/python3
# -*- coding: utf-8 -*-
#***************************************************
from .resultsBase import resultsBase
from typing import Union

#***************************************************
class resultsFrame(resultsBase):
    """
    response contains a result with frames:
    e.g. Prometheus with Grafana server 9.x

    ## Response
    "response": {
        "results": {
            "[refId]": {
                "frames": [
                    "{frame_1}",
                    "{... frame_X ...}",
                ],
                "refId": "[refId]"
            }
        }
    }

    ## definitions:
    frame: {
        "schema": {
            "refId": "[val]"
            "meta" :{
                "type": ...,
                "executedQueryString": "expr...",
                "step": "[step value]",
                "custom": {
                    "resultType": "matrix",
                }
            },
            // one object by timeseries
            "fields": [
                //0: timestamp part
                {
                    "name": "Time",
                    "type": "time",
                    "typeInfo": {...},
                    "config": {
                        "interval": <val>
                    }

                },
                //1: value part
                {
                    "name": "Value",
                    "type": "number",
                    "typeInfo": {...},
                    "config": {
                        "displayNameFromDS": <val: localhost:9090>
                    },
                    "labels": {
                        "__name__":"up",
                        "instance": "localhost:9090",
                        "job": "prometheus",
                    }

                }

            ]
        },
        "data": {
            "values": [
                // 0: timestamp
                [
                    ts1,
                    ts2,
                    ...
                ],
                // 1: values
                [
                    val1,
                    val2,
                    ...
                ]
            ]
        }
    }
    """

    #***********************************************
    def get_snapshotData(self, targets: Union[list, dict])-> list:
        snapshotData = list()
        snapshotDataObj = {}
        (ts_part, value_part, ref_id) = ( None, None, None)

        if not self.results or 'results' not in self.results \
            or len(self.results['results']) <= 0:
            return snapshotData

        if targets is None:
            targets = []
        if isinstance(targets, dict):
            targets = [ targets ]

        # required format is time_series:
        if self.format == 'time_series':
            for refid_key, refId in self.results['results'].items():

                #* the result contains an error
                if 'error' in refId:
                    return snapshotData

                # loop on each timeseries received from the frame
                for frame in refId['frames']:
                    snapshotDataObj = {}
                    name = None
                    if len(frame['data']['values']) < 1:
                        break

                    ts = frame['data']['values'][0]
                    values = frame['data']['values'][1]

                    (ts_part, value_part) = self.panel.get_FieldsConfig(frame, None, values=values)
                    #** build timestamp list
                    ts_part.update( {
                        'name': 'Time',
                        'type': 'time',
                        'values': ts
                    })

                    values_info = frame['schema']['fields'][1]

                    value_part.update( {
                        'labels': values_info['labels'],
                        'name': values_info['name'],
                        'type': values_info['type'],
                        'values': values
                    } )
                    # extract metric name from the result frame
                    if 'config' in values_info and 'displayNameFromDS' in values_info['config']:
                        name = values_info['config']['displayNameFromDS']
                        value_part['config']['displayNameFromDS'] = name
                    else:
                        value_part['config']['displayNameFromDS'] = self.buildLegend(values_info["labels"])

                    #** build snapshotDataObj for the current timeseries
                    if ts_part is not None and value_part is not None:
                        snapshotDataObj['fields']=[ ts_part, value_part]
                        if 'meta' in frame['schema']:
                            snapshotDataObj['meta'] = frame['schema']['meta']
                            snapshotDataObj['meta']['preferredVisualisationType'] = 'graph'

                        # snapshotDataObj['name'] = name
                        if name is not None:
                            snapshotDataObj['name'] = name
                        # snapshotDataObj['refId'] = target['refId']
                        snapshotDataObj['refId'] = refid_key

                    self.panel.set_overrides( snapshotDataObj )
                    snapshotData.append( snapshotDataObj )

        # format is table : received results are same than for time_series
        # but they must be formatted differently :
        # each frame represents a data line
        # one line has columns which are timestamp, [ labels_values ], values
        elif self.format == 'table':
            for refid_key, refId in self.results['results'].items():
                snapshotDataObj = {}
                fields_names = {}
                # for idx, frame in refId['frames'].items():
                #     names = [
                #         frame['schema']['fields'][0]['name']: ,
                #         frame['schema']['fields'][1]['name'],
                #     ]
                #     if 'labels' in frame['schema']['fields'][1]:
                #         names.extend( frame['schema']['fields'][1]['labels'].keys() )
                #     for name in names:
                #         if name not in fields_names:
                #             fields_names[name]={ 'index': idx, 'values': [], }

                # loop on each timeseries received from the frame
                meta = None
                for frame in refId['frames']:
                    if len(frame['schema']['fields']) > 0:
                        if ts_part is None:
                            ts_part = { 
                                'name': frame['schema']['fields'][0]['name'],
                                'type': frame['schema']['fields'][0]['type'],
                                'values': [],
                            }
                            if 'meta' in frame['schema']:
                                meta = frame['schema']['meta']
                                meta.pop('step', None)
                                # found 
                                # old: "table"
                                # for resultFrame from Prometheus: "rawPrometheus" 
                                # maybe value mus be adapt upon datasource
                                meta['preferredVisualisationType'] = 'rawPrometheus'
                        if value_part is None:
                            value_part = { 
                                'name': frame['schema']['fields'][1]['name'],
                                'type': frame['schema']['fields'][1]['type'],
                                'values': [],
                            }

                        if 'labels' in frame['schema']['fields'][1]:
                            for label in frame['schema']['fields'][1]['labels'].keys():
                                if label not in fields_names:
                                    fields_names.update( {
                                        label: { 
                                            'name': label,
                                            'type': 'string',
                                            'values': [],
                                        }
                                    })
                if ts_part is not None and value_part is not None:
                    for frame in refId['frames']:
                        # add timestamp value
                        ts_part['values'].extend(frame['data']['values'][0])
                        # add Value value
                        value_part['values'].extend(frame['data']['values'][1])

                        # add values for each labels
                        labels = []
                        value_length = len(frame['data']['values'][1])
                        if 'labels' in frame['schema']['fields'][1]:
                            labels = frame['schema']['fields'][1]['labels']
                        for field_name, field in fields_names.items():
                            value = ''
                            # label found for this serie
                            if field_name in labels:
                                value = [labels[field_name]] * value_length
                            # label not found for this serie add ""
                            else:
                                value = [""] * value_length
                            field['values'].extend(value)


                    # build list of fields to extend with default schema elements
                    # order is timestamp, labels, then values
                    # ts = frame['data']['values'][0]
                    fields = [
                        { 'type': 'timestamp', 'value': ts_part },
                    ]

                    for _, field in fields_names.items():
                        fields.append( {'type': 'timestamp', 'value': field} )

                    # values = frame['data']['values'][1]
                    fields.append( { 'type': 'value', 'value': value_part } )

                    snapshotDataObj['fields'] = self.panel.get_FieldsConfig(frame, None, fields=fields, format="table")
                    snapshotDataObj['meta'] = meta

                    # snapshotDataObj['refId'] = target['refId']
                    snapshotDataObj['refId'] = refid_key

                    self.panel.set_overrides( snapshotDataObj )
                    snapshotData.append( snapshotDataObj )
                    #** build timestamp list
                        # ts_part.update( {
                        #     'name': 'Time',
                        #     'type': 'time',
                        #     'values': ts
                        # })

                        # values_info = frame['schema']['fields'][1]

                        # value_part.update( {
                        #     'labels': values_info['labels'],
                        #     'name': values_info['name'],
                        #     'type': values_info['type'],
                        #     'values': values
                        # } )

        snapshotData = self.panel.set_transformations( snapshotData )

        return snapshotData

#***************************************************
