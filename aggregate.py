from __future__ import division

import json
import argparse
import requests
from datetime import date

import numpy as np
import matplotlib.pyplot as plt

# Local settings
# OSF_APP_URL = 'http://localhost:5000/api/v1/share/search/?raw=True'

# production SHARE settings
OSF_APP_URL = 'https://osf.io/api/v1/share/search/?raw=True&v={}'


FRONTEND_KEYS = [
    "uris",
    "contributors",
    "providerUpdatedDateTime",
    "description",
    "title",
    "freeToRead",
    "languages",
    "licenses",
    "publisher",
    "subjects",
    "tags",
    "sponsorships",
    "otherProperties",
    "shareProperties"
]


def query_osf(url, query):
    response = requests.post(url, json=query, verify=False)
    return response.json()


def search(url, aggs):
    query = {
        'size': 0,
        'aggs': aggs
    }

    osf_query = query_osf(url, query)
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
        "{}IncludedAggregation".format(term): {
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

    source_counts = {
        result['key']: result['doc_count']
        for result in full_elastic_results['aggregations']['allSourceAgg']['buckets']
    }

    if agg_type == 'Term':
        agg_results = full_elastic_results['aggregations']['{}{}Filter'.format(term, agg_type)]['buckets']
        return [{
            'key': result['key'],
            'value': float(result['doc_count'])
        } for result in agg_results]

    else:
        agg_results = full_elastic_results['aggregations']['{}{}Aggregation'.format(term, agg_type)]['sources']['buckets']
        return [{
            'key': result['key'],
            'value': float(result['doc_count']) / source_counts[result['key']] * 100
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
        labels.append(item['key'])
        values.append(item['value'])

    return values, labels


def create_pie_chart(elastic_results, terms, agg_type, title):
    ''' takes a list of elastic results, and
    returns a bar graph of the doc counts.
    Looks very messy at the moment - need to fix labels'''

    source_percents = full_results_to_list(elastic_results, terms, agg_type)
    values, labels = extract_values_and_labels(source_percents)

    title = '{} {} {}'.format(title, agg_type, terms[0])
    plt.pie(values, labels=labels)
    plt.title(title)
    plt.savefig(title + 'PieGraph')


def create_bar_graph(elastic_results, terms, agg_type, x_label, title):
    ''' takes a list of elastic results, and
    returns a bar graph of the doc counts'''
    source_percents = full_results_to_list(elastic_results, terms, agg_type)
    values, labels = extract_values_and_labels(source_percents)

    index = np.arange(len(values))
    width = 0.35

    plt.bar(index, values)

    title = '{} {} {}'.format(title, agg_type, terms[0])

    plt.xticks(index + width / 2, labels, rotation='vertical')
    plt.xlabel(x_label)

    if agg_type == 'Term':
        plt.ylabel('Documents in Each Source')
    else:
        plt.ylabel('Percent of Documents in Each Source')

    plt.title(title)
    plt.tight_layout()
    plt.ylim(0, 100)
    # plt.show(title + 'BarGraph', )
    plt.savefig('figures/' + title.replace('SHARE Results ', '').replace(' ', '') + 'BarGraph')


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


def create_histogram(elastic_results, terms, agg_type, title):
    source_percents = full_results_to_list(elastic_results, terms, agg_type)
    values, labels = extract_values_and_labels(source_percents)

    index = np.arange(len(values))
    width = 0.35

    plt.hist(values, label=labels)

    title = '{} {} {}'.format(title, agg_type, terms[0])

    plt.xlim(0, 100)

    plt.ylabel('Frequency (Number of Providers)')

    plt.xlabel('Percent {}'.format(agg_type))
    plt.title(title)
    plt.tight_layout()
    plt.savefig('figures/' + title.replace('SHARE Results ', '').replace(' ', '') + 'Histogram')


def parse_args():
    parser = argparse.ArgumentParser(description="A command line interface for getting numbers of SHARE sources missing given terms")

    parser.add_argument('-m', '--missing', dest='missing', type=str, help='The terms to aggregate with, to find sources with terms missing', nargs='+')
    parser.add_argument('-t', '--terms', dest='terms', type=str, help='The top unique entries with given terms. Use with size to control number of results shown.', nargs='+')
    parser.add_argument('-s', '--size', dest='size', type=int, help='The number of results to return per aggretation', default=0)
    parser.add_argument('-v', '--version', dest='v', type=int, help='The version of the OSF SHARE API to hit', default=2)
    parser.add_argument('-i', '--includes', dest='includes', type=str, help='The terms to aggregate with, to find sources with terms included', nargs='+')
    parser.add_argument('-b', '--bargraph', dest='bargraph', help='A flag to signal to draw a bar graph', action='store_true')
    parser.add_argument('-p', '--piegraph', dest='piegraph', help='A flag to signal to draw a pie graph', action='store_true')
    parser.add_argument('-hist', '--histogram', dest='histogram', help='A flag to signal to draw a histogram', action='store_true')
    parser.add_argument('-bub', '--bubblechart', dest='bubblechart', help='A flag to signal to draw a bubblechart', action='store_true')

    return parser.parse_args()


def main():
    today = date.today().isoformat()
    args = parse_args()
    aggs = all_source_counts()
    if args.missing:
        agg_type = 'Missing'
        aggs.update(missing_agg_query(args.missing))
    if args.terms:
        agg_type = 'Term'
        aggs.update(terms_agg_query(args.terms, args.size))
    if args.includes:
        agg_type = 'Included'
        aggs.update(includes_agg_query(args.includes))

    url = OSF_APP_URL.format(args.v)

    results = search(url, aggs)

    print(json.dumps(results, indent=4))

    for agg in aggs.keys():
        if agg != 'allSourceAgg':
            filename = agg

    with open('figures/data/{}.json'.format(filename), 'w') as outfile:
        json.dump(results, outfile)

    graph_variable = args.missing or args.includes or args.terms

    if args.bargraph:
        create_bar_graph(elastic_results=results, terms=graph_variable, agg_type=agg_type, x_label='terms', title='SHARE Results as of {}'.format(today))
    if args.piegraph:
        create_pie_chart(results, terms=graph_variable, agg_type=agg_type, title='SHARE Results as of {}'.format(today))
    if args.histogram:
        create_histogram(results, terms=graph_variable, agg_type=agg_type, title='SHARE Results as of {}'.format(today))
    if args.bubblechart and 'tags' in args.terms:
        create_bubble(results)

if __name__ == '__main__':
    main()
