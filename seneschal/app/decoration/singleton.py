#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
def singleton(cls):
    '''
    singleton decorator
    
    Returns:
        [type] -- [description]
    '''

    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance