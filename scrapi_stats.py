
# coding: utf-8

# #SHARE Results
# ----
# Here are some working examples of how to query the current scrAPI database for metrics of results coming through the SHARE Notifiation Service.  
# 
# ----
# 

# ##Setup: 

# In[1]:

from __future__ import division
import copy
import json
import logging
import requests
import datetime

# Want to eventually use pandas!
# from pandas import DataFrame, Series


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
    'format': 'json',
    'empty_field': None,
    'agg': False
}


# ## Query Setup

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
    if params.get('agg'):
        return {
            'query': build_query(
                params.get('q'),
                params.get('start_date'),
                params.get('end_date'),
                params.get('empty_field'),
                params.get('agg')
                
            ),
            'sort': build_sort(params.get('sort_field'), params.get('sort_type')),
            'from': params.get('from'),
            'size': params.get('size'),
            
        }
    else:
        return {
            'query': build_query(
                params.get('q'),
                params.get('start_date'),
                params.get('end_date'),
                params.get('empty_field'),
                params.get('agg')
            ),
            'sort': build_sort(params.get('sort_field'), params.get('sort_type')),
            'from': params.get('from'),
            'size': params.get('size')
        }


# In[7]:

def build_query(q, start_date, end_date, empty_field, agg):
    if empty_field is not None and not agg:
        return {
            'filtered': {
                'query': build_query_string(q),
                'filter': {
                    'bool': {
                        'must': [
                            build_date_filter(start_date, end_date),
                        ],
                        'must_not' : [
                            build_empty_filter(empty_field)
                        ]
                    }
                }
            },
            'aggs': build_aggregation('empty_field'),
    else:
        }
        return {
            'filtered': {
                'query': build_query_string(q),
                'filter': build_date_filter(start_date, end_date)
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

def build_empty_filter(empty_field):
    return {
        'exists' : {
            'field': empty_field
        }
    }


# In[11]:

def build_sort(sort_field, sort_type):
    print sort_field
    return [{
        sort_field : {
            'order': sort_type
        }
    }]


# For the aggregations section a little later...

# In[ ]:

def build_aggregation(empty_field):
    return build_missing_aggregation(empty_field)


# In[ ]:

def build_missing_aggregation(empty_field):
    return {
        "results_with_missing_fields": {
            "terms": {"field": "source"}
    }
}


# Now we can get the Total Number of results for later calculation of percentage stats

# In[12]:

all_results = search({})


# In[13]:

total_results = all_results['total']


# In[14]:

total_results


# Create a large dictionary from all results

# #Building Metrics for Results with Filters

# Here are some ways we can query elasticsearch to gather some metrics, and see which fields are missing in the data we've collected so far. 

# ##DOI

# In[15]:

# Find all results without a DOI
results_no_doi = search({'empty_field': 'doi'})


# In[ ]:

total_no_doi = results_no_doi['total']


# ####Percentage of all results with no DOI

# In[ ]:

(total_no_doi/total_results)*100


# DOI per source

# In[ ]:

source_total = search({'q': 'source:dataone'})


# In[ ]:

source_total_num = source_total['total']


# In[ ]:

source_no_doi = search({'q': 'source:dataone', 'empty_field': 'doi'})


# In[ ]:

source_no_doi_num = source_no_doi['total']


# Percentage of source with no DOI

# In[ ]:

(source_total_num/source_no_doi_num)*100


# ##Title

# In[ ]:

# Find all results without a title
results_no_title = search({'empty_field': 'title'})


# In[ ]:

total_no_title = results_no_title['total']


# ####Percentage of results with no Title

# In[ ]:

(total_no_title/total_results)*100


# In[ ]:

source_no_title = search({'q': 'source:dataone', 'empty_field': 'title'})


# In[ ]:

source_no_title['total']


# ### Filter Aggregation

# Instead of adding filters to the queries, it looks like we can instead do some aggregations instead. 

# In[ ]:

agg_search = search({'q': '*', 'agg': True, 'empty_field': 'title', 'size':6000})


# In[ ]:

agg_search.keys()


# In[ ]:

agg_search['results']


# In[ ]:



