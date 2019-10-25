from dataflows import Flow, load, dump_to_path, add_metadata, printer
from dataflows import add_field, delete_fields

def portais_estaduais_csv():
    'Process the portais-estatuais.csv file from the archive into the valid schema.'
	
    def transform_schema(row):
        row['type'] = row['tipo']
	
    flow = Flow(
        # Load inputs
        load('../../data/archive/portais-estaduais.csv', format='csv', ),
        # Process them (if necessary)
		add_field('type', 'string', lambda row: row['tipo']),
		delete_fields(['uf_nome', 'tipo']),
        # Save the results
        # TODO: get the metadata from the intended output datapackage instead
        add_metadata(name='brazilian-transparency-and-open-data-portals', title='''Brazilian Transparency and Open Data Portals'''),
        printer(),
        # TODO: change to real path once the schema & merging part are done
        dump_to_path('brazilian-transparency-and-open-data-portals'),
    )
    flow.process()

# TODO:
def portais_municipais_csv():
    'Process the portais-municipais.csv file from the archive into the valid schema.'
    pass

if __name__ == '__main__':
    portais_estaduais_csv()
    #portais_municipais_csv()
