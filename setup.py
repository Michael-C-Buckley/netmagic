# NetMagic Setup

from setuptools import setup, find_packages

from netmagic.VERSION import __version__

DESCRIPTION = 'Project NetMagic',
LONG_DESCRIPTION = 'Project NetMagic'

setup(
    name='NetMagic',
    author='Michael Buckley',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    version=__version__,
    packages=find_packages(),
    install_requires=[
        'netmiko',
        'mactools',
        'pydantic',
        'textfsm',
    ],
    keywords=['networking','network','ssh','cli','api','automation']
)