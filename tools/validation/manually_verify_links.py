"""
This script opens candidate URLs for municipalities websites in the
web browser and asks the user to check whether or not they seem to be the
official city hall or city council portals.

Usage:
  python manually_verify_links.py

For instructions use:
  python manually_verify_links.py --help

Este script abre no navegador as URLs candidatas a sites dos municípios e
pede ao utilizador que verifique se elas parecem ser os portais das
prefeituras e câmaras municipais.
"""

import os
import argparse
from datetime import datetime
import logging
import webbrowser

import pandas as pd

from validation.verify_links import (healthy_link, get_title_and_type,
    get_candidate_links, get_output_to_be_merged, store_csv)

INPUT_FOLDER = '../../data/unverified'
INPUT_FILE = 'municipality-website-candidate-links.csv'
OUTPUT_FOLDER = '../../data/valid'
MAX_QUANTITY = 0

def parse_cli() -> dict:
    """Parses the command line interface.

    Returns:
        dict: A dict containing the values for input_folder, input_file,
            data_package_path, max_quantity, max_simultaneous
    """
    parser = argparse.ArgumentParser(
        description='''Opens in a web browser candidate URLs for municipalities
        websites and asks the user to checks if they seem to be the city hall or
        city council portals.
        
    Abre no navegador as URLs candidatas a sites dos municípios e  pede ao
        utilizador que verifique se elas parecem ser os portais das prefeituras e
        câmaras municipais.
        '''
        )

    parser.add_argument('input',
        help='input file in CSV format / arquivo em formato CSV',
        default='',
        nargs='?',
        )
    parser.add_argument('output',
        help=('output folder for the CSV '
            '(must have a datapackage.json with a schema) / '
            'pasta de saída para o CSV '
            '(precisa ter um datapackage.json com um esquema)'),
        default='',
        nargs='?',
    )
    parser.add_argument('-q', '--quantity',
        metavar='int', type=int,
        help='maximum quantity of cities to process / quantidade máxima a processar',
        default=0,
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

    return params

def choose(text: str, options: str) -> str:
    """Asks the user to choose one of the defined options.

    Args:
        text (str): The text prompt to be presented to the user.
        options (str): A string containing one character for each option
            the user can choose.

    Returns:
        str: The key containing one character representing what the user
            has chosen.
    """
    while True:
        key = input(text).lower()
        if key in options.lower():
            break
    return key

def verify_city_links(candidates, code):
    'Verify links for a city with a given code.'
    verified_links = []
    signal = None
    city_links = candidates[candidates.code == code]
    name = city_links.name.iloc[0]
    uf = city_links.uf.iloc[0]
    print(f'Verifying candidate links for {name}, {uf}...')
    for link in city_links.link.unique():
        print(f'  Checking link "{link}"...')
        working_link = healthy_link(link)
        if working_link:
            print(f'  Returned status code {working_link.status_code}')
            title, link_type = get_title_and_type(
                working_link,
                candidates[candidates.link==link]
            )
            print(f'  Title is: {title}.')
            print(f'  Most likely site type is: {link_type}')
            print('  Opening URL in browser...')
            webbrowser.open(link)
            choice = choose('''
  What link type does this seem to be?
    [P] Prefeitura (city hall)
    [C] Câmara (city council)
    [T] City hall transparency portal
    [Y] City council transparency portal
    [N] None of the above
    [S] Skip
    [Q] Quit
  ''', 'pctynsq')
            # TODO: implement deletion if link type is none or broken
            if choice in ['n','s']: # none or skip
                continue
            elif choice == 'q': # quit
                signal = 'q'
                break
            elif choice == 'p': # prefeitura
                branch = 'executive'
            elif choice == 'c': # camara
                branch = 'legislative'
            verified_link = {
                'state_code': uf,
                'municipality_code': code,
                'municipality': name,
                'sphere': 'municipal',
                'branch': branch,
                'url': working_link.url, # update if redirected
                'last-verified-manual': datetime.utcnow()
            }
            verified_links.append(verified_link)
        else:
            print('  Error opening URL.')
    return signal, verified_links

def manual_verify(input_folder: str, input_file: str, data_package_path: str,
        max_quantity: int) -> pd.DataFrame:
    """Manually verifies links by opening each one of them on the browser
    for the user to check. Then asks the user to classify the link type.

    A Python function that does the same job as the script that is run
    from the command line.

    Args:
        input_folder (str): The folder containing the input table.
        input_file (str): Name of the file containing the input table in
            csv format.
        data_package_path (str): Path to the datapackage.json file.
        max_quantity (int): Maximum quantity of links to check.

    Returns:
        pd.DataFrame: Pandas dataframe containing the verified links.
    """
    candidates = get_candidate_links(
        file_path=os.path.join(input_folder, input_file),
        max_quantity=max_quantity)
    codes = candidates.code.unique()

    results = []
    print(f'Verifying candidate URLs for {max_quantity} cities...')
    for code in codes:
        signal, links_to_add = verify_city_links(candidates[candidates.code == code], code)
        if signal == 'q':
            print('Quitting...')
            break
        results.extend(links_to_add)

    # read resource to be updated
    table = get_output_to_be_merged(data_package_path)

    print('Updating values...')
    for result in results:
        # get existing data in file to be updated
        existing_data = table.loc[
                (table.municipality_code == result['municipality_code']) &
                (table.branch == result['branch'])
            ]
        if len(existing_data) > 0:
            row = existing_data.iloc[0].copy()
            for key in ['sphere', 'branch', 'url', 'last-verified-manual']:
                row[key] = result[key] # update the values
            table = table.append(row, ignore_index=True)
        else:
            table = table.append(result, ignore_index=True)

    # remove duplicate entries,
    # take into account only url column,
    # keep last entry to preserve the last-verified-auto timestamp
    table.drop_duplicates(subset='url', keep='last', inplace=True)
    table.sort_values(by=['state_code', 'municipality'], inplace=True)
    return table

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    options = parse_cli()
    table = manual_verify(**options)
    print(f'Recording {options["data_package_path"]}...')
    store_csv(table, options['data_package_path'])
