"""
This script crawls candidate URLs for municipalities websites and
checks if they are active and likely to be the city hall or
city council portals.

Usage:
  python auto_verify_links.py

For instructions use:
  python auto_verify_links.py --help

Este script navega nas URLs candidatas a sites dos municípios e
verifica se elas estão ativas e são prováveis portais das prefeituras
e câmaras municipais.
"""

import os
import argparse
import re
from datetime import datetime
import random
import logging
import multiprocessing
from functools import partial
from typing import Sequence, List

import pandas as pd
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from frictionless import Package

USER_AGENT = 'transparencia-dados-abertos-brasil/0.0.2'
TIMEOUT = 20
INPUT_FOLDER = '../../data/unverified'
INPUT_FILE = 'municipality-website-candidate-links.csv'
MAX_SIMULTANEOUS = 10
MAX_QUANTITY = 0
OUTPUT_FOLDER = '../../data/valid'
OUTPUT_FILE = 'brazilian-municipality-and-state-websites.csv'

def healthy_link(link: str) -> requests.Response:
    """Check whether or not the link is healthy.

    Args:
        link (str): The url of the link to be verified.

    Returns:
        requests.Response: The Response object in case the link
            is healthy, None otherwise.
    """
    try:
        response = requests.get(
            link,
            headers={'user-agent': USER_AGENT},
            timeout=TIMEOUT
            )
    except (
        requests.exceptions.ConnectionError,
        requests.exceptions.InvalidURL,
        requests.exceptions.TooManyRedirects,
        requests.exceptions.ReadTimeout
    ):
        return None
    if response and response.status_code == 200:
        return response
    return None

def check_type(
    response: requests.Response,
    candidates: pd.DataFrame) -> str:
    """Try to infer the type of site this is.

    Args:
        response (requests.Response): The Response object obtained when
            crawling the page.
        candidates (pd.DataFrame): The Pandas dataframe slice containing
            the candidate links.

    Returns:
        str: The link type category.
    """
    soup = BeautifulSoup(response.text, 'html.parser')
    title_tag = soup.find('title')
    if title_tag is None:
        return None
    title = unidecode(title_tag.text.lower())
    link_types = candidates.link_type
    if 'prefeitura' in link_types:
        link_type = 'prefeitura'
    elif 'camara' in link_types:
        link_type = 'camara'
    elif 'hino' in title:
        link_type = None
    elif 'brasao' in title:
        link_type = None
    elif 'prefeitura' in title:
        link_type = 'prefeitura'
    elif 'municipio' in title:
        link_type = 'prefeitura'
    elif re.match(r'c.{0,3}mara', title, re.IGNORECASE):
        link_type = 'camara'
    elif 'poder executivo' in title:
        link_type = 'prefeitura'
    elif 'governo municipal' in title:
        link_type = 'prefeitura'
    elif 'pref.' in title:
        link_type = 'prefeitura'
    else:
        logging.warning(
            'Unable to determine site type from title: “%s”.', title)
        link_type = None
    return link_type

def verify_city_links(candidates: pd.DataFrame, code: int) -> List[dict]:
    """Verify links for a city with a given code.

    Args:
        candidates (pd.DataFrame): The dataframe slice with the link
            candidates to verify.
        code (int): The IBGE municipality code associated with the link.

    Returns:
        List(dict): A list of dictionaries containing information about
            the detected link.
    """
    verified_links = []
    city_links = candidates[candidates.code == code]
    for link in city_links.link.unique():
        working_link = healthy_link(link)
        if working_link:
            link_type = check_type(
                working_link,
                candidates[candidates.link==link]
            )
            if link_type is not None:
                verified_link = {
                    'code': code,
                    'link': working_link.url, # update if redirected
                    'link_type': link_type,
                    'name': city_links.name.iloc[0],
                    'uf': city_links.uf.iloc[0],
                    'last_checked': datetime.utcnow()
                }
                verified_links.append(verified_link)
    return verified_links

def parse_cli() -> dict:
    """Parses the command line interface.

    Returns:
        dict: A dict containing the values for input_folder, input_file,
            data_package_path, max_quantity, max_simultaneous
    """
    parser = argparse.ArgumentParser(
        description='''Crawls candidate URLs for municipalities websites and checks
    if they are active and likely to be the city hall or city council portals.'''
        )

    parser.add_argument('input',
        help='input file in CSV format',
        default='',
        nargs='?',
    )
    parser.add_argument('output',
        help=('output folder for the CSV '
            '(must have a datapackage.json with a schema)'),
        default='',
        nargs='?',
    )
    parser.add_argument('-q', '--quantity',
        metavar='int', type=int,
        help='maximum quantity of cities to process',
        default=0,
    )
    parser.add_argument('-p', '--processes',
        metavar='int', type=int,
        help='number of processes (parallel downloads) to use',
        default=8,
    )
    params = {}
    args = parser.parse_args()
    if args.input:
        params['input_folder'] = os.path.dirname(args.input)
        params['input_file'] = os.path.basename(args.input)
    else: # use default values
        params['input_folder'] = INPUT_FOLDER
        params['input_file'] = INPUT_FILE
    if args.output:
        if not os.path.exists(args.output):
            raise FileNotFoundError(f'Folder not found: {args.output}')
        output_folder = args.output
    else: # use default value
        output_folder = OUTPUT_FOLDER
    params['data_package_path'] = os.path.join(output_folder, 'datapackage.json')
    if not os.path.exists(params['data_package_path']):
        raise FileNotFoundError(
            f'datapackage.json not found in folder: {args.output}')
    if args.quantity:
        params['max_quantity'] = args.quantity
    else: # use default value
        params['max_quantity'] = MAX_QUANTITY
    if args.processes:
        params['max_simultaneous'] = args.processes
    else: # use default value
        params['max_simultaneous'] = MAX_SIMULTANEOUS
    return params

def auto_verify(input_folder: str, input_file: str, data_package_path: str,
        max_quantity: int, max_simultaneous: int) -> pd.DataFrame:
    """Automatically verifies links and try to infer the link type for
    each.

    A Python function that does the same job as the script that is run
    from the command line.

    Args:
        input_folder (str): The folder containing the input table.
        input_file (str): Name of the file containing the input table in
            csv format.
        data_package_path (str): Path to the datapackage.json file.
        max_quantity (int): Maximum quantity of links to check.
        max_simultaneous (int): Maximum quantity of simultaneous (in
            parallel) checks.

    Returns:
        pd.DataFrame: Pandas dataframe containing the verified links.
    """
    candidates = pd.read_csv(os.path.join(input_folder, input_file))
    logging.info(
        'Found %d link candidates in %s.',
        len(candidates),
        os.path.join(input_folder, input_file))
    codes = candidates.code.unique()
    random.shuffle(codes) # randomize sequence
    if max_quantity:
        codes = codes[:max_quantity] # take a subsample for quicker processing
    goodlinks = pd.DataFrame(columns=candidates.columns)

    def in_chunks(seq: Sequence, size: int) -> Sequence:
        """Returns a Sequence spaced in chunks of arbitrary size.

        Args:
            seq (Sequence): The Sequence to separate in chunks.
            size (int): The chunk size.

        Returns:
            Sequence: The Sequence of chunks resulting from the separation.
        """
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))

    pool = multiprocessing.Pool(processes=max_simultaneous)

    with tqdm(total=len(codes)) as progress_bar:
        logging.info('Cralwing candidate URLs for %d cities...', len(codes))
        for chunk in in_chunks(codes, max_simultaneous):
            results = pool.map(partial(verify_city_links, candidates), chunk)
            for result in results:
                for verified_link in result:
                    # TODO: replace deprecated pd.DataFrame.append
                    goodlinks = goodlinks.append(
                        verified_link, ignore_index=True)
            progress_bar.update(max_simultaneous)

    # record validated

    # read schema
    package = Package(data_package_path)
    resource = package.get_resource('brazilian-municipality-and-state-websites')
    table = resource.to_pandas()

    # prepare column names
    goodlinks.rename(columns={
        'uf': 'state_code',
        'code': 'municipality_code',
        'name': 'municipality',
        'link_type': 'branch',
        'link': 'url',
        'last_checked': 'last-verified-auto'
    }, inplace=True)

    # map values
    goodlinks.branch = goodlinks.branch.str.replace('prefeitura', 'executive')
    goodlinks.branch = goodlinks.branch.str.replace('camara', 'legislative')
    goodlinks['sphere'] = 'municipal'

    logging.info('Updating values...')
    for _, result in goodlinks.iterrows():
        # get existing data in file to be updated
        existing_data = table.loc[
                (table.municipality_code == result['municipality_code']) &
                (table.branch == result['branch'])
            ]
        if len(existing_data) > 0:
            row = existing_data.iloc[0].copy()
            for key in ['sphere', 'branch', 'url', 'last-verified-auto']:
                row[key] = result[key] # update the values
            table = table.append(row, ignore_index=True)
        else:
            table = table.append(result, ignore_index=True)

    # remove duplicate entries,
    # take into account only url column,
    # keep last entry to preserve the last-verified-auto timestamp
    table.drop_duplicates(subset='url', keep='last', inplace=True)
    table.sort_values(by=['state_code', 'municipality'], inplace=True)

    # returns the results
    return table

def store_csv(table: pd.DataFrame, data_package_path: str):
    """Stores the csv file in the output folder.

    Args:
        table (pd.DataFrame): The dataframe containing the data.
        data_package_path (str): Path to the datapackage.json file.
    """
    package = Package(data_package_path)
    resource = package.get_resource('brazilian-municipality-and-state-websites')
    output = resource.path # filename of csv to write
    logging.info('Recording %s...', output)
    # store the file
    table.to_csv(output, index=False, date_format='%Y-%m-%dT%H:%M:%SZ')

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    options = parse_cli()
    table = auto_verify(**options)
    store_csv(table, options['data_package_path'])
