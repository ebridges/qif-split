
from unittest import TestCase, main
from qif_split import qif_split
from decimal import Decimal

class MockTxn():
  def __init__(self, category='mock-category', amount=Decimal('0'), splits=[]):
    self.category=category
    self.amount=amount
    self.splits=splits


class TestQifSplit(TestCase):
  def test_get_splits_for_transaction(self):
    CATEGORY_NAME='foobar'
    EXPECTED_RESULT='barfoo'
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
    txn = MockTxn(amount=Decimal("1.00"))
    
    cfg_pct = {'percentage': '25%'}
    amount = qif_split.amount_for_transaction(txn, cfg_pct)
    self.assertEqual(amount, Decimal("0.25"))

    cfg_nil = {}
    amount = qif_split.amount_for_transaction(txn, cfg_nil)
    self.assertEqual(amount, Decimal("1.00"))



  def test_load_split_config(self):
    EG_CONFIG_FILE='eg/split-config.json'
    config = qif_split.load_split_config(EG_CONFIG_FILE)
    self.assertTrue('category:Expenses:Food & Dining:Groceries' in config)
    splits = config['category:Expenses:Food & Dining:Groceries']
    self.assertEqual(splits[0]['credit-account'], 'Assets:Budgeted Cash')


  def test_round_out_splits(self):
    EG_SPLITS = [
      {
        "credit-account": "Assets:Budgeted Cash",
        "debit-account": "Budget:Expenses:Food & Dining:Groceries",
        "percentage": "75%"
      }
    ]
    actual_splits = qif_split.round_out_splits(EG_SPLITS)

    self.assertEqual(len(actual_splits), 2)
    self.assertEqual(actual_splits[1]['percentage'], "25%")


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


if __name__ == '__main__':
    main()
