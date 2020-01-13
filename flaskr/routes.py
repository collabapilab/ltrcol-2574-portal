# import os
# import pathlib

from flask import render_template
from flask import Blueprint
from flask import request

core = Blueprint('', __name__,
                 template_folder='templates',
                 static_folder='static')


@core.route('/')
def index():
    return render_template('index.html',
                           title='LTRCOL-2574 Portal')


@core.route('/provisioning')
def provisioning_route():
    return render_template('provisioning.html',
                           title='LTRCOL-2574 Portal - Provisioning')


@core.route('/', defaults={'path': ''})
@core.route('/<path:path>')
def catch_all(path):
    return render_template(path,
                           title='LTRCOL-2574 Sample Portal')
