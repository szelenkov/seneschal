#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0621
''' Partition tests '''
import pytest

@pytest.fixture(scope='class')
def smtp_connection():
    '''fixture'''
    import smtplib
    return smtplib.SMTP("smtp.gmail.com", 587, timeout=5)

def test_ehlo(smtp_connection):
    ''' test '''
    response, _ = smtp_connection.ehlo()
    assert response == 250
    assert 0 # for demo purposes
