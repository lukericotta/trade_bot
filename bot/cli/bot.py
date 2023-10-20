"""
Command line interface (CLI) for BoptimalTrader Interface
"""
import click
import logging

from bot import __version__
from bot import BoptimalTrader

@click.command()
@click.version_option(__version__)
@click.argument('api_config')
@click.argument('training_config')
@click.option('--crypto/--stocks', default=False)
@click.option('--continuous/--single', default=False)
def main(api_config, training_config, crypto, continuous):
  """
  BoptimalTrader script

  This command line interface provides capability as a  bot for stock and crypto trading.
  """
  logging.basicConfig(level=logging.INFO, format='%(message)s')

  bot = BoptimalTrader(api_config, training_config, crypto, continuous)
  bot.setup()
  bot.start()

if __name__ == "__main__":
  main() # pylint: disable=no-value-for-parameter
