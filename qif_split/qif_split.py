'''
QIF Split

Usage:
  qif-split split --qif-input=<PATH> [--split-cfg=<PATH>] [--asof=<DATE>] [--verbose]
  qif-split -h | --help
  qif-split --version

Options:
  --qif-input=<PATH>   Input QIF file.
  --split-cfg=<PATH>   Input configuration of splits [Default: ./split-config.json]
  --asof=<DATE>        Only process splits for transactions on or after this date (e.g.: %Y-%m-%d).
  -h --help            Show this screen.
  --version            Show version.
  --verbose            Debug-level output.
'''


import json
from decimal import Decimal, getcontext, ROUND_HALF_UP
from logging import info, debug, error
from datetime import datetime
from docopt import docopt
from jsoncomment import JsonComment
from qifparse.parser import QifParser
from qifparse.qif import AmountSplit

from .util import configure_logging
from .version import __version__


def process_qif_file(config, qif_file, txn_filter):
  """
  Given a QIF file and configuration for splitting transactions,
  loop through all of the transactions and split them up based
  on the given configuration.

  Args:
    config (dictionary): Split configuration.
    qif_file (string): Path to a QIF file.
    txn_filter (dictionary): A collection of rules for filtering transactions.
  """
  with open(qif_file) as q:
    qif = QifParser.parse(q)
    for account in qif.get_accounts():
      for transactions in account.get_transactions():
        for transaction in transactions:
          if transaction_filter(transaction, txn_filter):
            splits = get_splits_for_transaction(config, transaction)
            if splits:
              process_transaction_splits(splits, transaction)
    print(str(qif))


def transaction_filter(transaction, txn_filter):
  """
  Using the given dictionary of transaction-filtering rules,
  decide whether any of them apply to the given transaction.
  """
  if 'asof' in txn_filter and transaction.date.date() < txn_filter['asof']:
    return False
  return True


def process_transaction_splits(split_configs, txn):
  """
  Given a transaction and a configuration for how to split it,
  add splits to the transaction per the configuration.
  """
  info('processing splits for transaction [%s]...' % txn.category)
  account_tally = dict()
  for split_config in split_configs:
    amount = amount_for_transaction(txn.amount, split_config)

    sign = sign_of(split_config.get('credit-sign'))
    incr_account_by(account_tally, split_config.get('credit-account'), amount*sign)

    sign = sign_of(split_config.get('debit-sign'))
    incr_account_by(account_tally, split_config.get('debit-account'), amount*sign)

  # add a split for original category of the transaction
  incr_account_by(account_tally, txn.category, txn.amount)

  for account, amount in account_tally.items():
    add_split(amount, account, txn)

  debug('%s - %s: %s' % (txn.date, txn.category, txn.amount))
  info('...completed.')


def incr_account_by(tally, account, amount):
  """
  Updates a given account by an amount and stored in the given tally.
  """
  if account not in tally:
    tally[account] = Decimal(0)
  tally[account] = tally[account] + amount


def amount_for_transaction(amount, cfg):
  """
  Returns a percentage of the amount, if configured for that, else
  returns the given amount unmodified.
  """
  if 'percentage' in cfg:
    return percentage_of(amount, cfg['percentage'])
  else:
    return amount


def add_split(amount, category, transaction):
  """
  Initializes a split for the given transaction.
  """
  if category:
    split = AmountSplit(category=category, amount=amount)
    transaction.splits.append(split)


def get_splits_for_transaction(cfg, txn):
  """
  Encapsulates the structure of the key used for mapping splits for a given category.
  """
  key = 'category:%s' % txn.category
  return cfg.get(key)


def load_split_config(config):
  """
  Loads a file containing a split configuration and structures it as a dictionary.
  """
  parser = JsonComment(json)
  with open(config) as config_file:
    cfg = parser.load(config_file)
    split_config = dict()
    for entry in cfg:
      key = '%s:%s' % (entry['match-on-field'], entry['match-on-text'])
      split_config[key] = entry['splits']
    return split_config


def percentage_of(amount, pctg):
  """
  Calculates the percentage of the given amount.
  """
  one_hundred = Decimal('100.0000')
  getcontext().rounding = ROUND_HALF_UP
  decimal_context = getcontext()

  dividend = Decimal(pctg.replace('%', ''))
  percentage = decimal_context.divide(dividend, one_hundred)
  product = decimal_context.multiply(amount, percentage)
  return product.quantize(Decimal('0.01'))


def sign_of(value):
  """
  Normalizes the sign of a given value to ±1
  """
  return -1 if value and value < 0 else 1


def main():
  """
  Entry point of application.
  """
  args = docopt(__doc__, version=__version__)
  configure_logging(args['--verbose'])

  split_cfg = args['--split-cfg']
  split_config = load_split_config(split_cfg)
  info('loaded split config from [%s]' % split_cfg)

  qif_file = args['--qif-input']
  info('processing QIF file: [%s]' % qif_file)

  asof = args['--asof']
  if asof:
    asof_date = datetime.strptime(asof, '%Y-%m-%d').date()
    info('filtering transactions as of %s' % asof_date)
    txn_filter = {'asof': asof_date}
  else:
    txn_filter = {}

  if qif_file:
    process_qif_file(split_config, qif_file, txn_filter)
  else:
    error('qif-input not specified.')


if __name__ == '__main__':
    main()
