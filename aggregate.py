from __future__ import division

import json
import argparse
import requests

import numpy as np
import matplotlib.pyplot as plt

# Local settings
# OSF_APP_URL = 'http://localhost:5000/api/v1/share/search/?raw=True'

# production SHARE settings
OSF_APP_URL = 'https://osf.io/api/v1/share/search/?raw=True&v=1'


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
                "query": {
                    "query_string": {
                        "query": "NOT {}:*".format(term)
                    }
                }
            },
            "aggs": {
                "sources": {
                    "terms": {
                        "field": "source",
                        "min_doc_count": 0,
                        "size": 0
                    }
                }
            }
        } for term in terms
    }


def all_source_counts():
    return {
        "allSourceAgg": {
            "terms": {
                "field": "source",
                "min_doc_count": 0,
                "size": 0
            }
        }
    }


def includes_agg_query(terms):
    return {
        "{}NotMissingAggregation".format(term): {
            "filter": {
                "query": {
                    "query_string": {
                        "query": "{}:*".format(term)
                    }
                }
            },
            "aggs": {
                "sources": {
                    "terms": {
                        "field": "source",
                        "size": 0
                    }
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
                "exclude": "of|and|or",
                "size": size
            }
        } for term in terms
    }


def full_results_to_list(full_elastic_results, terms, agg_type):
    ''' takes the raw elastic search results, and
    returns a simplified version with just a list of
    all the doc counts and their values '''
    term = terms[0]

    agg_results = full_elastic_results['aggregations']['{}{}Aggregation'.format(term, agg_type)]['sources']['buckets']

    source_counts = {
        result['key']: result['doc_count']
        for result in full_elastic_results['aggregations']['allSourceAgg']['buckets']
    }

    return [{
        'key': result['key'],
        'percent': float(result['doc_count']) / source_counts[result['key']] * 100
    } for result in agg_results]


def extract_values_and_labels(elastic_results):
    ''' Takes a list of dictionaries of the results of
    an elasticsearch aggregation, and converts them into
    two lists - of values, and labels - to be used in
    plotting later.

    Returns a tuple with the lists of values and labels
    '''
    labels = []
    values = []
    for item in elastic_results:
        # import ipdb; ipdb.set_trace()
        labels.append(item['key'])
        values.append(item['percent'])

    return values, labels


def create_pie_chart(elastic_results, terms, agg_type, title):
    ''' takes a list of elastic results, and
    returns a bar graph of the doc counts.
    Looks very messy at the moment - need to fix labels'''

    source_percents = full_results_to_list(elastic_results, terms, agg_type)
    values, labels = extract_values_and_labels(source_percents)

    plt.pie(values, labels=labels)
    plt.title('{} {} {}'.format(title, agg_type, terms[0]))
    plt.show()


def create_bar_graph(elastic_results, terms, agg_type, x_label, title):
    ''' takes a list of elastic results, and
    returns a bar graph of the doc counts'''
    source_percents = full_results_to_list(elastic_results, terms, agg_type)
    values, labels = extract_values_and_labels(source_percents)

    index = np.arange(len(values))
    width = 0.35

    if agg_type == 'NotMissing':
        agg_type = 'Including'

    plt.bar(index, values)

    plt.xticks(index + width / 2, labels, rotation='vertical')
    plt.xlabel(x_label)
    plt.ylabel('Percent of Documents in Each Source')
    plt.title('{} {} {}'.format(title, agg_type, terms[0]))
    plt.show()

def create_bubble(results):
    tags = results['aggregations']['tagsTermFilter']['buckets']
    x = list(range(len(tags)))
    y, z = np.random.rand(2, len(tags))
    s = []
    for tag in tags:
        s.append(tag['doc_count'])

    fig, ax = plt.subplots()
    sc = ax.scatter(x, y, s=s, c=z)
    ax.grid()
    plt.show()

def parse_args():
    parser = argparse.ArgumentParser(description="A command line interface for getting numbers of SHARE sources missing given terms")

    parser.add_argument('-m', '--missing', dest='missing', type=str, help='The terms to aggregate with, to find sources with terms missing', nargs='+')
    parser.add_argument('-t', '--terms', dest='terms', type=str, help='The top unique entries with given terms. Use with size to control number of results shown.', nargs='+')
    parser.add_argument('-s', '--size', dest='size', type=int, help='The number of results to return per aggretation', default=0)
    parser.add_argument('-i', '--includes', dest='includes', type=str, help='The terms to aggregate with, to find sources with terms included', nargs='+')
    parser.add_argument('-b', '--bargraph', dest='bargraph', help='A flag to signal to draw a bar graph', action='store_true')
    parser.add_argument('-p', '--piegraph', dest='piegraph', help='A flag to signal to draw a pie graph', action='store_true')
    parser.add_argument('-bub', '--bubblechart', dest='bubblechart', help='A flag to signal to draw a bubblechart', action='store_true')

    return parser.parse_args()


def main():
    args = parse_args()
    aggs = all_source_counts()
    if args.missing:
        agg_type = 'Missing'
        aggs.update(missing_agg_query(args.missing))
    if args.terms:
        aggs.update(terms_agg_query(args.terms, args.size))
    if args.includes:
        agg_type = 'NotMissing'
        aggs.update(includes_agg_query(args.includes))

    results = search(aggs)

    print(json.dumps(results, indent=4))

    graph_variable = args.missing or args.includes

    if args.bargraph:
        create_bar_graph(elastic_results=results, terms=graph_variable, agg_type=agg_type, x_label='terms', title='SHARE Results')
    if args.piegraph:
        create_pie_chart(results, terms=graph_variable, agg_type=agg_type, title='SHARE Results')
    if args.bubblechart and 'tags' in args.terms:
        create_bubble(results)

if __name__ == '__main__':
    main()
