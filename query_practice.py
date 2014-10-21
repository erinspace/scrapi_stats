from __future__ import division
import copy
import json
import logging
import requests
import datetime


DEFAULT_PARAMS = {
    'q': '*',
    'start_date': None,
    'end_date': datetime.date.today().isoformat(),
    'sort_field': 'dateUpdated',
    'sort_type': 'desc',
    'from': 0,
    'size': 10,
    'format': 'json',
    'empty_field': None,
    'agg': False
}

def query_osf(query):
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(query)
    print(data)
    return requests.post(OSF_APP_URL, auth=OSF_AUTH, headers=headers, data=data, verify=False).json()
