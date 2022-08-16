# auto_verify_links.py
#
# This script crawls candidate URLs for municipalities websites and
# checks if they are active and likely to be the city hall or
# city council portals.
#
# Usage:
#   python auto_verify_links.py
# 
# Este script navega nas URLs candidatas a sites dos municípios e
# verifica se elas estão ativas e são prováveis portais das prefeituras
# e câmaras municipais.
#

import os
import argparse
import re
from datetime import datetime
import random
import warnings
import multiprocessing
from functools import partial

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

# Command line interface
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
                    help='output file in CSV (must have a schema in datapackage.json)',
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
args = parser.parse_args()
if args.input:
    INPUT_FOLDER = os.path.dirname(args.input)
    INPUT_FILE = os.path.basename(args.input)
if args.output:
    OUTPUT_FOLDER = os.path.dirname(args.output)
    OUTPUT_FILE = os.path.basename(args.output)
if args.quantity:
    MAX_QUANTITY = args.quantity
if args.processes:
    MAX_SIMULTANEOUS = args.processes

candidates = pd.read_csv(os.path.join(INPUT_FOLDER, INPUT_FILE))
print (f'Found {len(candidates)} cities in {os.path.join(INPUT_FOLDER, INPUT_FILE)}.')
codes = candidates.code.unique()
random.shuffle(codes) # randomize sequence
if MAX_QUANTITY:
    codes = codes[:MAX_QUANTITY] # take a subsample for quicker processing
goodlinks = pd.DataFrame(columns=candidates.columns)

def healthy_link(link):
    'Check whether the link is healthy or not.'
    try:
        r = requests.get(
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
        r = None
    if r and r.status_code == 200:
        return r
    return False

def check_type(r, candidates):
    'Try to infer the type of site this is.'
    soup = BeautifulSoup(r.text, 'html.parser')
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
        warnings.warn(f'Unable to determine site type from title: “{title}”.')
        link_type = None
    return link_type

def verify_city_links(candidates, code):
    'Verify links for a city with a given code.'
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

def in_chunks(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

pool = multiprocessing.Pool(processes=MAX_SIMULTANEOUS)

with tqdm(total=len(codes)) as pbar:
    print (f'Cralwing candidate URLs for {len(codes)} cities...')
    for chunk in in_chunks(codes, MAX_SIMULTANEOUS):
        results = pool.map(partial(verify_city_links, candidates), chunk)
        for result in results:
            for verified_link in result:
                goodlinks = goodlinks.append(verified_link, ignore_index=True)
        pbar.update(MAX_SIMULTANEOUS)

# record validated

# read schema
package = Package(os.path.join(OUTPUT_FOLDER, 'datapackage.json'))
resource = package.get_resource('brazilian-municipality-and-state-websites')
df = resource.to_pandas()

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

print('Updating values...')
for index, result in goodlinks.iterrows():
    # get existing data in file to be updated
    existing_data = df.loc[
            (df.municipality_code == result['municipality_code']) &
            (df.branch == result['branch'])
        ]
    if len(existing_data) > 0:
        row = existing_data.iloc[0].copy()
        for key in ['sphere', 'branch', 'url', 'last-verified-auto']:
            row[key] = result[key] # update the values
        df = df.append(row, ignore_index=True)
    else:
        df = df.append(result, ignore_index=True)

output = resource.path # filename of csv to write
print(f'Recording {output}...')
# remove duplicate entries,
# take into account only url column,
# keep last entry to preserve the last-verified-auto timestamp
df.drop_duplicates(subset='url', keep='last', inplace=True)
df.sort_values(by=['state_code', 'municipality'], inplace=True)
# store the results
df.to_csv(output, index=False, date_format='%Y-%m-%dT%H:%M:%SZ')
