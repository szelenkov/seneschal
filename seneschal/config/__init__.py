#!python -u
# -*- coding: utf-8 -*-
"""
    Configuration
"""
import os
import sqlite3
from os import environ, system as system_name
from os.path import join, abspath, dirname

BASEDIR = abspath(dirname(__file__))

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

    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL') or \
        'sqlite:///' + join(BASEDIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    def __init__(self):
        pass

    @property
    def workspaces(self):
        '''workspaces generator'''
        global_data_path = join({'Windows' : environ.get('ProgramData') or 'C:\\ProgramData',
                                 'Linux' : '/usr/share'}.get(system_name, default=None), 'seneschal')

        conn = sqlite3.connect(join(global_data_path, 'example.db'))
        conn.isolation_level = None
        try:
            cur = conn.Cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            print(cur.fetchall())
        except sqlite3.Error:
            pass
        finally:
            pass
        conn.close()

if __name__ == "__main__":
    import doctest

    doctest.testmod()
