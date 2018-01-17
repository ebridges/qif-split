import os
from setuptools import setup, find_packages

app_name='qif-split'
app_dir='qif_split'

with open('requirements.txt') as f:
  REQUIRED = [line.rstrip('\n') for line in f]

version_string = None
with open('%s/version.py' % app_dir) as f:
  for line in f:
    if(line.startswith('__version__')):
      version_string = line.strip().split('=')[1]

setup(
    name = app_name,
    version = version_string,
    packages=find_packages(),
    install_requires=REQUIRED,
    include_package_data=True,
    long_description=__doc__,
    entry_points={
       'console_scripts': [
           '%s = %s.%s:main' % (app_name, app_dir, app_dir),
       ]
    },
)
