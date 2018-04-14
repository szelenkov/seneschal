#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Setup
'''
from distutils.core import setup

__author__ = "Serhiy Zelenkov"
__copyright__ = "Copyright 2018"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = __author__
__email__ = "zelenkov@gmail.com"
__status__ = "Production"

setup(name='Distutils',
      version='1.0',
      description='Python Distribution Utilities',
      author=__author__,
      author_email=__email__,
      url='https://www.python.org/sigs/distutils-sig/',
      packages=['distutils', 'distutils.command'],
     )
     