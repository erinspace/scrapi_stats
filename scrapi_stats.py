
# coding: utf-8

# In[1]:

import copy
import json
import logging
import requests
import datetime


# In[2]:

OSF_APP_URL = 'https://share-dev.osf.io/api/v1/app/6qajn/'
OSF_AUTH = ('scrapi_stats','543edf86b5e9d7579327c710eb1d94ee-d8da-472a-84bb-ba6b96499c80')


# In[3]:

DEFAULT_PARAMS = {
    'q': '*',
    'start_date': None,
    'end_date': datetime.date.today().isoformat(),
    'sort_field': 'dateUpdated',
    'sort_type': 'desc',
    'from': 0,
    'size': 10,
    'format': 'json'
}


# In[4]:

def query_osf(query):
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(query)
#     import pdb; pdb.set_trace()
    print(data)
    return requests.post(OSF_APP_URL, auth=OSF_AUTH, headers=headers, data=data, verify=False).json()


# In[5]:

def search(raw_params):
    params = copy.deepcopy(DEFAULT_PARAMS)
    params.update(raw_params)
    for key in params.keys():
        if isinstance(params[key], list) and len(params[key]) == 1:
            params[key] = params[key][0]
    params['from'] = int(params['from'])
    params['size'] = int(params['size'])
    print params
    query = parse_query(params)
    query['format'] = params.get('format')
    return query_osf(query)


# In[6]:

def parse_query(params):
    return {
        'query': build_query(
            params.get('q'),
            params.get('start_date'),
            params.get('end_date')
        ),
        'sort': build_sort(params.get('sort_field'), params.get('sort_type')),
        'from': params.get('from'),
        'size': params.get('size'),
    }


# In[7]:

def build_query(q, start_date, end_date):
    return {
        'filtered': {
             'query': build_query_string(q),
             'filter': build_date_filter(start_date, end_date),
        }
    }


# In[8]:

def build_query_string(q):
    return {
        'query_string': {
            'default_field': '_all',
            'query': q,
            'analyze_wildcard': True,
            'lenient': True  # TODO, may not want to do this
        }
    }


# In[9]:

def build_date_filter(start_date, end_date):
    return {
        'range': {
            'consumeFinished': {
                'gte': start_date,  # TODO, can be None, elasticsearch may not like it
                'lte': end_date
            }
        }
    }


# In[10]:

def build_sort(sort_field, sort_type):
    print sort_field
    return [{
        sort_field : {
            'order': sort_type
        }
    }]


# In[13]:

all_results = search({'size': 1000})


# In[11]:
import pdb; pdb.set_trace()

# print(results)

# In[11]:



