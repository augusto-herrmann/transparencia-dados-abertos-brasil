from setuptools import setup

setup(
    name='transparency_opendata_br',
    version='0.0.2',
    author='Augusto Herrmann',
    author_email='augusto+github@herrmann.tech',
    packages=['.'],
    license='LICENSE.txt',
    description=("A survey of Brazilian states' and municipalities' "
        "transparency and open data portals, as well as institutional "
        "websites, obtained from several public data sources."),
    project_urls={
        'Source': 'https://github.com/augusto-herrmann/transparencia-dados-abertos-brasil/',
        'Tracker': 'https://github.com/augusto-herrmann/transparencia-dados-abertos-brasil/issues'
    },
    install_requires=[
        'requests==2.28.1',
        'pandas==1.4.3',
        'tqdm==4.64.0',
        'beautifulsoup4==4.11.1',
        'frictionless==4.40.3',
        'Unidecode==1.3.4',
    ]
)
