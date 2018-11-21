#!python -u
# -*- coding: utf-8 -*-
"""
    Configuration
"""

import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    ''' Config
    >>> Config().workspaces.name
    default
    '''
    PUBLIC_KEY = 'None'
    APP_NAME = 'seneschal'
    COMPANY_NAME = 'your name or company name'
    UPDATE_URLS = ['']
    MAX_DOWNLOAD_RETRIES = 3

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASEDIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    def __init__(self):
        pass

    @property
    def workspaces(self):
        '''workspaces generator'''
        global_data_pass =  {'Windows': os.environ.get('ProgramData') or 'C:\\ProgramData',
                             'Linux':'/usr/share'}.get(os.system, default=None)
        

if __name__ == "__main__":
    import doctest

    doctest.testmod()
