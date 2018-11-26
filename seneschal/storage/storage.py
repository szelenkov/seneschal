#!python -u
# -*- coding: utf-8 -*-
#
# Storage module
from app.decoration import singleton

@singleton
class Storage():
    '''
    Storage class
    '''
    def __init__(self):
        '''
        '''
        pass

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
