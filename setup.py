"""
Python packaging infrasctructure.

This file defines how the python package for the bot module will be
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
shutil.copyfile('README.md', 'bot/README.md')
shutil.copyfile('LICENSE', 'bot/LICENSE')
shutil.copyfile('botFunctions.py', 'bot/botFunctions.py')
shutil.copyfile('botTrain.py', 'bot/botTrain.py')

setup(
  name='bot',
  version='0.0.1',
  description='boptimal_trader',
  long_description=readme,
  license=bb_license,
  long_description_content_type='text/markdown',
  url=('https://bitbucket.org/lukerr/trade_tronic/src/main/'),
  author='Luciano Ricotta',
  entry_points={
    'console_scripts': [
      'bot=bot.cli.bot:main',
      ],
    },
  classifiers=[
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'License :: 2023 Almania',
    'Natural Language :: English',
    'Programming Language :: Python :: 3.8',
  ],
  keywords='bot',
  packages=find_packages(),
  setup_requires=[],
  tests_require=[],
  package_data={
    'bot': [
      'README.md', 'LICENSE']},
  include_package_data=True
  )
