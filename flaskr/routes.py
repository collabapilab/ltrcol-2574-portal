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
    return render_template('main.html',
                           title='LTRCOL-2574 Collaboration APIs')


@core.route('/cucm')
def cucm_route():
    return render_template('cucm.html',
                           title='LTRCOL-2574 Sample Portal')


@core.route('/cuc')
def cuc_route():
    return render_template('cuc.html',
                           title='LTRCOL-2574 Sample Portal')


@core.route('/cms')
def cms_route():
    return render_template('cms.html',
                           title='LTRCOL-2574 Sample Portal')


@core.route('/wbxt')
def wbxt_route():
    return render_template('wbxt.html',
                           title='LTRCOL-2574 Sample Portal')
