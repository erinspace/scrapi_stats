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

DEFAULT_REQUEST_PARAMS = {
    'return_raw': False
}

# Local settings
# OSF_APP_URL = 'http://localhost:5000/api/v1/app/kb7ae/?return_raw=True'
# OSF_AUTH = ('scrapi', '54331d5a669aec8577089ad1e4b9dcb3-50f3-4828-9232-d85512a999e7')

# share-dev settings
OSF_APP_URL = 'https://share-dev.osf.io/api/v1/app/6qajn/?return_raw=True'
OSF_AUTH = ('scrapi_stats','543edf86b5e9d7579327c710eb1d94ee-d8da-472a-84bb-ba6b96499c80')

def query_osf(query):
    headers = {'Content-Type': 'application/json'}
    return requests.post(OSF_APP_URL, auth=OSF_AUTH, headers=headers, data=data, verify=False).json()

def search(request_params, raw_query_params):
    query = nested_agg_query()
    osf_query = query_osf(query)
    return osf_query

def simple_agg_query():
    return {
        "size" : 0,
        "aggs": {
            "sources" : {
                "terms" : {"field": "source"}
            }
        }
    }

def nested_agg_query():
    return {
        "size" : 0,
        "aggs": {
            "sourceAggregation": {
                "filter" : {
                    "missing" : {"field" : "prefix"}
                },

                "aggs" : {
                    "sources" : {
                        "terms" : {"field": "source"}
                    }
                }
            }

        }
    }




search_osf = search(request_params={'return_raw': True}, raw_query_params={})

print(json.dumps(search_osf, indent=4))

