from __future__ import division
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


def fields_from_raw():
    fields = {}
    fields['all_source_count_list'] = []
    for d in raw_data:
        if d.get('source'):
            fields['all_source_count_list'].append(d['source'])
            for field in d.get('properties', {}).keys():
                if fields.get(field):
                    fields[field]['count'] +=1
                    fields[field]['sources'].add(d['source'])
                    fields[field]['all_sources'].append(d['source'])
                else:
                    fields[field] = {'count': 1, 'sources': set([d['source']]), 'all_sources': []}

    fields['all_source_count'] = Counter(fields['all_source_count_list'])
    del fields['all_source_count_list']

    for field, value in fields.iteritems():
        if field != 'all_source_count':
            value['sources_count'] = Counter(value['all_sources'])

            # value['count'] -=1
            # del(value['sources'])
            del(value['all_sources'])

            value['source_percent'] = {}
            value['percent_field_with_source'] = {}
            for source, number in value['sources_count'].iteritems():
                value['source_percent'][source] = round((number/value['count'])*100)
                # value['source_percent'][source] = '{}/{}'.format(number, value['count'])
                value['percent_field_with_source'][source] = round((number/fields['all_source_count'][source])*100)
                # value['percent_field_with_source'][source] = '{}/{}'.format(number, fields['all_source_count'][source])

    for field, value in fields.iteritems():
        for key, item in value.iteritems():
            if key == 'percent_field_with_source':
                print(json.dumps(item, indent=4))


fields_from_raw()
 
top_fields()

large_dot_plot()

