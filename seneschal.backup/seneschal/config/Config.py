#!python -u
# -*- coding: utf-8 -*-
"""
    Configuration
"""
import sqlite3
from os import name, getenv, makedirs
from os.path import join, abspath, dirname, exists
import Workspace

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
        if not exists(global_data_path):
            makedirs(global_data_path)

        default_config = {'default': {'workspace': join(global_data_path, 'workspace')}}

        config_file_path = join(global_data_path, 'config.ini')
        config = configparser.ConfigParser()
        config.read(config_file_path)
        modified = False

        for key, value in default_config.items():
            if key not in config:
                modified = True
                config[key] = {}

            for key1, value1 in value.items():
                if key1 not in config[key]:
                    config[key][key1] = value1
                    modified = True

        if modified:
            with open(config_file_path, 'w') as configfile:
                config.write(configfile)

        current_workspace = Workspace

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
