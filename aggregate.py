from __future__ import division

import sys
import json
import argparse
import datetime
import requests

import getopt


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

DEFAULT_REQUEST_PARAMS = {
    'return_raw': False
}

# Local settings
OSF_APP_URL = 'http://localhost:5000/api/v1/share/search/?raw=True'
# OSF_AUTH = ('scrapi', '54331d5a669aec8577089ad1e4b9dcb3-50f3-4828-9232-d85512a999e7')

# share-dev settings
# OSF_APP_URL = 'https://share-dev.osf.io/api/v1/app/6qajn/?return_raw=True'
# OSF_AUTH = ('scrapi_stats','543edf86b5e9d7579327c710eb1d94ee-d8da-472a-84bb-ba6b96499c80')


def query_osf(query):
    response = requests.post(OSF_APP_URL, json=query, verify=False)
    return response.json()


def search(missing_terms):
    query = nested_agg_query(missing_terms)
    osf_query = query_osf(query)
    return osf_query


def simple_agg_query():
    return {
        "size": 0,
        "aggs": {
            "sources": {
                "terms": {"field": "source"}
            }
        }
    }


def nested_agg_query(terms):
    return {
        "size": 0,
        "aggs": {
            term + "Aggregation": {
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
    }


def usage():
    print('Usage:')
    print('-t or --terms: enter terms you would like to see are missing from each source')


def parse_args():
    parser = argparse.ArgumentParser(description="A command line interface for getting numbers of SHARE sources missing given terms")

    parser.add_argument('terms', type=str, help='The terms to search for', nargs='+')
    return parser.parse_args()


def main():
    args = parse_args()

    search_osf = search(args.terms)

    print(json.dumps(search_osf, indent=4))


if __name__ == '__main__':
    main()
