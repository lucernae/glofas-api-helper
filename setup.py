
from setuptools import setup, find_packages


setup(
    name='GloFAS-API-Wrapper',
    version='0.1',
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=[
        'GDAL>=2,<3',
        'owslib>=0.19',
        'lxml>=4'
    ]
)
