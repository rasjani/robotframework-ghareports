# -*- coding: utf-8 -*-

from codecs import open
from os.path import join, abspath, dirname

from setuptools import setup, find_packages

CWD = abspath(dirname(__file__))
PACKAGE_NAME='robotframework-ghareports'

# Get the long description from the README file
with open(join(CWD, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Get version
CWD = abspath(dirname(__file__))

with open(join(CWD, 'requirements.txt'), encoding="utf-8") as f:
    REQUIREMENTS = f.read().splitlines()

CLASSIFIERS='''
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: Developers
Intended Audience :: End Users/Desktop
Intended Audience :: Information Technology
Intended Audience :: System Administrators
Programming Language :: Python :: 3
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3.9
Topic :: Software Development :: Libraries
Topic :: Software Development :: Quality Assurance
Topic :: Software Development :: Testing
Topic :: Utilities
'''.strip().splitlines()

setup(name="{}".format(PACKAGE_NAME.lower()),
      version="0.0.3",
      description='Simple github action summary report for robotframework',
      long_description=long_description,
      long_description_content_type='text/markdown',
      classifiers=CLASSIFIERS,
      url='https://github.com/rasjani/{}'.format(PACKAGE_NAME.lower()),
      author='Jani Mikkonen',
      author_email='jani.mikkonen@gmail.com',
      license='GPLV3',
      packages=[PACKAGE_NAME],
      package_dir={PACKAGE_NAME: 'src/'},
      install_requires=REQUIREMENTS,
      zip_safe=True)
