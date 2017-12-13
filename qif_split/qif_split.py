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
from qifparse.parser import QifParser

BUDGETED_CASH='Assets:Budgeted Cash'
UNBUDGETED_CASH='Budget:Unbudgeted Cash'

def process_qif_file(config, qif_file):
  with open(qif_file) as q:
    qif = QifParser.parse(q)
    for a in qif.get_accounts():
      for t in a.get_transactions():
        for tt in t:
          splits = get_splits_for_transaction(config, tt)
          process_transaction_splits(splits)
    #print(str(qif))


def process_transaction_splits(splits):
  if splits:
    print("\nThis transaction has a split:")
  else:
    print("\nThis transaction does not have a split:")
  print('%s - %s: %s' % (txn.date, txn.category, txn.amount))


def get_splits_for_transaction(cfg, txn):
  key = 'category:%s' % txn.category
  return cfg.get(key)


def load_split_config(config):
  parser = JsonComment(json)
  with open(config) as fp:
    cfg = parser.load(fp)
    split_config = dict()
    for entry in cfg:
      key = '%s:%s' % (entry['match-on-field'], entry['match-on-text'])
      split_config[key] = round_out_splits(entry['splits'])
    return split_config


## Appends a split to add any remainder < 100% to an
## account for unbudgeted cash.  intended for budget
## setup to ensure all income is assigned to a budget account
def round_out_splits(splits):
  global BUDGETED_CASH
  global UNBUDGETED_CASH
  pctg = 0
  for split in splits:
    if 'percentage' in split:
      pctg = pctg + int(split['percentage'].replace('%', ''))
  remainder=100-pctg
  if(remainder > 0 and remainder < 100):
    splits.append({
      "credit-account": UNBUDGETED_CASH,
      "debit-account": BUDGETED_CASH,
      "percentage": "%d%%" % remainder
    })
  return splits


def sign_of(value):
  return -1 if value and value < 0 else 1

def main():
  args = docopt(__doc__, version=__version__)
  configure_logging(args['--verbose'])

  split_config = load_split_config(args['--split-cfg'])

  qif_file = args['--qif-input']

  if qif_file:
    process_qif_file(split_config, qif_file)
  else:
    error('qif-input not specified.')
