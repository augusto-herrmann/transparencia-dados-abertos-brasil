# klein_2017.py
# 
# This script converts data from the Klein-2017 dataset in the archived
# format (used to be the main data in this repository) to the current format
# where state and municipal transparency and open data portals are represented
# in a single CSV resource.
#
# Usage:
#   python klein_2017.py
# 
# Este script converte os dados do dataset Klein-2017, no formato arquivado
# (anteriormente era o conjunto de dados principal deste repositório) para o
# formato atual em que os portais de transparência e dados abertos dos estados
# e municípios estão representados em um único recurso CSV.
# 

import os
from typing import List

import pandas as pd
from frictionless import Package

INPUT_PATH = '../../../../data/archive'
INPUT_MUNICIPAL = 'portais-municipais.csv'
INPUT_STATE = 'portais-estaduais.csv'
OUTPUT_PATH = '../../../../data/valid'
OUTPUT_FILE = 'brazilian-transparency-and-open-data-portals.csv'
IBGE_CODE_PATH = '../../../../data/auxiliary/geographic'

def get_schema() -> List[str]:
    """Gets the column names from the data schema.

    Returns:
        List(str): The list of column names.
    """
    package = Package(os.path.join(OUTPUT_PATH,'datapackage.json'))
    fields = package.get_resource('brazilian-transparency-and-open-data-portals').schema.fields
    return [field.name for field in fields]

def get_state_dataframe(input_path: str, file_name: str):
    """Obtains a state data portals dataframe from the specified csv file.

    Args:
        input_path (str): Path to the csv file.
        file_name (str): Name of the csv file.

    Returns:
        pd.DataFrame: A dataframe containing the state data.
    """
    # state portals
    df_state = (
        pd.read_csv(os.path.join(input_path, file_name))
        .drop('uf_nome', axis=1)
        .rename(columns={'uf': 'state_code', 'tipo': 'type'})
    )

    df_state['sphere'] = 'state'
    df_state['branch'] = 'executive'

    return df_state

def get_municipality_dataframe(input_path: str, file_name: str):
    """Obtains a municipality data portals dataframe from the specified
    csv file.

    Args:
        input_path (str): Path to the csv file.
        file_name (str): Name of the csv file.

    Returns:
        pd.DataFrame: A dataframe containing the state data.
    """
    df_municipality = (
        pd.read_csv(os.path.join(input_path, file_name))
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

    return df_municipality

def concatenate_sources(dataframes: List[pd.DataFrame]) -> pd.DataFrame:
    """Concatenate Pandas dataframes using the data schema from the
    output table.

    Args:
        dataframes (List[pd.DataFrame]): A list of dataframes to be
            concatenated.

    Returns:
        pd.DataFrame: The dataframe in the output schema containing the
            concatenated data from the input dataframes.
    """
    columns = get_schema()

    return pd.concat([
            pd.DataFrame(columns=columns),
            *dataframes
    ], sort=False)

def set_municipal_codes(table: pd.DataFrame) -> pd.DataFrame:
    """Looks up and sets the municipal codes (IBGE) for each
    municipality in the dataframe.

    Args:
        table (pd.DataFrame): The dataframe with original data.

    Returns:
        pd.DataFrame: The resulting dataframe including municipal codes.
    """
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

    table = (
        table.drop('municipality_code', axis=1) # discard original column
        .merge(
            municipalities,
            how='left'
        )
    )
    table.municipality_code = table.municipality_code.astype('Int64') # keep as int
    columns = get_schema()
    table = table[columns] # reorder columns

    return table

def save_and_merge_existing_data(table: pd.DataFrame, output_path: str,
    file_name: str):
    """Saves the dataframe, merging existing data, if present.

    Args:
        table (pd.DataFrame): The dataframe to save do disk.
        output_path (str): The path where to save the file.
        file_name(str): The name of the file to be saved or merged.
    """
    index_columns = ['state_code', 'municipality_code', 'sphere', 'branch']
    if os.path.exists(os.path.join(output_path, file_name)):
        package = Package(os.path.join(output_path, 'datapackage.json'))
        df_existing = (
            package
            .get_resource('brazilian-transparency-and-open-data-portals')
            .to_pandas()
            .set_index(index_columns)
        )
        df_existing.update(table.set_index(index_columns))
        table = df_existing.reset_index()
    columns = get_schema()
    table = table[columns] # reorder columns

    table.to_csv(os.path.join(output_path, file_name), index=False)

if __name__ == '__main__':
    df = set_municipal_codes(
        concatenate_sources([
            get_state_dataframe(INPUT_PATH, INPUT_STATE),
            get_municipality_dataframe(INPUT_PATH, INPUT_MUNICIPAL)
        ])
    )
    save_and_merge_existing_data(df, OUTPUT_PATH, OUTPUT_FILE)
