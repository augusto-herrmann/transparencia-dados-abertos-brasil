# 03-auto-verify-links.py
#
# This script crawls candidate URLs for municipalities websites and
# checks if they are active and likely to be the city hall or
# city council portals.
# 
# Este script navega nas URLs candidatas a sites dos municípios e
# verifica se elas estão ativas e são prováveis portais das prefeituras
# e câmaras municipais.
#

import re
import os
import urllib
import pandas as pd
from tqdm import tqdm
import requests
import random
from bs4 import BeautifulSoup
from unidecode import unidecode

INPUT_FOLDER = '../../data/unverified'
INPUT_FILE = 'municipality-website-candidate-links.csv'

candidates = pd.read_csv(os.path.join(INPUT_FOLDER, INPUT_FILE))
codes = candidates.code.unique()
random.shuffle(codes) # for testing
codes = codes[:4] # for testing
goodlinks = pd.DataFrame(columns=candidates.columns)

def healthy_link(link):
    'Check whether the link is healthy or not.'
    try:
        r = requests.get(link)
    except requests.exceptions.ConnectionError:
        r = None
    if r and r.status_code == 200:
        return r
    return False

def check_type(r, candidates):
    'Try to infer the type of site this is'
    soup = BeautifulSoup(r.text, 'html.parser')
    title = unidecode(soup.find('title').text.lower())
    link_types = candidates.link_type
    if 'prefeitura' in link_types:
        link_type = 'prefeitura'
    elif 'camara' in link_types:
        link_type = 'camara'
    elif 'prefeitura' in title:
        link_type = 'prefeitura'
    elif 'camara municipal' in title:
        link_type = 'camara'
    elif 'camara de' in title:
        link_type = 'camara'
    return link_type

with tqdm(total=len(codes)) as pbar:
    print (f'Cralwing candidate URLs for {len(codes)} cities...')
    for code in codes:
        city_links = candidates[candidates.code == code]
        for link in city_links.link.unique():
            working_link = healthy_link(link)
            if working_link:
                link_type = check_type(
                    working_link,
                    candidates[candidates.link==link]
                )
                goodlinks = goodlinks.append({
                    'code': code,
                    'link': link,
                    'link_type': link_type,
                    'name': city_links.name.iloc[0],
                    'uf': city_links.uf.iloc[0],
                }, ignore_index=True)
    pbar.update(1)

print(goodlinks)
