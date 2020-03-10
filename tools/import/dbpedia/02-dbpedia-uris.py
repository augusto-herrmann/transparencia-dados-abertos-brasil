# 02-dbpedia-uris.py
#
# This script fetches the municipalities URIs from DBPedia.
# 
# Este script traz as URIs de municípios da DBPedia.
#

import re
import os
import urllib
import pandas as pd
from tableschema import Storage
from datapackage import Package

GEO_FOLDER = '../../../data/auxiliary/geographic'
GEO_FILE = 'municipality.csv'
OUTPUT_FOLDER = '../../../data/auxiliary/geographic'
OUTPUT_FILE = 'municipality.csv'

remove_parenthesis = re.compile(r'[^(,]+')

# read SPARQL queries
with open ('dbpedia-pt.sparql', 'r') as f:
    DBPPT_SPARQL_CSV = urllib.parse.urlencode({'query':f.read()})
with open ('dbpedia.sparql', 'r') as f:
    DBP_SPARQL_CSV = urllib.parse.urlencode({'query':f.read()})
DBPEDIA_PT_URL = f'http://pt.dbpedia.org/sparql?default-graph-uri=&{DBPPT_SPARQL_CSV}&should-sponge=&format=text%2Fcsv&timeout=0&debug=on'
DBPEDIA_URL = f'http://dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fdbpedia.org&{DBP_SPARQL_CSV}&format=text%2Fcsv&CXML_redir_for_subjs=121&CXML_redir_for_hrefs=&timeout=30000&debug=on&run=+Run+Query+'

# read data frame from Portuguese DBPedia
dbp_pt = pd.read_csv(DBPEDIA_PT_URL)


# remove links column
dbp_pt.drop('link', axis=1, inplace=True)

# remove parenthesis in city names
dbp_pt['name'] = dbp_pt.name.apply(
    lambda s: remove_parenthesis.match(s).group().strip()
)


# get the state (UF) abbreviations as the DBPedia data does not contain them
geographic = Storage.connect('pandas')
package = Package(os.path.join(GEO_FOLDER,'datapackage.json'))
package.save(storage=geographic)

# adjust column names and types
uf = geographic['uf'].rename(columns={'name': 'state'})
uf.drop('code', axis=1, inplace=True)
uf['state'] = uf['state'].astype('category')

# merge back into the DBPedia data
dbp_pt = dbp_pt.merge(uf)
dbp_pt.drop('state', axis=1, inplace=True)
dbp_pt.rename(columns={'abbr': 'uf'}, inplace=True)


# get the municipality codes as the DBPedia data does not contain them
mun = geographic['municipality']

# merge the data
mun_URI =  mun.merge( 
    dbp_pt.loc[:, dbp_pt.columns.isin(['city', 'name', 'uf'])] 
    .rename(columns={'city': 'URI'}), # proper column name
    on=['name', 'uf'], # keys for the join operation
    how='left' # keep the keys from mun dataframe even if not found on dbp_pt
).drop_duplicates(subset=['code'], keep='first') # remove duplicate rows

# do some cleaning


# write back the csv
mun_URI.to_csv(os.path.join(OUTPUT_FOLDER, OUTPUT_FILE), index=False)

