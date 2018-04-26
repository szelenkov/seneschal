#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 
'''
The script simply creates the application object (of class Flask) and then imports
the views module, which we haven't written yet.
Do not confuse app the variable (which gets assigned the Flask instance)
with app the package (from which we import the views module).
'''

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models
