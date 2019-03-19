# -*- coding: utf-8 -*-

import argparse

parser = argparse.ArgumentParser(
    description='Exporta as planilhas CSV para o formato texto markdown do colaboradados.'
    )

parser.add_argument('entrada', help='arquivo de entrada no formato CSV')
parser.add_argument('-e', '--estaduais',
                    help='processa planilhas estaduais',
                    default=False,
                    action='store_true'
                    )
parser.add_argument('-m', '--municipais',
                    help='processa planilhas municipais',
                    action='store_true',
                    default=True
                    )

args = parser.parse_args()

if args.estaduais:
    args.municipais = False

portal_type = {
    'SPT': 'Portal da Transparência',
    'PTDAG': 'Portal da Transparência e Dados Abertos',
    'PEDAG': 'Portal de Dados Abertos'
}

output = ''

import rows

if args.estaduais:
    states = rows.import_from_csv(args.entrada)
    for state in states:
        output += '## {}\n\n'.format(state.uf_nome)
        name = portal_type[state.tipo.strip()] + ' do Estado de ' + state.uf_nome
        output += '-  **[{}]({})**: {}\n\n'.format(name, state.url, state.url)
elif args.municipais:
    cities = rows.import_from_csv(args.entrada)
    states = set([city.uf.upper() for city in cities])
    for state in sorted(states):
        output += '## {}\n\n'.format(state)
        for city in (city for city in cities if city.uf==state and city.url.strip()):
            output += '### {}\n\n'.format(city.municipio)
            name = portal_type[city.tipo.strip()] + ' do Município de ' + city.municipio
            output += '-  **[{}]({})**: {}\n\n'.format(name, city.url, city.url)
            if city.observacao.strip():
                output += '*Observação:* {}\n\n'.format(city.observacao.strip())
        output += '\n'

print(output)
