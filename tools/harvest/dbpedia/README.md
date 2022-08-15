# DBPedia import scripts

These scripts import data from DBPedia. For more information on the rationale
and process, see the
[source description here](../../../sources/dbpedia/dbpedia.org.md).

## Usage

1. Create a Pyton virtual environment. This is not required, but it is
   recommended.
2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the scripts.

   First, gather the DBPedia identifier URI for each municipality:
   
   ```
   python 01-dbpedia-municipality-uris.py
   ```
   
   Then, try to find the official website property for each one of them:
   
   ```
   python 02-dbpedia-website-links.py
   ```

Note: Python 3 is required for this script. Tested on 3.8.10.
