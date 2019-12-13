# 02-dbpedia-links.py
#
# This script interprets the URLs municipalities websites from
# DBPedia. At a later stage these URLs are used to find out the respective
# transparency portals.
# 
# Este script interpreta as URLs dos sites dos municípios a
# partir da DBPedia. Em uma etapa posterior essas URLs são usadas para
# encontrar os respectivos portais da transparência.
#

import re
import os
import urllib
import pandas as pd
from tableschema import Storage
from datapackage import Package

GEO_FOLDER = '../../../data/auxiliary/geographic'
GEO_FILE = 'municipality.csv'
OUTPUT_FOLDER = '../../../data/unverified'
OUTPUT_FILE = 'municipality-website-candidate-links.csv'

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


# do some cleaning

# remove URIs column
dbp_pt.drop('city', axis=1, inplace=True)

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
dbp_pt = dbp_pt.merge(mun)


# remove duplicate rows
dbp_pt.drop_duplicates(inplace=True)

# melt 4 types of links into one
dbp_pt = pd.melt(dbp_pt, id_vars=['name', 'uf', 'code'], var_name='link_type', value_name='link')
dbp_pt.drop_duplicates(inplace=True)

# remove empty lines and duplicate links
dbp_pt.dropna(subset=['link'], inplace=True)
dbp_pt.drop_duplicates(subset=['link'], keep='first', inplace=True)




# read data frame from English DBPedia
dbp = pd.read_csv(DBPEDIA_URL)


# do some cleaning

# remove URIs column
dbp.drop('city', axis=1, inplace=True)

# remove parenthesis and commas in city names
dbp['name'] = dbp.name.apply(
    lambda s: remove_parenthesis.match(s).group().strip()
)


# adjust the state (UF) abbreviations as the DBPedia data is inconsistent

# rename columns to match other dataset
dbp.rename(columns={'state_name': 'state'}, inplace=True)

# merge data frames to obtain state abbreviations from state names
dbp = dbp.merge(uf, on='state', how='left')

# obtain state from DBPedia abbreviation from
# lines with a state abbreviation but without a state name
dbp_abbr = dbp.abbr.isnull() & ~dbp.state_abbr.isnull()
dbp.loc[dbp_abbr,'abbr'] = dbp.loc[dbp_abbr].state_abbr.str.replace('BR-','')

# try to obtain still missing states from link url
dbp.loc[dbp.abbr.isnull(), 'abbr'] = (
    dbp.loc[dbp.abbr.isnull()]
    .link.str.extract(r'(\w{2})\.gov\.br$') # get state name
    .iloc[:,0].str.upper() # get it into uppercase
)

# rename/remove columns before melting
dbp.drop(['state_abbr','state'], axis=1, inplace=True)
dbp.rename(columns={'abbr': 'uf'}, inplace=True)

# melt 2 types of links into one
dbp = pd.melt(dbp, id_vars=['name', 'uf'], var_name='link_type', value_name='link')
dbp.drop_duplicates(inplace=True)

# merge with municipalities data frame to get the code based on name and uf
dbp = dbp.merge(mun, on=['name', 'uf'], how='left')




# combine data: concatenate the results
dbp_links = pd.concat([dbp, dbp_pt], sort=True)

# remove garbage links

# remove links to files
dbp_links = dbp_links[
    ~dbp_links.link.str.contains(r'\.(?:pdf|png|jpg)$', na=False, regex=True)
]

# remove generic links to IBGE
dbp_links = dbp_links[
    ~dbp_links.link.str.contains(r'ibge\.gov\.br\/?', na=False, regex=True)
]

# remove generic links to Blogspot
dbp_links = dbp_links[
    ~dbp_links.link.str.contains(r'blogspot\.com\/?', na=False, regex=True)
]

# remove generic links to Facebook
dbp_links = dbp_links[
    ~dbp_links.link.str.contains(r'facebook\.com\/?', na=False, regex=True)
]

# remove generic links to Yahoo
dbp_links = dbp_links[
    ~dbp_links.link.str.contains(r'yahoo\.com\/?', na=False, regex=True)
]

# remove generic links to state website
dbp_links = dbp_links[
    ~dbp_links.link.str.contains(r'//www\.\w{2}\.gov\.br\/?$', na=False, regex=True)
]

# remove Google trackers
google_trackers = dbp_links.link.str.contains(
    r'google\.com(?:\.br)?/url',
    na=False,
    regex=True
)
dbp_links.loc[google_trackers, 'link'] = dbp_links.loc[google_trackers].link.apply(
    lambda outer_url: urllib.parse.parse_qs(
        urllib.parse.urlparse(outer_url).query
    )['url'][0]
)

# remove empty links and duplicates
dbp_links.dropna(subset=['link'], inplace=True)
dbp_links.drop_duplicates(inplace=True)


# prepare output

# check if the output folder alredy does exist and, if not, create it
if not os.path.exists(OUTPUT_FOLDER):
    print(f'Output folder does not yet exist. Creating "{OUTPUT_FOLDER}"...')
    os.mkdir(OUTPUT_FOLDER)

output = os.path.join(OUTPUT_FOLDER, OUTPUT_FILE)
generated_df = dbp_links
# check whether if there is an existing file to merge
if os.path.exists(output):
    recorded_df = pd.read_csv(output)
    new_df = pd.concat([recorded_df, generated_df], sort=True)
else:
    new_df = generated_df.copy()
# remove duplicate entries
new_df.drop_duplicates(inplace=True)
# store the results
new_df.to_csv(output, index=False)

