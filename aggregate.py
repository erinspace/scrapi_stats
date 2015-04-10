from __future__ import division

import json
import argparse
import requests

import numpy as np
import matplotlib.pyplot as plt

# Local settings
OSF_APP_URL = 'http://localhost:5000/api/v1/share/search/?raw=True'

# share-dev settings
# OSF_APP_URL = 'https://osf.io/api/v1/share/search/?raw=True'


def query_osf(query):
    response = requests.post(OSF_APP_URL, json=query, verify=False)
    return response.json()


def search(aggs):
    query = {
        'size': 0,
        'aggs': aggs
    }
    osf_query = query_osf(query)
    return osf_query


def missing_agg_query(terms):
    return {
        "{}MissingAggregation".format(term): {
            "filter": {
                "missing": {"field": term}
            },

            "aggs": {
                "sources": {
                    "terms": {"field": "source"}
                }
            }
        } for term in terms
    }


def includes_agg_query(terms):
    return {
        "{}NotMissingAggregation".format(term): {
            "filter": {
                "not": {
                    "missing": {"field": term}
                }
            },

            "aggs": {
                "sources": {
                    "terms": {"field": "source"}
                }
            }
        } for term in terms
    }


def terms_agg_query(terms, size):
    return {
        "{}TermFilter".format(term): {
            "terms": {
                "field": term,
                "size": size,
                "exclude": "of|and|or"
            }
        } for term in terms
    }


def full_results_to_list(full_elastic_results):
    ''' takes the raw elastic search results, and
    returns a simplified version with just a list of
    all the doc counts and their values '''
    try:
        return full_elastic_results['aggregations']['sources']['buckets']
    except KeyError:
        return full_elastic_results['aggregations']['sourceAggregation']['sources']['buckets']


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

    return values, labels


def create_pie_chart(elastic_results, title, field_for_title=''):
    ''' takes a list of elastic results, and
    returns a bar graph of the doc counts.
    Looks very messy at the moment - need to fix labels'''

    simplified_elastic_results = full_results_to_list(elastic_results)
    values, labels = extract_values_and_labels(simplified_elastic_results)

    plt.pie(values, labels=labels)
    plt.title(title + field_for_title)
    plt.show()


def create_bar_graph(elastic_results,  x_label, title, field_for_title=''):
    ''' takes a list of elastic results, and
    returns a bar graph of the doc counts'''
    simplified_elastic_results = full_results_to_list(elastic_results)
    values, labels = extract_values_and_labels(simplified_elastic_results)

    index = np.arange(len(values))
    width = 0.35

    plt.bar(index, values)

    plt.xticks(index + width / 2, labels, rotation='vertical')
    plt.xlabel(x_label)
    plt.ylabel('Document Count')
    plt.title(title + field_for_title)
    plt.show()


def parse_args():
    parser = argparse.ArgumentParser(description="A command line interface for getting numbers of SHARE sources missing given terms")

    parser.add_argument('-m', '--missing', dest='missing', type=str, help='The terms to aggregate with, to find sources with terms missing', nargs='+')
    parser.add_argument('-t', '--terms', dest='terms', type=str, help='The top unique entries with given terms. Use with size to control number of results shown.', nargs='+')
    parser.add_argument('-s', '--size', dest='size', type=int, help='The number of results to return per aggretation', default=0)
    parser.add_argument('-i', '--includes', dest='includes', type=str, help='The terms to aggregate with, to find sources with terms included', nargs='+')
    parser.add_argument('-b', '--bargraph', dest='bargraph', help='A flag to signal to draw a bar graph', action='store_true')
    parser.add_argument('-p', '--piegraph', dest='piegraph', help='A flag to signal to draw a pie graph', action='store_true')

    return parser.parse_args()


def main():
    args = parse_args()
    aggs = {}
    if args.missing:
        aggs.update(missing_agg_query(args.missing))
    if args.terms:
        aggs.update(terms_agg_query(args.terms, args.size))
    if args.includes:
        aggs.update(includes_agg_query(args.includes))

    results = search(aggs)

    if args.bargraph:
        create_bar_graph(results, 'terms', 'SHARE Results')
    if args.piegraph:
        create_pie_chart(results, 'SHARE Results')
    else:
        print(json.dumps(results, indent=4))


if __name__ == '__main__':
    main()
