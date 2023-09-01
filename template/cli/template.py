"""
Command line interface (CLI) for Template Interface
"""
import click
import colorama
import logging
from pprint import pprint

from template import __version__
from template import Template

@click.command()
@click.version_option(__version__)
@click.argument('string')
@click.argument('int', type=int)
@click.option('--true/--false', default=True)
def main(string, int, true):
  """
  Template script

  This command line interface provides capability as a template.
  """
  logging.basicConfig(level=logging.INFO, format='%(message)s')

  template = Template(string, int)

  pprint(template)

if __name__ == "__main__":
  main() # pylint: disable=no-value-for-parameter
