# step_02_dbpedia_website_links.py
"""
  This script interprets the URLs municipalities websites from
  DBPedia. At a later stage these URLs are used to find out the respective
  transparency portals.

  Usage:
    python step_02_dbpedia_website_links.py

  Este script interpreta as URLs dos sites dos municípios a
  partir da DBPedia. Em uma etapa posterior essas URLs são usadas para
  encontrar os respectivos portais da transparência.
"""

import re
import os
import urllib
import yaml
import logging

import pandas as pd
from frictionless import Package

GEO_FOLDER = '../../../data/auxiliary/geographic'
GEO_FILE = 'municipality.csv'
OUTPUT_FOLDER = '../../../data/unverified'
OUTPUT_FILE = 'municipality-website-candidate-links.csv'
re_remove_parenthesis = re.compile(r'[^(,]+')

def get_config(file_name: str = 'config.yaml') -> dict:
    """Reads configuration from yaml file.

    Returns:
        The configuration dict containing all relevant config data.
    """
    with open(file_name, 'r') as file:
        config = yaml.safe_load(file)
    for source in config['sources']:
        for query in source['queries']:
            with open(query['sparql_file'], 'r') as query_file:
                query_string = urllib.parse.urlencode(
                    {'query':query_file.read()})
            query['url'] = (
                f'{source["endpoint"]}?'
                f'default-graph-uri=&{query_string}'
                f'&{query["options"]}'
            )
    return config

def remove_parenthesis(text: str) -> str:
    """Removes parenthesis from a string.

    Many city names are followed by the state name in parenthesis.

    Args:
        text (str): The text to process, usually a name that may or may
            not contain parenthesis.

    Returns:
        str: The text without the part in parenthesis.
    """
    if not text:
        return text
    match = re_remove_parenthesis.match(text)
    if not match:
        return text.strip()
    return match.group().strip()

def get_dbpedia_links_dataframe(query_url: str) -> pd.DataFrame:
    """Get a clean pd.DataFrame containing the desired links from the
    csv file obtained at the given url.

    Args:
        query_url (str): A url that returns a csv file in the desired
            format.

    Returns:
        od.DataFrame: a cleaned up Pandas dataframe containing the
            discovered links.
    """
    # read data frame from url to csv
    table = pd.read_csv(query_url)

    # do some cleaning:
    # - no need for the city URIs column
    table.drop('city', axis=1, inplace=True)
    # - remove parenthesis in city names
    table['name'] = table.name.fillna('').apply(remove_parenthesis)
    table['state'] = table.state.fillna('').apply(remove_parenthesis)

    # get the state (UF) abbreviations as the DBPedia data does not contain them
    geodata = Package(os.path.join(GEO_FOLDER,'datapackage.json'))

    # adjust column names and types
    uf = (
        geodata.get_resource('uf').to_pandas()
        .rename(columns={'name': 'state'})
        .drop('code', axis=1) # no need to keep the state code
    )
    uf['state'] = uf['state'].astype('category')

    # merge back into the DBPedia data
    table = (
        table
        .merge(uf, on='state')
        .drop('state', axis=1)
        .rename(columns={'abbr': 'uf'})
    )

    # get the municipality codes as the DBPedia data does not contain them
    mun = geodata.get_resource('municipality').to_pandas()

    # merge the data and remove duplicate rows
    table = (
        table
        .merge(mun)
        .drop_duplicates()
    )

    # melt 4 types of links into one
    table = pd.melt(table, id_vars=['name', 'uf', 'code'], var_name='link_type', value_name='link')
    table.drop_duplicates(inplace=True)

    # remove empty lines and duplicate links
    table.dropna(subset=['link'], inplace=True)
    table.drop_duplicates(subset=['link'], keep='first', inplace=True)

    logging.info('Got %d links from "%s".', len(table), query_url)

    return table

def clean_dbpedia_links(table: pd.DataFrame) -> pd.DataFrame:
    """Clean a DBPedia links dataframe, fixing some links and removing
    unwanted links.

    Args:
        table (pd.DataFrame): A Pandas dataframe containing links,
            structured like the output of get_dbpedia_links_dataframe

    Returns:
        pd.DataFrame: A clean Pandas dataframe.
    """
    # remove links to files
    table = table[
        ~table.link.str.contains(r'\.(?:pdf|png|jpg|gif|bmp)$', na=False, regex=True)
    ]

    # remove generic links to IBGE
    table = table[
        ~table.link.str.contains(r'ibge\.gov\.br\/?', na=False, regex=True)
    ]

    # remove generic links to Blogspot
    table = table[
        ~table.link.str.contains(r'blogspot\.com\/?', na=False, regex=True)
    ]

    # remove generic links to Facebook
    table = table[
        ~table.link.str.contains(r'facebook\.com\/?', na=False, regex=True)
    ]

    # remove generic links to Yahoo
    table = table[
        ~table.link.str.contains(r'yahoo\.com\/?', na=False, regex=True)
    ]

    # remove generic links to Google
    table = table[
        ~table.link.str.contains(r'(?:googleusercontent\.com|google\.com\.br)\/?', na=False, regex=True)
    ]

    # remove generic links to Wikimedia
    table = table[
        ~table.link.str.contains(r'wiki(?:media|pedia|source)\.org\/?', na=False, regex=True)
    ]

    # remove recursive links to DBPedia
    table = table[
        ~table.link.str.contains(r'dbpedia\.org\/?', na=False, regex=True)
    ]

    # remove generic links to state website
    table = table[
        ~table.link.str.contains(r'//www\.\w{2}\.gov\.br\/?$', na=False, regex=True)
    ]

    # remove Google trackers
    google_trackers = table.link.str.contains(
        r'google\.com(?:\.br)?/url',
        na=False,
        regex=True
    )
    table.loc[google_trackers, 'link'] = table.loc[google_trackers].link.apply(
        lambda outer_url: urllib.parse.parse_qs(
            urllib.parse.urlparse(outer_url).query
        )['url'][0]
    )

    # remove white spaces after URLs (WTF?)
    parenthesis_things = table.link.str.contains(
        r'^[^\s]+\s',
        na=False,
        regex=True
    )
    table.loc[parenthesis_things, 'link'] = table.loc[parenthesis_things].link.apply(
        lambda thing: thing.split()[0]
    )

    # remove parenthesis over URLs (WTF?)
    parenthesis_things = table.link.str.contains(
        r'^\(.+\)$',
        na=False,
        regex=True
    )
    table.loc[parenthesis_things, 'link'] = table.loc[parenthesis_things].link.apply(
        lambda thing: thing[1:-1]
    )

    # fix malformed URLs
    malformed_urls = table.link.str.contains(
        r'^\w+(?:\.\w+)+\.(?:br|com|net)[\w/]*$', # URLs without a schema part
        na=False,
        regex=True
    )
    table.loc[malformed_urls, 'link'] = table.loc[malformed_urls].link.apply(
        # default to http, should at least have a redirect to https
        lambda url: f'http://{url}'
    )

    # remove empty links and duplicates
    table.dropna(subset=['link'], inplace=True)
    table.drop_duplicates(inplace=True)

    # final adjustments to link types
    table.link_type.replace('link_camara', 'camara', inplace=True)
    table.link_type.replace('link_prefeitura', 'prefeitura', inplace=True)
    table.link_type.replace('external_link', 'external', inplace=True)
    table.link_type.replace('link_site', 'link', inplace=True)
    table.link_type.replace('link_site_oficial', 'prefeitura', inplace=True)

    return table

def store_dbpedia_links(table: pd.DataFrame, output_folder: str,
    output_file: str):
    """Store the links in a CSV file. If the file already exists, merge
    the existing with the obtained data.

    Args:
        table (pd.DataFrame): A Pandas dataframe containing the links
            obtained from DBPedia, in the format output by
            get_dbpedia_links_dataframe.
        output_folder (str): The path where the output file should be
            stored.
        output_file: (str): The file name of the output.
    """
    # prepare output

    # check if the output folder alredy does exist and, if not, create it
    if not os.path.exists(output_folder):
        print(f'Output folder does not yet exist. Creating "{output_folder}"...')
        os.mkdir(output_folder)

    output = os.path.join(output_folder, output_file)
    generated_df = table
    # check whether if there is an existing file to merge
    if os.path.exists(output):
        recorded_df = pd.read_csv(output)
        new_df = pd.concat([recorded_df, generated_df], sort=True)
    else:
        new_df = generated_df.copy()
    # remove duplicate entries
    new_df.drop_duplicates(inplace=True)
    # store the results
    new_df.to_csv(output, index=False)

if __name__ == '__main__':
    config = get_config()

    # combine data: concatenate the results
    dbp_links = pd.concat(
        [
            get_dbpedia_links_dataframe(query['url'])
            for source in config['sources']
            for query in source['queries']
        ],
        sort=True
    )

    # remove garbage links
    dbp_links = clean_dbpedia_links(dbp_links)

    # store the results
    store_dbpedia_links(dbp_links, OUTPUT_FOLDER, OUTPUT_FILE)
