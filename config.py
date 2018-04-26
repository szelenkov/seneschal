#!/usr/bin/env python
# -*- coding: UTF-8 -*-
''' configuration '''

import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    ''' Config '''
    PUBLIC_KEY = 'None'
    APP_NAME = 'seneschal'
    COMPANY_NAME = 'your name or company name'
    UPDATE_URLS = ['']
    MAX_DOWNLOAD_RETRIES = 3

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASEDIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
