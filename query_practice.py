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

# Local settings
OSF_APP_URL = 'http://localhost:5000/api/v1/app/kb7ae/agg/'
OSF_AUTH = ('scrapi', '54331d5a669aec8577089ad1e4b9dcb3-50f3-4828-9232-d85512a999e7')

# share-dev settings
# OSF_APP_URL = 'https://share-dev.osf.io/api/v1/app/6qajn/'
# OSF_AUTH = ('scrapi_stats','543edf86b5e9d7579327c710eb1d94ee-d8da-472a-84bb-ba6b96499c80')

def query_osf(query):
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(query, indent=4)
    print(data)
    return requests.post(OSF_APP_URL, auth=OSF_AUTH, headers=headers, data=data, verify=False).json()


def search(raw_params):
    params = copy.deepcopy(DEFAULT_PARAMS)
    params.update(raw_params)
    for key in params.keys():
        if isinstance(params[key], list) and len(params[key]) == 1:
            params[key] = params[key][0]
    params['from'] = int(params['from'])
    params['size'] = int(params['size'])
    # print(params)
    # query = parse_query(params)
    query = create_test_agg_query()
    query['format'] = params.get('format')
    osf_query = query_osf(query)
    # import pdb; pdb.set_trace()
    return osf_query



def create_test_agg_query():
    return {
        "size" : 0,
        "aggs": {
            "sourceAggregation": {
                "filter" : {
                    "missing" : {"field" : "title"}
                },

                "aggs" : {
                    "sources" : {
                        "terms" : {"field": "source"}
                    }
                }
            }

        }
    }


search_osf = search({})

print(json.dumps(search_osf, indent=4))

# import pdb; pdb.set_trace()

