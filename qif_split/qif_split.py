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
from qifparse.qif import AmountSplit
from decimal import Decimal, getcontext, ROUND_HALF_UP


BUDGETED_CASH='Assets:Budgeted Cash'
UNBUDGETED_CASH='Budgets:Unbudgeted Cash'

ONE_HUNDRED = Decimal('100.0000')


def process_qif_file(config, qif_file):
  with open(qif_file) as q:
    qif = QifParser.parse(q)
    for a in qif.get_accounts():
      for t in a.get_transactions():
        for tt in t:
          splits = get_splits_for_transaction(config, tt)
          if splits:
            process_transaction_splits(splits, tt)
    print(str(qif))


def process_transaction_splits(split_configs, txn):
  for split_config in split_configs:
    amount = amount_for_transaction(txn, split_config)

    sign=sign_of(split_config.get('credit-sign'))
    add_split(amount*sign, split_config.get('credit-account'), txn)

    sign=sign_of(split_config.get('debit-sign'))
    add_split(amount*sign, split_config.get('debit-account'), txn)

    # replace the original category of the transaction with its own split
    add_split(txn.amount, txn.category, txn)
    txn.category = None
    txn.amount = 0
  debug('%s - %s: %s' % (txn.date, txn.category, txn.amount))


def amount_for_transaction(txn, cfg):
  if 'percentage' in cfg:
    return percentage_of(txn.amount, cfg['percentage'])
  else:
    return txn.amount


def add_split(amount, category, transaction):
  if category:
    split=AmountSplit(category=category, amount=amount)
    transaction.splits.append(split)


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


def percentage_of(amount, pctg):
  global ONE_HUNDRED
  getcontext().rounding = ROUND_HALF_UP
  c = getcontext()

  dividend = Decimal(pctg.replace('%', ''))
  percentage = c.divide(dividend, ONE_HUNDRED)
  product = c.multiply(amount, percentage)
  return product.quantize(Decimal('0.01'))


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
