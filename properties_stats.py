from __future__ import division

import json
import operator
import requests
import numpy as np 
from collections import Counter
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


def fields_from_raw(percents=True):
    ''' percents is used later on to determine the output of the  function. 
    If True, it returns a percentage from that source that have each field. 
    If False, it returns the raw numbers 
    '''

    fields = {}
    fields['all_source_count_list'] = []
    for d in raw_data:
        # This ensures it's a report and not a resource
        if d.get('source'):
            fields['all_source_count_list'].append(d['source'])
            for field in d.get('properties', {}).keys():
                if fields.get(field) and fields.get(field) != '':
                    fields[field]['count'] += 1
                    fields[field]['sources'].add(d['source'])
                    fields[field]['all_sources'].append(d['source'])
                else:
                    fields[field] = {'count': 1, 'sources': set([d['source']]), 'all_sources': []}

    '''
    fields is a dict with keys that are each of the field names found in properties
    fields has one key that is special - all_sources_count, that is a record
    of every time the field ever appears
    Each field value is a dict, with the keys count, sources, and all_sources.
    - count is an int, and is the number of times that field appears
    - sources is a set, and is just the sources that have that field
    - all_sources is a cumultive list of every time that field appeared
    '''

    fields['all_source_count'] = Counter(fields['all_source_count_list'])
    import pdb; pdb.set_trace()
    del fields['all_source_count_list']

    for field, value in fields.iteritems():
        if field != 'all_source_count':
            value['sources_count'] = Counter(value['all_sources'])

            del(value['all_sources'])

            value['source_percent'] = {}
            value['percent_field_with_source'] = {}
            for source, number in value['sources_count'].iteritems():
                if percents:
                    value['source_percent'][source] = round((number/value['count'], 2)*100)
                    value['percent_field_with_source'][source] = round((number/fields['all_source_count'][source], 2)*100)
                else: 
                    value['source_percent'][source] = '{}/{}'.format(number, value['count'])
                    value['percent_field_with_source'][source] = '{}/{}'.format(number, fields['all_source_count'][source])

    field_source_percents = {}
    for field, value in fields.iteritems():
        for key, item in value.iteritems():
            if key == 'percent_field_with_source':
                # print(json.dumps(item, indent=4))
                field_source_percents[field] = item

    return field_source_percents

def fields_data():
    source_percents = fields_from_raw(percents=False)

    print(json.dumps(source_percents, indent=4))

fields_data()

# fields_from_raw()
 
# top_fields()

# large_dot_plot()

