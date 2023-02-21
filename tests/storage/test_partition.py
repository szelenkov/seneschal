#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
# py lint: disable=W0621
"""Partition tests."""
from os import path
import os
import pytest
from archivist import Archivist


@pytest.fixture(scope='class')
def storage_connection():
    """Fixture."""
    filepath = "temp.dat"
    if path.exists(filepath):
        os.remove(filepath)

    storage = Archivist(filepath)
    assert storage is not None

    return storage


def test_storage(storage: Archivist):
    """Test."""
    assert storage is not None
    files = storage.files
    assert files is not None
