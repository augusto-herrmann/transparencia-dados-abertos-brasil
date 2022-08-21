"""This script downloads and stores auxiliary data from IBGE about Brazilian
municipalities. This will be useful later for disambiguation and finding out
the municipality codes.

Usage:
  python ibge_municipalities.py

Este script faz o download e armazena dados auxiliares do IBGE sobre os
municípios. Isso será útil mais tarde para desambiguação e para descobrir
os códigos de municípios.
"""

import os, io, pathlib
import urllib
import requests
import ftplib
from zipfile import ZipFile
import logging

from tqdm import tqdm
import pandas as pd
from frictionless import Package

TEMPORARY_FOLDER = '../../../data/download-cache'
DOWNLOAD_URL = 'https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/divisao_territorial/2021/DTB_2021.zip'
OUTPUT_FOLDER = '../../../data/auxiliary/geographic'
OUTPUT_FILE = 'municipality.csv'

IBGE_FILE_NAME = os.path.basename(urllib.parse.urlparse(DOWNLOAD_URL).path)

def download_file(folder, url):
    'Download a (large) file using a progress bar.'
    local_filename = os.path.join(folder,url.split('/')[-1])
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with open(local_filename, 'wb') as file:
            for chunk in tqdm(response.iter_content(chunk_size=8192)):
                if chunk: # filter out keep-alive new chunks
                    file.write(chunk)
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

def fetch_ibge_spreadsheet(tmp_path: str,
    url: str) -> pd.DataFrame:
    """Check if folder and downloaded file already do exist and, if not,
    create and download them.

    Args:
        tmp_path (str): Temporary folder path.
        url (str): The url of the file to download.
    """
    file_name = os.path.basename(urllib.parse.urlparse(url).path)

    if not os.path.exists(tmp_path):
        logging.info('Temporary folder does not yet exist. Creating "%s"...', tmp_path)
        pathlib.Path(tmp_path).mkdir(parents=True, exist_ok=True)

    if not os.path.exists(os.path.join(tmp_path, file_name)):
        logging.info('IBGE file does not yet exist. Downloading from "%s"...', url)
        download_file(tmp_path, url)

    # unpack the zipped file
    with ZipFile(os.path.join(tmp_path, file_name)) as pacote:
        with io.BytesIO(pacote.read('RELATORIO_DTB_BRASIL_MUNICIPIO.xls')) as f:
            table = pd.read_excel(
                f,
                dtype={
                    'Nome_UF': 'category',
                    'Nome_Mesorregião': 'category',
                    'Nome_Microrregião': 'category'
                }
            )

    return table

def add_state_codes(table: pd.DataFrame) -> pd.DataFrame:
    """Get the state (UF) codes as the IBGE DTB file does not contain
    them.

    Args:
        table (pd.DataFrame): The original dataframe from IBGE spreadsheet.

    Returns:
        pd.DataFrame: The enriched dataframe with state codes.
    """
    package = Package(os.path.join(OUTPUT_FOLDER,'datapackage.json'))
    states = package.get_resource('uf').to_pandas()

    states = (
        states
        .rename(columns={'code': 'UF', 'abbr': 'Sigla_UF'})
        .drop('name', axis=1)
    )

    # adjust column names and types
    states['Sigla_UF'] = states['Sigla_UF'].astype('category')

    # merge back into the IBGE DTB data
    return table.merge(states)

def remove_and_rename_columns(table: pd.DataFrame) -> pd.DataFrame:
    """Remove unneeded columns and rename other columns according to
    our schema.

    Args:
        table (pd.DataFrame): The dataframe with municipality data.

    Returns:
        pd.DataFrame: The dataframe adapted to our schema.
    """
    table =(
        table
        .rename(columns={
            'Código Município Completo': 'code',
            'Nome_Município': 'name',
            'Sigla_UF':'uf'
        })
        .loc[:,['code', 'name', 'uf']]
        .sort_values(by='code')
    )

    return table

def merge_existing(table: pd.DataFrame, data_package_path: str) -> pd.DataFrame:
    """Merges with existing data.

    Args:
        table (pd.DataFrame): A Pandas dataframe with the new data.
        data_package_path (str): Path to the data package with exsiting
            data.

    Returns:
        pd.DataFrame: The pandas dataframe with the merged data.
    """
    # checks if the table already exists. If not, return just the new data
    data_package_file_name = os.path.join(data_package_path,
        'datapackage.json')
    if not os.path.exists(data_package_file_name):
        print(data_package_file_name)
        return table
    package = Package(data_package_file_name)
    resource = package.get_resource('municipality')
    resource_path = os.path.join(data_package_path, resource.path)
    if not os.path.exists(resource_path):
        print(resource_path)
        return table
    old_table = resource.to_pandas()
    # update rows that might have changed
    old_table.set_index('code').update(table.set_index('code'))
    # add new rows that might have been added
    new_values = table[~table.code.isin(old_table.code.unique())]
    return pd.concat([old_table, new_values])

if __name__ == '__main__':
    table = fetch_ibge_spreadsheet(TEMPORARY_FOLDER, DOWNLOAD_URL)
    table = add_state_codes(table)
    table = remove_and_rename_columns(table)
    table = merge_existing(table, OUTPUT_FOLDER)
    table.to_csv(os.path.join(OUTPUT_FOLDER, OUTPUT_FILE), index=False)
