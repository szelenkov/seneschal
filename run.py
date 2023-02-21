#!/usr/bin/env python -u
# -*- mode: python; coding: utf-8 -*-
#
# pylint: disable=no-name-in-module
"""
Entry point.

Created on Feb 16, 2021

@author: Serhiy
"""

import sys
from view.main import MainWindow

from PySide2.QtWidgets import QApplication

if __name__ == '__main__':

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()
