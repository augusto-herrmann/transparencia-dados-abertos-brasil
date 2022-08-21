import os

def read(*paths, encoding='utf-8'):
    """Read a text file."""
    basedir = os.path.dirname(__file__)
    fullpath = os.path.join(basedir, *paths)
    with open(fullpath, 'r', encoding=encoding) as file:
        contents = file.read().strip()
    return contents

VERSION = read('VERSION')
USER_AGENT = f'transparencia-dados-abertos-brasil/{VERSION}'
DEFAULT_TIMEOUT = 20
