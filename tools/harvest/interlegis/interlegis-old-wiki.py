import csv
import os
from urllib.parse import urlparse
import logging

import requests
from bs4 import BeautifulSoup

OUTPUT_FOLDER = '../../../data/unverified'
OUTPUT_FILE = 'municipality-website-candidate-links.csv'

SOURCE_URL = 'https://colab.interlegis.leg.br/wiki/CasasUsamPortalModelo?version=414#L1'

response = requests.get(SOURCE_URL)

if response.status_code != 200:
    raise ValueError(
        f'Request to {SOURCE_URL} failed with status code {response.code}'
        )

soup = BeautifulSoup(response.content, 'html.parser')

portals = [
    {
        # 'code': get_city_code(),
        'name': li.get_text().split('-')[0].strip(),
        'link': li.a['href'],
        'link_type': 'camara',
        'uf': urlparse(li.a['href']).hostname.split('.')[-3].upper(),
    } for li in soup.find(id='wikipage').find_all('li') \
        if li.find_next(id='Prefeituras') and \
            len(urlparse(li.a['href']).hostname.split('.')[-3]) == 2
]

portals.extend([
    {
        # 'code': get_city_code(),
        'link': li.a['href'],
        'link_type': 'prefeitura',
        'name': li.get_text().split('-')[0].strip(),
        'uf': urlparse(li.a['href']).hostname,
    } for li in soup.find(id='Prefeituras').find_next('ul').find_all('li')
])

logging.info("Read data about %s portals from Interlegis' old wiki.",
                                                        len(portals))

# with open(os.path.join(OUTPUT_FOLDER, OUTPUT_FILE), 'a') as f:
#     spamwriter = csv.DictWriter(f,fieldnames=portals[0].keys())
#     for portal in portals:
#         spamwriter.writerow(portal)
