# 03-crawler-validation.py
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

INPUT_FOLDER = '../../../data/unverified'
INPUT_FILE = 'municipality-website-candidate-links.csv'

candidates = pd.read_csv(os.path.join(INPUT_FOLDER, INPUT_FILE))

with tqdm(total=len(candidates)) as pbar:
    print (f'Cralwing {len(candidates)} candidate URLs...')
    for index, candidate in candidates.iterrows():
        pbar.update(1)


