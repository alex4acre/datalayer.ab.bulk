from setuptools import setup

setup(
    name='sdk-py-datalayer-provider',
    version='2.4.0',
    description='This sample shows how to provide data to ctrlX Data Layer',
    author='SDK Team',
    install_requires = ['ctrlx-datalayer', 'pylogix'],    
    packages=['app', 'helper'],
    # https://stackoverflow.com/questions/1612733/including-non-python-files-with-setup-py
    package_data={'./': []},
    scripts=['main.py'],
    license='Copyright (c) 2020-2022 Bosch Rexroth AG, Licensed under MIT License'
)
