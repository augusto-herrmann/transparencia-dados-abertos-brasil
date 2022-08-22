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

import argparse
from datetime import datetime
from functools import partial
import logging
import multiprocessing
import os
from typing import Sequence, List

import pandas as pd
from tqdm import tqdm

from validation.verify_links import (healthy_link, get_title_and_type,
    get_candidate_links, get_output_to_be_merged, store_csv)

INPUT_FOLDER = '../../data/unverified'
INPUT_FILE = 'municipality-website-candidate-links.csv'
MAX_SIMULTANEOUS = 10
MAX_QUANTITY = 0
OUTPUT_FOLDER = '../../data/valid'
OUTPUT_FILE = 'brazilian-municipality-and-state-websites.csv'

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
            _, link_type = get_title_and_type(
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
    candidates = get_candidate_links(
        file_path=os.path.join(input_folder, input_file),
        max_quantity=max_quantity)
    codes = candidates.code.unique()
    new_links = pd.DataFrame(columns=list(candidates.columns) +
        ['last_checked'])

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
                    new_links.loc[len(new_links)] = verified_link
            progress_bar.update(max_simultaneous)

    # read resource to be updated
    table = get_output_to_be_merged(data_package_path)

    # prepare column names
    new_links.rename(columns={
        'uf': 'state_code',
        'code': 'municipality_code',
        'name': 'municipality',
        'link_type': 'branch',
        'link': 'url',
        'last_checked': 'last-verified-auto'
    }, inplace=True)

    # map values
    new_links.branch = new_links.branch.str.replace('prefeitura', 'executive')
    new_links.branch = new_links.branch.str.replace('camara', 'legislative')
    new_links['sphere'] = 'municipal'

    logging.info('Updating values...')
    for _, result in new_links.iterrows():
        # get existing data in file to be updated
        existing_data = table.loc[
                (table.municipality_code == result['municipality_code']) &
                (table.branch == result['branch'])
            ]
        if len(existing_data) > 0:
            row = existing_data.iloc[0].copy()
            for key in ['sphere', 'branch', 'url', 'last-verified-auto']:
                row[key] = result[key] # update the values
            table.loc[len(table)] = row
        else:
            table.loc[len(table)] = result

    # remove duplicate entries,
    # take into account only url column,
    # keep last entry to preserve the last-verified-auto timestamp
    table.drop_duplicates(subset='url', keep='last', inplace=True)
    table.sort_values(
        by=['sphere', 'state_code', 'municipality', 'branch'],
        inplace=True)

    # returns the results
    return table

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    options = parse_cli()
    table = auto_verify(**options)
    store_csv(table, options['data_package_path'])
