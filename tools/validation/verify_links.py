"""Common code for link verification scripts in data validation.
"""
import logging
import random
import re
from typing import Tuple

import requests
import pandas as pd
from bs4 import BeautifulSoup
from unidecode import unidecode
from frictionless import Package

from settings import USER_AGENT, DEFAULT_TIMEOUT as TIMEOUT

WEBSITE_RESOURCE_NAME = 'brazilian-municipality-and-state-websites'

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

def get_title_and_type(
    response: requests.Response,
    candidates: pd.DataFrame) -> Tuple[str, str]:
    """Try to infer the type of site this is.

    Args:
        response (requests.Response): The Response object obtained when
            crawling the page.
        candidates (pd.DataFrame): The Pandas dataframe slice containing
            the candidate links.

    Returns:
        Tuple[str, str]: The page title and link type category.
    """
    soup = BeautifulSoup(response.text, 'html.parser')
    title_tag = soup.find('title')
    if title_tag is None:
        return None, None
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
    return title_tag.text, link_type

def get_candidate_links(file_path: str, max_quantity: int) -> pd.DataFrame:
    """Reads the csv table containing the candidate links.

    Args:
        file_path (str): The path to the csv file.
        max_quantity (int): The maximum number of entries to read. If
            `None`, returns all the data. If less than the number of
            entries in the file, selects a sample of this site.

    Returns:
        pd.DataFrame: The Pandas dataframe containing the read table.
    """
    candidates = pd.read_csv(file_path)
    logging.info('Found %d websites in %s.', len(candidates), file_path)
    codes = candidates.code.unique()
    random.shuffle(codes) # randomize sequence
    if max_quantity:
        codes = codes[:max_quantity] # take a subsample for quicker processing
    return candidates[candidates.code.isin(codes)]

def get_output_to_be_merged(data_package_path: str) -> pd.DataFrame:
    """Gets the dataframe for merging the output with.

    Args:
        data_package_path (str): The path to the data package.

    Returns:
        pd.DataFrame: The dataframe with the data.
    """
    package = Package(data_package_path)
    resource = package.get_resource(WEBSITE_RESOURCE_NAME)
    return resource.to_pandas()

def store_csv(table: pd.DataFrame, data_package_path: str):
    """Stores the csv file in the output folder.

    Args:
        table (pd.DataFrame): The dataframe containing the data.
        data_package_path (str): Path to the data package.
    """
    package = Package(data_package_path)
    resource = package.get_resource(WEBSITE_RESOURCE_NAME)
    output = resource.fullpath # filename of csv to write
    logging.info('Recording %s...', output)
    # store the file
    table.to_csv(output, index=False, date_format='%Y-%m-%dT%H:%M:%SZ')
