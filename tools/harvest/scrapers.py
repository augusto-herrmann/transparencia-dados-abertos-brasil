from abc import ABC, abstractmethod
import os
import unicodedata
import logging

import requests
import pandas as pd
from frictionless import Package, Resource, Schema

from settings import USER_AGENT, DEFAULT_TIMEOUT as TIMEOUT


def remove_accents(text: str) -> str:
    """Remove accents from text.

    Args:
        text (str): The text to remove accents from.

    Returns:
        str: The text without accents.
    """
    return "".join(
        char
        for char in unicodedata.normalize("NFD", text)
        if not unicodedata.combining(char)
    )


class Harvester(ABC):
    """Base class for harvesting data sources."""

    output_folder: str
    output_file: str
    schema: Schema
    title: str = None
    description: str = None

    def __init__(
        self,
        title: str = None,
        description: str = None,
        schema: Schema = None,
        output_folder: str = "data/unverified",
    ):
        if title:
            self.title = title
        if description:
            self.description = description
        if schema:
            self.schema = schema
        if self.schema:
            self.resource = Resource(
                pd.DataFrame(columns=[field.name for field in schema.fields]),
                schema=schema,
                title=self.title,
                description=self.description,
            )
        else:
            self.resource = Resource(
                pd.DataFrame(),
                title=self.title,
                description=self.description,
            )
        self.output_folder = output_folder

    @property
    def dataframe(self) -> pd.DataFrame:
        """Shortcut to the resource data frame, containing the data
        harvested so far.

        Returns:
            pd.DataFrame: Data harvested
        """
        return self.resource.data

    def append(self, **kwargs):
        """Append a row to the data frame."""
        self.dataframe.loc[len(self.dataframe)] = kwargs

    @abstractmethod
    def harvest(self):
        """Harvest the data."""

    @property
    @abstractmethod
    def reference_data(self):
        """Handle for the data frame of reference data that is going
        to be updated."""
        return None

    @property
    def municipality(self):
        """Returns the auxiliary data resource for municipalities."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        aux_data_dir = os.path.join(
            current_dir, "..", "..", "data", "auxiliary", "geographic"
        )
        geographic = Package(os.path.join(aux_data_dir, "datapackage.json"))
        return geographic.get_resource("municipality")

    def fill_municipal_codes(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Fill municipal codes in harvested data based on state code and
        normalized municipality name.

        Args:
            frame (pd.DataFrame): Data frame without municipality codes.

        Returns:
            pd.DataFrame: Data frame with appropriate municipality codes.
        """
        frame["normalized_name"] = (
            frame["municipality"].str.lower().apply(remove_accents)
        )
        frame = frame.drop(["municipality", "municipality_code"], axis=1)
        codes = self.municipality.to_pandas().loc[:, ["uf", "name", "code"]]
        codes["normalized_name"] = codes["name"].str.lower().apply(remove_accents)
        codes = codes.rename(
            columns={
                "uf": "state_code",
                "name": "municipality",
                "code": "municipality_code",
            }
        )
        merged = frame.merge(codes, on=["state_code", "normalized_name"])
        merged = merged.reindex(
            columns=[field.name for field in self.resource.schema.fields]
        )
        return merged

    def save(self):
        """Saves the file with candidate links."""
        output_file_path = os.path.join(self.output_folder, self.output_file)
        logging.info("Writing file: %s", output_file_path)
        self.resource.data.to_csv(output_file_path, index=False)


class DataScraper(Harvester, ABC):
    """Harvester for scraping data off websites."""

    source_url: str
    web_content: str

    def __init__(self, *args, source_url: str = None, **kwargs):
        self.web_content = None
        if source_url:
            self.source_url = source_url
        super().__init__(*args, **kwargs)

    def fetch(self, url: str):
        """Fetches the website content from source and keeps it in the
        DataScraper object.
        """
        response = requests.get(
            url, headers={"user-agent": USER_AGENT}, timeout=TIMEOUT
        )
        response.raise_for_status()
        self.web_content = response.content

    @abstractmethod
    def parse(self):
        """Parse the page content and store it in the data frame."""

    def harvest(self):
        """Scrape the data by fetching and parsing the content of the
        web page."""
        self.fetch(self.source_url)
        self.parse()


class WebsiteLinkScraper(DataScraper):
    """Harvester for scraping institutional website links."""

    output_file: str = "municipality-website-candidate-links.csv"

    def __init__(self, *args, **kwargs):
        self.schema = self.municipality_website.schema
        super().__init__(*args, schema=self.schema, **kwargs)

    @property
    def municipality_website(self):
        """Returns the valid data resource for institutional websites."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        valid_data_dir = os.path.join(current_dir, "..", "..", "data", "valid")
        valid = Package(os.path.join(valid_data_dir, "datapackage.json"))
        return valid.get_resource("brazilian-municipality-and-state-websites")

    @property
    def reference_data(self):
        """Reference data is the municipality websites resource."""
        return self.municipality_website


class TransparencyPortalScraper(DataScraper):
    """Harvester for scraping transparency portal links."""

    output_file: str = "municipality-transparency-portals-candidate-links.csv"

    def __init__(self, *args, **kwargs):
        self.schema = self.transparency_portal.schema
        super().__init__(*args, schema=self.schema, **kwargs)

    @property
    def transparency_portal(self):
        """Returns the valid data resource for transparency portals."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        valid_data_dir = os.path.join(current_dir, "..", "..", "data", "valid")
        valid = Package(os.path.join(valid_data_dir, "datapackage.json"))
        return valid.get_resource("brazilian-transparency-and-open-data-portals")

    @property
    def reference_data(self):
        """Reference data is the municipality transparency portals resource."""
        return self.transparency_portal
