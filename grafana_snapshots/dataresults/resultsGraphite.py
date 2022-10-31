#!/usr/bin/python3
# -*- coding: utf-8 -*-
#***************************************************
from .resultsBase import resultsBase
from typing import Union

#***************************************************
class resultsGraphite(resultsBase):
    """
    response contains an array of results:
    e.g.: Graphite
    "response": [
        {
            "target": "<query...>",
            "datapoints": [
                [ <values>, timestamp ],
                [ ... ]
            ]
        }
    ]
    """

    #***********************************************
    def get_snapshotData(self, targets: Union[list, dict])-> list:
        snapshotData = list()
        snapshotDataObj = {}
        (ts_part, value_part, ref_id) = ( None, None, None)

        if not self.results or not isinstance(self.results, list) \
            or len(self.results) <= 0:
            return snapshotData

        if targets is None:
            targets = []
        if isinstance(targets, dict):
            targets = [ targets ]

        # required format is time_series:

        # loop on each timeseries received from the response
        for data_target in self.results:

            #*** split list of [ (ts,val),...] from values into 2 lists of (ts, tsx,...) (val, valx,...)
            ts=list()
            values=list()

            for value_pair in data_target['datapoints']:
                if self.debug:
                    print('ts={0} - val={1}'.format(value_pair[0], value_pair[1]))
                value = value_pair[0]
                if value is None or value == 'NaN':
                    value = None
                else:
                    value = float( value )
                values.append(value)

                ts.append(int(value_pair[1]))

            (ts_part, value_part) = self.panel.get_FieldsConfig(data_target, values=values)
            #** build timestamp list
            ts_part.update( {
                'name': 'Time',
                'type': 'time',
                'values': ts
            })

            #** build value part...
            value_part.update( {
                'name': 'Value',
                'type': 'number',
                'values': values
            } )
            name = data_target['target']

            #** build snapshotDataObj
            if ts_part is not None and value_part is not None:
                snapshotDataObj['fields']=[ ts_part, value_part]
                snapshotDataObj['name'] = name

                self.panel.set_overrides( snapshotDataObj )
                snapshotData.append( snapshotDataObj )


        snapshotData = self.panel.set_transformations( snapshotData )

        return snapshotData

#***************************************************
