import os
import argparse

from bs4 import BeautifulSoup

from harvest.scrapers import TransparencyPortalScraper


class FECAMRNScraper(TransparencyPortalScraper):
    source_url: str = "https://fecamrn.com.br/transparencias-das-camaras-municipais"

    def parse(self):
        """Parse list of city councils webpage."""
        soup = BeautifulSoup(self.web_content, "html.parser")
        links = [
            (p.text.title(), p.find_next("a")["href"])
            for p in soup.find("div", {"class": "texto"}).find_all("p")
            if p.text
        ]
        for name, url in links:
            self.append(
                state_code="RN",
                municipality=name,
                sphere="municipal",
                branch="legislative",
                url=url,
                type="SPT",
            )


def extract_fecamrn_portals(**kwargs):
    """Extract city council transparency portals by scraping FECAMRN's
    website.

    Args:
        output_folder (str): Path to write the output to.
        source_url (str): URL to FECAMRN's website.
    """
    scraper = FECAMRNScraper(**kwargs)
    scraper.harvest()
    scraper.resource.data = scraper.fill_municipal_codes(scraper.dataframe)
    scraper.save()


def parse_cli() -> dict:
    """Parses the command line interface.

    Returns:
        dict: A dict containing the values for data_package_path, url.
    """
    parser = argparse.ArgumentParser(
        description="""Scrapes candidate URLs for council portals """
        """from FECAMRN's website."""
    )
    parser.add_argument(
        "output",
        help=("path to write the extracted csv to"),
        default="",
        nargs="?",
    )
    parser.add_argument(
        "url",
        help=("URL for the FECAMRN website"),
        default="",
        nargs="?",
    )
    params = {}
    args = parser.parse_args()
    if args.output:
        params["output_folder"] = args.output
    if args.output and not os.path.exists(args.output):
        raise FileNotFoundError(f"Folder not found: {args.output}")
    params["source_url"] = args.url if args.url else FECAMRNScraper.source_url
    return params


if __name__ == "__main__":
    options = parse_cli()
    extract_fecamrn_portals(**options)
