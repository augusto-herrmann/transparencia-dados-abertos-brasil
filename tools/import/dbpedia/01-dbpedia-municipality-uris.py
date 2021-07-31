# 01-dbpedia-municipality-uris.py
"""
 This script fetches the municipalities URIs from DBPedia.
 
 Este script traz as URIs de municípios da DBPedia.
"""

import re
import os
import urllib
import pandas as pd
from frictionless import Package

GEO_FOLDER = '../../../data/auxiliary/geographic'
GEO_FILE = 'municipality.csv'
OUTPUT_FOLDER = '../../../data/auxiliary/geographic'
OUTPUT_FILE = 'municipality.csv'

remove_parenthesis = re.compile(r'[^(,]+')

DBPEDIA_PT_SPARQL = 'dbpedia-pt.sparql'
DBPEDIA_SPARQL = 'dbpedia.sparql'
ESPIRITO_SANTO_DBPEDIA_SPARQL = 'espirito-santo.dbpedia.sparql'
DBPEDIA_PT_URL = 'http://pt.dbpedia.org/sparql?default-graph-uri=&{}&should-sponge=&format=text%2Fcsv&timeout=0&debug=on'
DBPEDIA_URL = 'https://dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fdbpedia.org&{}&format=text%2Fcsv&timeout=30000&signal_void=on&signal_unconnected=on'


def update_column(
    old_df: pd.DataFrame,
    new_df:pd.DataFrame,
    column: str
    ) -> pd.DataFrame:
    "Update the column in the old dataframe with data from the same column in the new dataframe"
    
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
    
    # read SPARQL query
    with open (sparql_file, 'r') as f:
        sparql_query = urllib.parse.urlencode({'query':f.read()})
    
    # get query URL
    sparql_query_as_csv = sparql_query_url.format(sparql_query)

    # read data frame from Portuguese DBPedia
    dbp = pd.read_csv(sparql_query_as_csv)

    # remove parenthesis in city names
    dbp['name'] = dbp['name'].apply(
        lambda s: remove_parenthesis.match(s).group().strip()\
            if isinstance(s, str) else s
    )

    # remove parenthesis in state names
    dbp['state'] = dbp['state'].apply(
        lambda s: remove_parenthesis.match(s).group().strip() \
            if isinstance(s, str) else s
    )

    # get WikiData URIs for later
    wikidata = (
        dbp
        .loc[:, ['name', 'state', 'wikidata']]
        .loc[dbp.state.notna()]
        .loc[dbp.wikidata.notna()]
        .drop_duplicates()
        .copy()
    )

    # get the state (UF) abbreviations as the DBPedia data does not contain them
    package = Package(
        os.path.join(os.path.dirname(geo_file),'datapackage.json')
    )
    uf = package.get_resource('uf').to_pandas()

    # adjust column names and types
    uf.rename(columns={'name': 'state'}, inplace=True)
    uf.drop('code', axis=1, inplace=True)
    uf['state'] = uf['state'].astype('category')

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

    # get the municipality codes as the DBPedia data does not contain them
    mun = package.get_resource('municipality').to_pandas()

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
    # from Portuguese language DBPedia
    update_from_dbpedia(
        os.path.join(OUTPUT_FOLDER, OUTPUT_FILE),
        os.path.join(GEO_FOLDER, GEO_FILE),
        DBPEDIA_PT_SPARQL,
        DBPEDIA_PT_URL
    )
    # from English DBPedia
    update_from_dbpedia(
        os.path.join(OUTPUT_FOLDER, OUTPUT_FILE),
        os.path.join(GEO_FOLDER, GEO_FILE),
        DBPEDIA_SPARQL,
        DBPEDIA_URL
    )
    # state of Espírito Santo from English DBPedia
    update_from_dbpedia(
        os.path.join(OUTPUT_FOLDER, OUTPUT_FILE),
        os.path.join(GEO_FOLDER, GEO_FILE),
        ESPIRITO_SANTO_DBPEDIA_SPARQL,
        DBPEDIA_URL
    )
