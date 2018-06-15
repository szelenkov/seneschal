#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
'''
The script simply creates the application object (of class Flask) and then imports
the views module, which we haven't written yet.
Do not confuse app the variable (which gets assigned the Flask instance)
with app the package (from which we import the views module).
'''

import sys
import os

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    app = Flask(__name__, template_folder=template_folder)
else:
    app = Flask(__name__)

app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models
