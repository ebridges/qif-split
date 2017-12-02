'''
Naval Fate.

Usage:
  naval_fate [--verbose]
  naval_fate -h | --help
  naval_fate --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --verbose     Debug-level output.
'''


from .version import __version__
from .util import configure_logging
from logging import info, debug
from docopt import docopt


def do_something():
  pass


def main():
  args = docopt(__doc__, version=__version__)
  configure_logging(args['--verbose'])
  do_something()
