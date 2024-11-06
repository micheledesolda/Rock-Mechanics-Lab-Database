# setup.py
from setuptools import setup, find_packages

setup(
    name='Rock_Mechanics_Lab_Database',
    version='0.1',
    packages=find_packages(where='rock_mechanics_lab_database'),
    package_dir={'': 'rock_mechanics_lab_database'},
)