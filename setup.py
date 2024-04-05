from setuptools import setup

setup(
    name='AB-Connector-Bulk',
    version='0.0.01',
    description='This app will find and add all data from Allen-Bradley Controllers on the local network to the data-layer',
    author='SDK Team',
    install_requires = ['ctrlx-datalayer', 'pylogix', 'pycomm3'],    
    packages=['app', 'helper'],
    # https://stackoverflow.com/questions/1612733/including-non-python-files-with-setup-py
    package_data={'./': []},
    scripts=['main.py'],
    license='Copyright (c) 2020-2022 Bosch Rexroth AG, Licensed under MIT License'
)
