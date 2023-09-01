"""
Python packaging infrasctructure.

This file defines how the python package for the template module will be
constructed. It feeds descriptive information, dependencies, and entry points
for console applications to the python packaging services.
"""
import pathlib
import shutil
import sys
from setuptools import setup, find_packages

SCRIPT_PATH = pathlib.Path(__file__).resolve().parent

readme = SCRIPT_PATH.joinpath('README.md').read_text()
bb_license = SCRIPT_PATH.joinpath('LICENSE').read_text()
shutil.copyfile('README.md', 'template/README.md')
shutil.copyfile('LICENSE', 'template/LICENSE')

setup(
  name='template',
  version='0.0.1',
  description='template',
  long_description=readme,
  license=bb_license,
  long_description_content_type='text/markdown',
  url=('https://bitbucket.org/lukerr/template/src/main/'),
  author='Luciano Ricotta',
  entry_points={
    'console_scripts': [
      'template=template.cli.template:main',
      ],
    },
  classifiers=[
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'License :: 2023 Almania',
    'Natural Language :: English',
    'Programming Language :: Python :: 3.10',
    ],
  keywords='template',
  packages=find_packages(),
  setup_requires=[],
  tests_require=[],
  package_data={
    'template': [
      'README.md', 'LICENSE']},
  include_package_data=True
  )
