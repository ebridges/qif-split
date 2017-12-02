'''
QIF Split

Usage:
  qif-split split --qif-input=<PATH> [--split-cfg=<PATH>] [--verbose]
  qif-split -h | --help
  qif-split --version

Options:
  --qif-input=<PATH>   Input QIF file.
  --split-cfg=<PATH>   Input configuration of splits [Default: ./split-config.json]
  -h --help            Show this screen.
  --version            Show version.
  --verbose            Debug-level output.
'''


from .version import __version__
from .util import configure_logging
from logging import info, debug, error
from docopt import docopt
import json
from jsoncomment import JsonComment

def process_splits(config, qif_file):


def load_split_config(config):
  parser = JsonComment(json)
  with open(config) as fp:
    return parser.load(fp)

def main():
  args = docopt(__doc__, version=__version__)
  configure_logging(args['--verbose'])

  split_config = load_split_config(args['--split-cfg'])

  qif_file = args['--qif-input']

  if qif_file:
    process_splits(split_config, qif_file)
  else:
    error('qif-input not specified.')
