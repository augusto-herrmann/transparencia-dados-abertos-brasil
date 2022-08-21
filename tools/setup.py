import os
from setuptools import setup

def read(*paths, encoding='utf-8'):
    """Read a text file."""
    basedir = os.path.dirname(__file__)
    fullpath = os.path.join(basedir, *paths)
    with open(fullpath, 'r', encoding=encoding) as file:
        contents = file.read().strip()
    return contents

INSTALL_REQUIRES = [
    'requests==2.28.1',
    'pandas==1.4.3',
    'tqdm==4.64.0',
    'beautifulsoup4==4.11.1',
    'frictionless==4.40.3',
    'Unidecode==1.3.4',
]

setup(
    name='transparency_opendata_br',
    version=read('VERSION'),
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
    install_requires=INSTALL_REQUIRES
)
