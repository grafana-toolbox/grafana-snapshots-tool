from grafana_snapshots.constants import (PKG_NAME, PKG_VERSION)
from setuptools import setup, find_packages

# Global variables
name = PKG_NAME
version = PKG_VERSION
requires = [
    'grafana-api'
]

setup(
    name=name,
    version=version,
    description='A Python-based application to build Grafana snapshots using the Grafana API and grafana-api python interface',
    long_description_content_type='text/markdown',
    long_description=open('README.md', 'r').read(),
    author="author",
    author_email="jfpik78@gmail.com",
    url="https://github.com/peekjef72/grafana-snapshots-tool",
    entry_points={
        'console_scripts': [
            'grafana-snapshots = grafana_snapshots.cli:main'
        ]
    },
    packages=find_packages(),
    install_requires=requires,
    package_data={'': ['conf/*']},
)
