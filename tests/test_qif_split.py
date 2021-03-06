"""
Unit tests for QIF Split
"""

from datetime import datetime
from decimal import Decimal
from unittest import TestCase, main
from qif_split import qif_split

EG_CONFIG_FILE = 'eg/example-split-config.json'


class MockTxn():
  def __init__(self, category='mock-category', amount=Decimal('0'), splits=[], date=datetime.today()):
    self.category=category
    self.amount=amount
    self.splits=splits
    self.date = date


class TestQifSplit(TestCase):
  def test_get_splits_for_transaction(self):
    CATEGORY_NAME = 'foobar'
    EXPECTED_RESULT = 'barfoo'
    config = dict()
    config['category:%s' % CATEGORY_NAME] = EXPECTED_RESULT
    txn = MockTxn(CATEGORY_NAME)
    ACTUAL_RESULT = qif_split.get_splits_for_transaction(config, txn)
    self.assertEqual(EXPECTED_RESULT, ACTUAL_RESULT)


  def test_add_split(self):
    category='foobar'
    amount=Decimal(123.45)
    txn = MockTxn(category, amount)
    qif_split.add_split(amount, category, txn)
    self.assertEqual(len(txn.splits), 1)
    self.assertEqual(txn.splits[0].category, category)
    self.assertEqual(txn.splits[0].amount, amount)


  def test_amount_for_transaction(self):
    txn_amt = Decimal("1.00")
    
    cfg_pct = {'percentage': '25%'}
    amount = qif_split.amount_for_transaction(txn_amt, cfg_pct)
    self.assertEqual(amount, Decimal("0.25"))

    cfg_nil = {}
    amount = qif_split.amount_for_transaction(txn_amt, cfg_nil)
    self.assertEqual(amount, Decimal("1.00"))


  def test_load_split_config(self):
    global EG_CONFIG_FILE
    config = qif_split.load_split_config(EG_CONFIG_FILE)
    self.assertTrue('category:Expenses:Food & Dining:Groceries' in config)
    splits = config['category:Expenses:Food & Dining:Groceries']
    self.assertEqual(splits[0]['credit-account'], 'Assets:Budgeted Cash')


  def test_percentage_of(self):
    actual_value = qif_split.percentage_of(300, '33.3333%')
    self.assertEqual(Decimal(100), actual_value)
    actual_value = qif_split.percentage_of(100, '20%')
    self.assertEqual(Decimal(20), actual_value)
    actual_value = qif_split.percentage_of(40, '6.67%')
    self.assertEqual(Decimal("2.67"), actual_value)


  def test_sign_of(self):
    self.assertEqual(qif_split.sign_of(None), 1)
    self.assertEqual(qif_split.sign_of(-10), -1)
    self.assertEqual(qif_split.sign_of(+10), +1)


  def test_transaction_filter(self):
    """
    test of the `transaction_filter` function.
    """
    new_years = datetime(2017, 1, 1)
    txn_filter = {'asof': new_years.date()}
    empty_txn_filter = {}

    after_new_years = datetime(2017, 6, 6)
    txn = MockTxn(date=after_new_years)
    self.assertTrue(qif_split.transaction_filter(txn, txn_filter))

    on_new_years = datetime(2017, 1, 1)
    txn = MockTxn(date=on_new_years)
    self.assertTrue(qif_split.transaction_filter(txn, txn_filter))

    before_new_years = datetime(2016, 12, 31)
    txn = MockTxn(date=before_new_years)
    self.assertFalse(qif_split.transaction_filter(txn, txn_filter))

    today = datetime.today()
    txn = MockTxn(date=today)
    self.assertTrue(qif_split.transaction_filter(txn, empty_txn_filter))


if __name__ == '__main__':
    main()
