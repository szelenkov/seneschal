#!python -u
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

def create_app():
    '''app'''

    from flask import Flask
    # from flask_sqlalchemy import SQLAlchemy
    # from flask_migrate import Migrate
    from flask_debugtoolbar import DebugToolbarExtension

    app = Flask(
        __name__,
        instance_relative_config=True,
        static_url_path=''
    )

    app.debug = True
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY') or 'you-will-never-guess',
        # SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or
        #  'sqlite:///' + os.path.join(app.instance_path, 'app.db'),
        # SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # try:
    #     os.makedirs(app.instance_path)
    # except OSError:
    #     pass

    from flask_sslify import SSLify
    if 'DYNO' in os.environ:  # only trigger SSLify if the app is running on Heroku
        sslify = SSLify(app)

    # from app.model import db, migrate
    # db.init_app(app)
    # migrate.init_app(app, db)

    from app.controller import main, pwa

    app.register_blueprint(main.bp)
    app.register_blueprint(pwa.bp)

    # db = SQLAlchemy(app)
    # migrate = Migrate(app, db)
    # https://flask-debugtoolbar.readthedocs.io/en/latest/
    toolbar = DebugToolbarExtension(app)

    return app
