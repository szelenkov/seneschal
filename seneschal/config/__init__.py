#!python -u
# -*- coding: utf-8 -*-
"""
    Configuration
"""
import sqlite3
from os import name, getenv, makedirs
from os.path import join, abspath, dirname, exists

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

    SQLALCHEMY_DATABASE_URI = getenv('DATABASE_URL', 'sqlite:///' + join(BASEDIR, 'app.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    def __init__(self):
        pass

    @property
    def workspaces(self):
        '''workspaces generator'''
        import configparser

        global_data_path = join({'nt' : getenv('ProgramData', 'C:\\ProgramData'),
                                 'posix' : '/usr/share'}.get(name), 'seneschal')
        if not exists(directory):
            makedirs(directory)

        config = configparser.ConfigParser()
        config.read('config.ini')
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
