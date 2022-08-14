# archive-klein-2017.py
# 
# This script converts data from the Klein-2017 dataset in the archived
# format (used to be the main data in this repository) to the current format
# where state and municipal transparency and open data portals are represented
# in a single CSV resource.
# 
# Este script converte os dados do dataset Klein-2017, no formato arquivado
# (anteriormente era o conjunto de dados principal deste repositório) para o
# formato atual em que os portais de transparência e dados abertos dos estados
# e municípios estão representados em um único recurso CSV.
# 

import os
import pandas as pd
from frictionless import Package

INPUT_PATH = '../../../../data/archive'
INPUT_MUNICIPAL = 'portais-municipais.csv'
INPUT_STATE = 'portais-estaduais.csv'
OUTPUT_PATH = '../../../../data/valid'
OUTPUT_FILE = 'brazilian-transparency-and-open-data-portals.csv'
IBGE_CODE_PATH = '../../../../data/auxiliary/geographic'

# state portals
df_state = (
    pd.read_csv(os.path.join(INPUT_PATH,INPUT_STATE))
    .drop('uf_nome', axis=1)
    .rename(columns={'uf': 'state_code', 'tipo': 'type'})
)

df_state['sphere'] = 'state'
df_state['branch'] = 'executive'

# municipality portals

df_municipality = (
    pd.read_csv(os.path.join(INPUT_PATH,INPUT_MUNICIPAL))
    .drop('população', axis=1)
    .rename(columns={
        'uf': 'state_code',
        'município': 'municipality',
        'tipo': 'type',
        'observação': 'notes'
    })
)

df_municipality['sphere'] = 'municipal'
df_municipality['branch'] = 'executive'

# concatenate both sources

dp = Package(os.path.join(OUTPUT_PATH,'datapackage.json'))
fields = dp.get_resource('brazilian-transparency-and-open-data-portals').schema.fields
columns=[field.name for field in fields]

df = pd.concat([
        pd.DataFrame(columns=columns),
        df_state,
        df_municipality
], sort=False)

# look up municipal codes

geo_package = Package(os.path.join(IBGE_CODE_PATH, 'datapackage.json'))
municipalities = geo_package.get_resource('municipality').to_pandas()

municipalities.rename( # line up column names in preparation for merge
    columns={
        'uf': 'state_code',
        'name': 'municipality',
        'code': 'municipality_code'
    },
    inplace=True
)

df = (
    df.drop('municipality_code', axis=1) # discard original column
    .merge( 
        municipalities, 
        how='left', 
    )
)
df.municipality_code = df.municipality_code.astype('Int64') # keep as int
df = df[columns] # reorder columns

# merge existing data, if present

df.set_index('url', inplace=True)
if os.path.exists(os.path.join(OUTPUT_PATH,OUTPUT_FILE)):
    df_existing = pd.read_csv(
        os.path.join(OUTPUT_PATH,OUTPUT_FILE),
    ).set_index('url')
    df_new = pd.concat([
        df_existing,
        df
    ], sort=False)
else:
    df_new = df
df.reset_index(inplace=True)
df = df[columns] # reorder columns

df.to_csv(os.path.join(OUTPUT_PATH,OUTPUT_FILE), index=False)

