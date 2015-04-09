from __future__ import division

import json
import argparse
import requests

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


def parse_args():
    parser = argparse.ArgumentParser(description="A command line interface for getting numbers of SHARE sources missing given terms")

    parser.add_argument('-m', '--missing', dest='missing', type=str, help='The terms to aggregate with, to find sources with terms missing', nargs='+')
    parser.add_argument('-t', '--terms', dest='terms', type=str, help='The top unique entries with given terms. Use with size to control number of results shown.', nargs='+')
    parser.add_argument('-s', '--size', dest='size', type=int, help='The number of results to return per aggretation', default=0)
    parser.add_argument('-i', '--includes', dest='includes', type=str, help='The terms to aggregate with, to find sources with terms included', nargs='+')

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

    search_osf = search(aggs)

    print(json.dumps(search_osf, indent=4))


if __name__ == '__main__':
    main()
