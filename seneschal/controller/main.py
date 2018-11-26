#!python -u
# -*- coding: utf-8 -*-
#
from flask import (
    Blueprint, render_template
)

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    '''main/index.html'''
    return render_template('main/index.html', title='Flask-PWA')
