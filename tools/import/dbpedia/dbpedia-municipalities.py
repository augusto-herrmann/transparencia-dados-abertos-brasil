# dbpedia-municipalities.py
# 
# This script downloads and interprets the URLs municipalities websites from
# DBPedia. At a later stage these URLs are used to find out the respective
# transparency portals.
#
# Este script faz o download e interpreta as URLs dos sites dos municípios a
# partir da DBPedia. Em uma etapa posterior essas URLs são usadas para
# encontrar os respectivos portais da transparência.
#

import os, io
import urllib
import requests
import ftplib
from zipfile import ZipFile
from tqdm import tqdm
import pandas as pd
from tableschema import Storage
from datapackage import Package

TEMPORARY_FOLDER = 'download-cache'
DOWNLOAD_URL = 'ftp://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/divisao_territorial/2018/DTB_2018.zip'

IBGE_FILE_NAME = os.path.basename(urllib.parse.urlparse(DOWNLOAD_URL).path)

def download_file(folder, url):
    'Download a (large) file using a progress bar.'
    local_filename = os.path.join(folder,url.split('/')[-1])
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in tqdm(r.iter_content(chunk_size=8192)):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    # f.flush()
    return local_filename

def download_ftp_file(folder, url):
    'Download a file using the FTP protocol using a progress bar.'
    url = urllib.parse.urlparse(DOWNLOAD_URL)
    ftp = ftplib.FTP(url.netloc)
    ftp.login() # anonymous login
    ftp.cwd(os.path.dirname(url.path))
    filename = os.path.basename(url.path)
    size = ftp.size(filename)
    
    with open(os.path.join(folder, filename), 'wb') as downloaded:
        with tqdm(total=size, unit='B', unit_scale=True,
                  unit_divisor=1024) as progress:
            def download_chunk(data):
                progress.update(len(data))
                downloaded.write(data)
            ftp.retrbinary(
                f'RETR {filename}',
                download_chunk
            )


# check if folder and downloaded file alredy do exist and, if not, create /
# download them

if not os.path.exists(TEMPORARY_FOLDER):
    print(f'Temporary folder does not yet exist. Creating "{TEMPORARY_FOLDER}"...')
    os.mkdir(TEMPORARY_FOLDER)

if not os.path.exists(os.path.join(TEMPORARY_FOLDER, IBGE_FILE_NAME)):
    print(f'IBGE file does not yet exist. Downloading from "{DOWNLOAD_URL}"...')
    download_ftp_file(TEMPORARY_FOLDER, DOWNLOAD_URL)


# unpack the zipped file

with ZipFile(os.path.join(TEMPORARY_FOLDER, IBGE_FILE_NAME)) as pacote:
    with io.BytesIO(pacote.read('RELATORIO_DTB_BRASIL_MUNICIPIO.xls')) as f:
        df = pd.read_excel(
            f,
            dtype={
                'Nome_UF': 'category',
                'Nome_Mesorregião': 'category',
                'Nome_Microrregião': 'category'
            }
        )

# get the state (UF) codes as the IBGE DTB file does not contain them

geographic = Storage.connect('pandas')
package = Package('../../../data/auxiliary/geographic/datapackage.json')
package.save(storage=geographic)

# adjust column names and types
uf = geographic['uf'].rename(columns={'code': 'UF', 'abbr': 'Sigla_UF'})
uf['Sigla_UF'] = uf['Sigla_UF'].astype('category')

# merge back into the IBGE DTB data
df = df.merge(uf)


# clean and store auxiliary data

df.drop(
    [
        'UF',
        'Nome_UF',
        'Mesorregião Geográfica',
        'Nome_Mesorregião',
        'Microrregião Geográfica',
        'Nome_Microrregião',
        'Município'
    ],
    axis=1,
    inplace=True
)

df.rename(
    columns={
        'Código Município Completo': 'code',
        'Nome_Município': 'name',
        'Sigla_UF':'uf'
    },
    inplace=True
)

df.to_csv('../../../data/auxiliary/geographic/municipality.csv', index=False)

