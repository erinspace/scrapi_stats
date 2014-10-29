import json
import requests

import operator
from collections import Counter
import numpy as np 
import matplotlib.pyplot as plt


with open('counts.json', 'r') as counts:
    property_fields = json.load(counts)

with open('data.json', 'r') as raw:
    raw_data = json.load(raw)


def large_dot_plot():
    fields = [] 
    num_sources = []
    count = []

    for field, info in property_fields.iteritems():
        fields.append(field)
        num_sources.append(len(info['sources']))
        count.append(info['count'])

    x_numbers = []
    for i, field in enumerate(fields):
        x_numbers.append(i)

    plt.scatter(x_numbers, num_sources, s=count)
    plt.show()


# large_dot_plot()

def top_fields():
    fields = [] 
    num_sources = []
    count = []

    aggregate = []

    for field, info in property_fields.iteritems():
        agg_dict = {}
        agg_dict['term'] = field
        agg_dict['count'] = info['count']
        agg_dict['sources'] = info['sources']
        agg_dict['num_sources'] = len(info['sources'])
        aggregate.append(agg_dict)


    sorted_list = sorted(aggregate, key=operator.itemgetter('num_sources'))

    top_ten = sorted_list[-10:]

    print('The top 10 fields are...')

    for item in top_ten:
        print('The field {} is in {} different providers').format(item['term'], item['num_sources'])


  # "issued": {
  #   "count": 15243,
  #   "sources": [
  #     "crossref"
  #   ]
  # },
def fields_from_raw():
    fields = {}
    for d in raw_data:
        if d.get('source'):
            for field in d.get('properties', {}).keys():
                if fields.get(field):
                    fields[field]['count'] +=1
                    fields[field]['sources'].add(d['source'])
                    fields[field]['all_sources'].append(d['source'])
                else:
                    fields[field] = {'count': 1, 'sources': set([d['source']]), 'all_sources': []}

    for field, value in fields.iteritems():
        value['sources_count'] = Counter(value['all_sources'])
        value['sources'] = list(value['sources'])
        del(value['sources'])
        del(value['all_sources'])

    print(json.dumps(fields, indent=4))



fields_from_raw()
 
top_fields()


# total_docs = 90729


### To Get fields!!! ##
## Do this on the osf!!
## use the shell! 
def get_fields_from_metadata():
    fields = {}
    for d in Metadata.find():
        if d.get('isResource'):
            for field in d.get('properties', {}).keys():
                if fields.get(field):
                    fields[field]['count'] +=1
                    fields[field]['sources'].add(d['source'])
                else:
                    fields[field] = {'count': 1, 'sources': set([d['source']])}


