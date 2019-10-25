import os
import pandas as pd
from datapackage import Package

OUTPUT_FILE = '../../data/valid/brazilian-transparency-and-open-data-portals.csv'

# state portals
df_state = (
    pd.read_csv('../../data/archive/portais-estaduais.csv')
    .drop('uf_nome', axis=1)
    .rename(columns={'uf': 'state_code', 'tipo': 'type'})
)

# municipality portals

df_municipality = (
    pd.read_csv('../../data/archive/portais-municipais.csv')
    .drop('população', axis=1)
    .rename(columns={
        'uf': 'state_code',
        'município': 'municipality',
        'tipo': 'type',
        'observação': 'notes'
    })
)

# concatenate both sources

dp = Package('../../data/valid/datapackage.json')
fields = dp.get_resource('brazilian-transparency-and-open-data-portals').schema.fields
columns=[field.name for field in fields]

df = pd.concat([
        pd.DataFrame(columns=columns),
        df_state,
        df_municipality
], sort=False)

# merge existing data, if present

df.set_index('url', inplace=True)
if os.path.exists(OUTPUT_FILE):
    df_existing = pd.read_csv(
        OUTPUT_FILE,
    ).set_index('url')
    df_new = pd.concat([
        df_existing,
        df
    ], sort=False)
else:
    df_new = df
df.reset_index(inplace=True)
df = df[columns]

df.to_csv(OUTPUT_FILE, index=False)

