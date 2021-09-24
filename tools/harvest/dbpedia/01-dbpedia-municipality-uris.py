"""01-dbpedia-municipality-uris.py

This script fetches the municipalities URIs from DBPedia.

Este script traz as URIs de municípios da DBPedia.
"""

import re
import os
import urllib
import random
import time
import yaml

import pandas as pd
from frictionless import Package

GEO_FOLDER = '../../../data/auxiliary/geographic'
GEO_FILE = 'municipality.csv'
OUTPUT_FOLDER = '../../../data/auxiliary/geographic'
OUTPUT_FILE = 'municipality.csv'
CONFIG_FILE = 'config.yaml'

re_remove_parenthesis = re.compile(r'[^(,]+')

REQUEST_INTERVAL = (8, 16)

def query_from_dbpedia(
    sparql_file_name: str,
    sparql_query_url: str
    ) -> pd.DataFrame:
    """Reads a sparql query from file and returns a data frame.
    """

    # read SPARQL query
    with open (sparql_file_name, 'r') as f:
        sparql_query = urllib.parse.urlencode({'query':f.read()})

    # get query URL
    sparql_query_as_csv = sparql_query_url.format(sparql_query)

    # read data frame from Portuguese DBPedia
    return pd.read_csv(sparql_query_as_csv)

def get_mun_uf(geo_file: str) -> (pd.DataFrame, pd.DataFrame):
    """Get the state (UF) abbreviations from the geographic data package.
    """
    package = Package(
        os.path.join(os.path.dirname(geo_file),'datapackage.json')
    )
    uf = package.get_resource('uf').to_pandas()

    # adjust column names and types
    uf.rename(columns={'name': 'state'}, inplace=True)
    uf.drop('code', axis=1, inplace=True)
    uf['state'] = uf['state'].astype('category')

    mun = package.get_resource('municipality').to_pandas()

    return mun, uf

def remove_parenthesis(label: str) -> str:
    """Returns the string up to but not including the first comma or
    parenthesis."""
    return re_remove_parenthesis.match(label).group().strip()\
            if isinstance(label, str) else label

def update_column(
    old_df: pd.DataFrame,
    new_df:pd.DataFrame,
    column: str
    ) -> pd.DataFrame:
    """Update the column in the old dataframe with data from the same
    column in the new dataframe.
    """

    return old_df[column].combine(
        new_df[column],
        lambda old_URI, new_URI: old_URI if not new_URI or pd.isna(new_URI) else new_URI,
    ) if column in old_df.columns else new_df[column]

def update_from_dbpedia(
    output_file: str,
    geo_file: str,
    sparql_file: str,
    sparql_query_url: str
    ):
    """Makes a DBPedia query to retrieve data about municipalities and
    updates the csv file.
    """

    dbp = query_from_dbpedia(sparql_file, sparql_query_url)

    # remove parenthesis in city names
    dbp['name'] = dbp['name'].apply(remove_parenthesis)

    # remove parenthesis in state names
    dbp['state'] = dbp['state'].apply(remove_parenthesis)

    # get WikiData URIs for later
    wikidata = (
        dbp
        .loc[:, ['name', 'state', 'wikidata']]
        .loc[dbp.state.notna()]
        .loc[dbp.wikidata.notna()]
        .drop_duplicates()
        .copy()
    )

    # get the state (UF) abbreviations and municipality codes, as the
    # DBPedia data does not contain that information
    mun, uf = get_mun_uf(geo_file)

    # get state abbreviations for wikidata df
    wikidata = (
        wikidata
        .merge(uf)
        .loc[:, ['name', 'abbr', 'wikidata']]
        .rename(columns={'abbr': 'uf'})
    )

    # handle the different types of URIs – main DBPedia or pt DBPedia
    dbp['URI_type'] = dbp.city.apply(
        lambda s: 'dbpedia' \
            if s.startswith('http://dbpedia.org/') \
            else 'dbpedia_pt' \
                if s.startswith('http://pt.dbpedia.org/') \
                    else None
    )

    # format the dataframe like the municipality table
    dbp = dbp.merge(uf)
    dbp.drop('state', axis=1, inplace=True)
    dbp.rename(columns={'abbr': 'uf'}, inplace=True)
    dbp.rename(columns={'city': 'URI'}, inplace=True)
    dbp = dbp.loc[:, ['name', 'uf', 'URI', 'URI_type']] # discard all other columns
    dbp.sort_values(by=['uf', 'name', 'URI'], inplace=True)
    dbp.drop_duplicates(subset=['name', 'uf', 'URI_type'], keep='first', inplace=True)

    # create dbpedia and dbpedia_pt columns depending on the value of URI
    dbp = (
        dbp
        .merge(
            (
                dbp
                .pivot(index=['name', 'uf'], columns='URI_type', values='URI')
                .reindex()
            ), on=['name', 'uf'], how='left'
        )
        .drop(['URI', 'URI_type'], axis=1)
        .drop_duplicates()
    )

    # just add the municipality codes to the dataframe
    dbp = dbp.merge(
        mun.loc[:, ['code', 'name', 'uf']], # use just those columns for merge
        on=['name', 'uf'], # keys for the join operation
        how='right', # keep the keys from mun dataframe even if not found on dbp
    ).reindex(columns=['code', 'name', 'uf', 'dbpedia', 'dbpedia_pt'])

    # add wikidata column to dbp again
    dbp = (
        dbp
        .merge(wikidata, on=['name', 'uf'], how='left')
    )

    # TODO: figure out what to do with extra/duplicated Wikidata URIs
    # dbp[dbp.duplicated(subset=['name', 'uf'], keep=False)].to_csv('duplicated.csv', index=False)

    # if dataframe has more than one wikidata entry, consider only
    # the first one
    dbp.drop_duplicates(subset=['name', 'uf'], keep='first', inplace=True)

    # sort both dataframes to align them
    assert len(dbp) == len(mun) # must be the same size
    dbp.sort_values(by='code', inplace=True)
    mun.sort_values(by='code', inplace=True)
    dbp.set_index(dbp.code, inplace=True) # make the index be the code
    mun.set_index(mun.code, inplace=True) # make the index be the code

    # update the URIs, if present. Otherwise, preserve the old ones
    mun['dbpedia'] = update_column(mun, dbp, 'dbpedia')
    mun['dbpedia_pt'] = update_column(mun, dbp, 'dbpedia_pt')
    mun['wikidata'] = update_column(mun, dbp, 'wikidata')

    # write back the csv
    mun.to_csv(output_file, index=False)

if __name__ == '__main__':
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f.read())
        sources = config['sources']

        for source in sources:
            endpoint = source['endpoint']
            print(f'Processing endpoint: {endpoint}\n')
            for i, query in enumerate(source['queries']):
                update_from_dbpedia(
                        os.path.join(OUTPUT_FOLDER, OUTPUT_FILE),
                        os.path.join(GEO_FOLDER, GEO_FILE),
                        query['sparql_file'],
                        f"{endpoint}?{query['options']}"
                )
                if i + 1 < len(source['queries']): # do not wait the last one
                    interval = random.uniform(*REQUEST_INTERVAL)
                    print(f'Waiting {interval:.2f} seconds before '
                            'the next request...')
                    time.sleep(interval)
