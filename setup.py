from setuptools import setup, find_packages
from os import path
from io import open


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'MysqlORM',
    version = '0.1',
    description = 'A simple ORM MySQL operation Library, running on Python3.',
    long_description = long_description,
    long_description_content_type='text/markdown',
    url = 'https://github.com/cirlmcesc/mysqlorm',
    author = 'Cirlmcesc Ma',
    author_email = 'cirlmcesc_ma@163.com',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: Chinese',
        'Operating system :: MacOs',
        'Operating system :: Microsoft',
        'Operating system :: Unix',
        'Topic :: Software Development :: Mysql operation Library',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords = 'mysql orm',
    packages = find_packages(),
    install_requires = ['pymysql',],
    extras_require={
        'dev': [],
        'test': [],
    },
    package_data={},
    data_files=[],
    entry_points={},
    project_urls = {},
)