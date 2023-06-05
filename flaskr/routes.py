from flask import render_template
from flask import Blueprint
from flask import request

core = Blueprint('ltrcol-2574-portal', __name__,
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
