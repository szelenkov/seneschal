#!python -u
# -*- coding: utf-8 -*-
'''
entry point
'''
from seneschal import config

def main():
    ''' main '''
    for workspace in config.Config().workspaces:
        if workspace.is_default:
            pass

if __name__ == "__main__":
    main()
