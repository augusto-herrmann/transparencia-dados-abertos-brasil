# manually-verify-links.py
#
# This script opens candidate URLs for municipalities websites in the
# web browser and asks the user to check whether or not they seem to be the
# official city hall or city council portals.
# 
# Este script abre no navegador as URLs candidatas a sites dos municípios e
# pede ao utilizador que verifique se elas parcem ser os portais das
# prefeituras e câmaras municipais.
#

import os
import argparse
import urllib
from datetime import datetime, timezone
import random
import warnings
import webbrowser

import pandas as pd
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from datapackage import Package

USER_AGENT = 'transparencia-dados-abertos-brasil/0.0.1'
INPUT_FOLDER = '../../data/unverified'
INPUT_FILE = 'municipality-website-candidate-links.csv'
OUTPUT_FOLDER = '../../data/valid'
OUTPUT_FILE = 'brazilian-municipality-and-state-websites.csv'

# Command line interface
parser = argparse.ArgumentParser(
    description='''Opens in a web browser candidate URLs for municipalities
    websites and asks the user to checks if they seem to be the city hall or
    city council portals.
    
Abre no navegador as URLs candidatas a sites dos municípios e  pede ao
    utilizador que verifique se elas parcem ser os portais das prefeituras e
    câmaras municipais.
    '''
    )

parser.add_argument('input',
                    help='input file in CSV format / arquivo em formato CSV',
                    default='',
                    nargs='?',
                    )
parser.add_argument('output',
                    help='input file in CSV format / arquivo em formato CSV',
                    default='',
                    nargs='?',
                    )
parser.add_argument('-q', '--quantity',
                    metavar='int', type=int,
                    help='maximum quantity of cities to process / quantidade máxima a processar',
                    default=0,
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
else:
    MAX_QUANTITY = None

candidates = pd.read_csv(os.path.join(INPUT_FOLDER, INPUT_FILE))
print (f'Found {len(candidates)} websites in {os.path.join(INPUT_FOLDER, INPUT_FILE)}.')
print (f'Encontrados {len(candidates)} sites em {os.path.join(INPUT_FOLDER, INPUT_FILE)}.')
codes = candidates.code.unique()
random.shuffle(codes) # randomize sequence
if MAX_QUANTITY:
    codes = codes[:MAX_QUANTITY] # take a subsample for shorter session
else:
    MAX_QUANTITY = len(codes)
goodlinks = pd.DataFrame(columns=candidates.columns)

def choose(text, options):
    'Asks the user to choose one of the defined options.'
    while True:
        key = input(text).lower()
        if key in options.lower():
            break
    return key

def healthy_link(link):
    'Check whether the link is healthy or not.'
    try:
        r = requests.get(link, headers={'user-agent': USER_AGENT})
    except (
        requests.exceptions.ConnectionError,
        requests.exceptions.InvalidURL
    ):
        r = None
    if r and r.status_code == 200:
        return r
    return False

def title_and_type(r, candidates):
    'Try to infer the type of site this is.'
    soup = BeautifulSoup(r.text, 'html.parser')
    title_tag = soup.find('title')
    if title_tag is None:
        return None
    title = unidecode(title_tag.text)
    link_types = candidates.link_type
    if 'prefeitura' in link_types:
        link_type = 'prefeitura'
    elif 'camara' in link_types:
        link_type = 'camara'
    elif 'prefeitura' in title.lower():
        link_type = 'prefeitura'
    elif 'municipio' in title.lower():
        link_type = 'prefeitura'
    elif 'camara municipal' in title.lower():
        link_type = 'camara'
    elif 'camara de' in title.lower():
        link_type = 'camara'
    else:
        warnings.warn(f'Unable to determine site type from title: “{title}”.')
        link_type = None
    return title, link_type

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
            print(f'  Returned stats code {working_link.status_code}')
            title, link_type = title_and_type(
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
                'last-verified-manual': (
                    datetime.now(timezone.utc)
                    .isoformat(timespec='seconds')
                    .replace('+00:00', 'Z')
                )
            }
            verified_links.append(verified_link)
        else:
            print('  Error opening URL.')
    return signal, verified_links

results = []
print (f'Verifying candidate URLs for {min(len(codes),MAX_QUANTITY)} cities...')
for code in codes[:MAX_QUANTITY]:
    signal, links_to_add = verify_city_links(candidates[candidates.code == code], code)
    if signal == 'q':
        print('Quitting...')
        break
    else:
        results.extend(links_to_add)

# read resource to be updated
package = Package(os.path.join(OUTPUT_FOLDER, 'datapackage.json'))
r = package.get_resource('brazilian-municipality-and-state-websites')
columns = r.schema.field_names
df = pd.DataFrame(r.read(), columns = columns)

print('Updating values...')
for result in results:
    for key in ['sphere', 'branch', 'url', 'last-verified-manual']:
        df.loc[df.municipality_code == result['municipality_code'], key] = \
            result[key] # update the value
    
output = os.path.join(OUTPUT_FOLDER, OUTPUT_FILE)
print(f'Recording {output}...')
generated_df = df
# check whether if there is an existing file to merge
if os.path.exists(output):
    recorded_df = pd.read_csv(output)
    new_df = pd.concat([recorded_df, generated_df], sort=True)
else:
    new_df = generated_df.copy()
# remove duplicate entries,
# take into account only url column,
# keep last entry to preserve the last-verified-auto timestamp
new_df.drop_duplicates(subset='url', keep='last', inplace=True)
# reorder columns
new_df = new_df[columns]
new_df.sort_values(by=['state_code', 'municipality'], inplace=True)
# store the results
new_df.to_csv(output, index=False)

