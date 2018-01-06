# QIF Split

[![Travis CI Status](https://travis-ci.org/ebridges/qif-split.png?branch=master)](https://travis-ci.org/ebridges/qif-split)

Splits transactions in a QIF file to support budgeting and more granular financial tracking.

## Installation

```
$ mkvirtualenv --python=python3 qif-split # optional
$ pip install --requirement requirements.txt
$ python setup.py test install
```

## Usage

```
$ qif-split --help
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
```

## Example

### Overview

In order to illustrate how you might use `qif-split` to automate maintaining a budget in GnuCash, take this 
 budgeting scenario described in the blog post 
["Better budgeting with GnuCash"](http://allmybrain.com/2008/12/15/better-budgeting-with-gnucash/). This scenario involves splitting transactions to allocate them properly to budget contra-accounts.

By using the `qif-split` tool when importing transactions from QIF files downloaded from your bank,
you can eliminate the tedious & error-prone work of manually splitting transactions to keep your budget updated.

### Illustration

The file `allmybrain-input.qif` provides a QIF file consisting of the two transactions
described in that blog post:

```
!Account
NAssets:Current Assets:Checking Account
TBank
^
!Type:Bank
C
D12/15/2008
NN/A
PSample Income
T100.00
LIncome
^
C
D12/16/2008
NN/A
PGrocery Shopping
T-37.50
LExpenses:Food
^
```

By running  `qif-split` on that input, we get a new QIF file with the transactions
split so that the amounts get properly allocated to the configured budget account:

```
$ qif-split split \
    --qif-input=eg/allmybrain-input.qif \
    --split-cfg=eg/allmybrain-split-config.json
!Account
NAssets:Current Assets:Checking Account
TBank
^
!Type:Bank
D12/15/2008
NN/A
T100.00
PSample Income
LIncome
SBudget:Food
$50.00
SAssets:Budgeted Cash
$-50.00
SIncome
$100.00
^
D12/16/2008
NN/A
T-37.50
PGrocery Shopping
LExpenses:Food
SAssets:Budgeted Cash
$37.50
SBudget:Food
$-37.50
SExpenses:Food
$-37.50
^
```

Importing the resulting split QIF file into the provided GnuCash file (`eg/allmybrain.gnucash`)
gives the desired result of the transactions split properly across budget accounts:

![Journal view of imported QIF file with splits.](./eg/allmybrain-journal.png)

