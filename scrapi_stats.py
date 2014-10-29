
# coding: utf-8

# #SHARE Results
# ----
# Here are some working examples of how to query the current scrAPI database for metrics of results coming through the SHARE Notifiation Service.
# 
# These particular queries are just examples, and the data is open for anyone to use, so feel free to make your own and experiment!
# 
# ----
# 

# ### Service Names for Reference
# ----
# Each provider harvested from uses a shortened name for its source. Here's a guide to which short names refer to which services
# 

# <table>
#     <tr>
#         <td> arxiv_oai </td>
#         <td> ArXiv </td>
#     </tr>
#     <tr>
#         <td> calpoly </td>
#         <td> Digital Commons at Cal Poly </td>
#     </tr>
#     <tr>
#         <td> clinicaltrials </td>
#         <td> ClinicalTrials.gov </td>
#     </tr>    
#     <tr>
#         <td> crossref </td>
#         <td> CrossRef </td>
#     </tr>
#     <tr>
#         <td> doepages </td>
#         <td> Department of Energy Pages </td>
#     </tr>
# 
#     <tr>
#         <td> cmu </td>
#         <td> Carnegie Mellon University Research Showcase </td>
#     </tr>
#     <tr>
#         <td> columbia  </td>
#         <td> Columbia Adacemic Commons </td>
#     </tr>
#     <tr>
#         <td> dataone </td>
#         <td> DataONE: Data Observation Network for Earth </td>
#     </tr>
#     <tr>
#         <td> mit </td>
#         <td> DSpace@MIT </td>
#     </tr>
#     <tr>
#         <td> opensiuc </td>
#         <td> OpenSIUC at the Southern Illinois University Carbondale </td>
#     </tr>
#     <tr>
#         <td> plos </td>
#         <td> Public Library Of Science </td>
#     </tr>
#     <tr>
#         <td> scitech </td>
#         <td> SciTech Connect </td>
#     </tr>
#     <tr>
#         <td> stcloud </td>
#         <td> theRepository at St. Cloud State </td>
#     </tr>
#     <tr>
#         <td> uceschol </td>
#         <td> California Digital Library eScholarship System </td>
#     </tr>
#     <tr>
#         <td> uiucideals </td>
#         <td> University of Illinois at Urbana-Champaign Illinois Digital Enviornment for Access to Learning and Scholarship </td>
#     </tr>
#     <tr>
#         <td> upenn </td>
#         <td> University of Pennsylvania Scholarly Commons </td>
#     </tr>
#     <tr>
#         <td> utaustin </td>
#         <td> University of Texas Digital Repository </td>
#     </tr>
#     <tr>
#         <td> uwdspace </td>
#         <td> ResearchWorks at the University of Washington </td>
#     </tr>
#     <tr>
#         <td> vtechworks </td>
#         <td> Virginia Tech VTechWorks </td>
#     </tr>
#     <tr>
#         <td> wayne </td>
#         <td> DigitalCommons@WayneState </td>
#     </tr>
#     
# </table>

# ##Setup: 

# In[125]:

import json
import requests

import numpy as np
import matplotlib.pyplot as plt

get_ipython().magic(u'matplotlib inline')


# In[126]:

# SHARE-dev settings
# OSF_APP_URL = 'http://share-dev.osf.io/api/v1/app/6qajn/?return_raw=True'


# In[127]:

# Localhost settings - for testing
OSF_APP_URL = 'http://localhost:5000/api/v1/app/kb7ae/?return_raw=True'


# ## Query Setup

# In[128]:

def query_osf(query):
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(query)
    return requests.post(OSF_APP_URL, headers=headers, data=data, verify=False).json()


# In[129]:

def search(agg_type, field=None, all_results=True, exclude_terms=False):
    if agg_type == 'field':
        query = field_aggregation_query(field, all_results)
    elif agg_type == 'missing':
        query = source_missing_query(field)
    elif agg_type == 'common_properties':
        query = common_properties_query()
    else: 
        print("Not a valid agg query!")
        return None
    return query_osf(query)


# In[130]:

def field_aggregation_query(field, all_results):
    ''' Use this basic aggregation query to find all
    of the results from a particular field. Perhaps
    best used for sources or tag counts '''
    
    return {
        "size" : 0,
        "aggs": {
            "sources" : {
                "terms" : {
                    "field": field, 
                    "size" : return_all(all_results),
                    "exclude" : "of|and|or"
                }
            }
        }
    }


# In[131]:

def source_missing_query(missing_field):
    ''' Use this query to find how many documents from 
    a particular source are missing an entry for any field '''
    
    return {
        "size": 0,
            "aggs": {
            "sourceAggregation": {
                "filter" : {
                    "missing" : {"field" : missing_field}
                },
                "aggs" : {
                    "sources" : {
                        "terms" : {
                            "field": "source",
                            "size": 0
                        }
                    }
                }
            }
        }
    }


# In[132]:

def common_properties_query():
    ''' This is totally wrong - try again with examples
    from: https://github.com/elasticsearch/elasticsearch/issues/5789
    and http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/mapping-field-names-field.html#mapping-field-names-field
    '''
    return {
        "size": 0,
        "aggs": {
            "properties": {
                "nested": {
                    "path": "properties"
                },
            "aggs": {
                "key": {
                    "terms": {
                        "field": "properties.key"
                    },
                    "aggs": {
                        "value": {
                            "terms": {
                                "field": "properties.value"
                            }
                        }
                    }
                }
            }}
        }
    }


# In[133]:

def return_all(all_results):
    ''' used to determine if you want 
    to show all of the results, or just 
    the top 10 '''
    
    if all_results:
        return 0
    else:
        return 10
    


# ## Query Cleanup

# In[134]:

def full_results_to_list(full_elastic_results):
    ''' takes the raw elastic search results, and 
    returns a simplified version with just a list of 
    all the doc counts and their values '''
    
    try:
        return full_elastic_results['aggregations']['sources']['buckets']
    except KeyError:
        return full_elastic_results['aggregations']['sourceAggregation']['sources']['buckets']


# In[135]:

def extract_values_and_labels(elastic_results):
    ''' Takes a list of dictionaries of the results of
    an elasticsearch aggregation, and converts them into
    two lists - of values, and labels - to be used in 
    plotting later.
    
    Returns a dictionary with the lists of values and labels
    '''
    labels = []
    values = []
    for item in elastic_results:
        labels.append(item['key'])
        values.append(item['doc_count'])
    
    return {'values': values, 'labels':labels}


# ## Functions for Making Graphs!

# In[136]:

def create_bar_graph(elastic_results,  x_label, title, field_for_title=''):
    ''' takes a list of elastic results, and 
    returns a bar graph of the doc counts'''
    
    values_labels = extract_values_and_labels(elastic_results)
    values = values_labels['values']
    labels = values_labels['labels']
    
    length = len(values)
    index = np.arange(len(values))
    width = 0.35 
    
    bar = plt.bar(index, values)
    
    plt.xticks(index+width/2, labels, rotation='vertical')
    plt.xlabel(x_label)
    plt.ylabel('Document Count')
    plt.title(title + field_for_title)


# In[137]:

def create_pie_chart(elastic_results, title, field_for_title=''):
    ''' takes a list of elastic results, and 
    returns a bar graph of the doc counts.
    Looks very messy at the moment - need to fix labels'''
    
    values_labels = extract_values_and_labels(elastic_results)
    values = values_labels['values']
    labels = values_labels['labels']
    
    pie = plt.pie(values, labels=labels)
    plt.title(title + field_for_title)


# ## Exploring the SHARE Data

# ###Documents per source
# ----
# Here are some examples of how to use the above queries to get the number of documents returned by each source

# In[138]:

source_stats_search = search(agg_type='field', field='source')


# In[139]:

source_statistics = full_results_to_list(source_stats_search)


# In[140]:

# print(json.dumps(source_statistics, indent=4))


# In[141]:

create_bar_graph(source_statistics, title="Documents Per Source", x_label='Source')


# In[142]:

''' The labels on this need some serious fixing!!
'''

create_pie_chart(source_statistics, "Documents Per Source")


# ### Number of missing fields per source
# ----
# These queries will find the sources that are missing a certain field. 
# The two examples we'll give here are title and email 

# In[143]:

missing_by_title_search = search('missing', field='title')


# In[144]:

missing_by_title = full_results_to_list(missing_by_title_search)


# In[145]:

print(json.dumps(missing_by_title, indent=4))


# In[146]:

create_bar_graph(missing_by_title, title="Documents Missing the Field: ", field_for_title='Title', x_label="Source")


# In[147]:

missing_by_email_search = search('missing', field='email')


# In[148]:

missing_by_email = full_results_to_list(missing_by_email_search)


# In[149]:

# print(json.dumps(missing_by_email, indent=4))


# In[150]:

create_bar_graph(missing_by_email, title="Documents Missing the Field: ", field_for_title='Email', x_label="Source")


# ##Most Popular Tags in the dataset

# In[151]:

top_tags_search = search(agg_type='field', field='tags', all_results=False)


# In[152]:

top_tags = full_results_to_list(top_tags_search)


# In[153]:

# print(json.dumps(top_tags, indent=4))


# In[154]:

create_bar_graph(top_tags, title="Most Frequent Tags", x_label="Tag")


# ## Testing Area

# Testing out getting intersection of properties across all documents

# In[155]:

search('common_properties')


# In[ ]:



