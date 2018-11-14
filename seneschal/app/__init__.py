#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
'''
The script simply creates the application object and then imports
the views module, which we haven't written yet.
Do not confuse app the variable (which gets assigned the Flask instance)
with app the package (from which we import the views module).
'''

import sys
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

if getattr(sys, 'frozen', False):
    TEMPLATE_FOLDER = os.path.join(sys._MEIPASS, 'templates')
    app = Flask(__name__, template_folder=TEMPLATE_FOLDER)
else:
    app = Flask(__name__)

app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models
