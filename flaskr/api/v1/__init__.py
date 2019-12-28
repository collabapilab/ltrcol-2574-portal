from flask import Flask, Blueprint
from flask_restplus import Api, Resource

from flaskr.api.v1.cucm import api as cucm
from flaskr.api.v1.cuc import api as cuc
from flaskr.api.v1.cms import api as cms
from flaskr.api.v1.wbxt import api as wbxt

v1_blueprint = Blueprint('api_v1', __name__,
                         template_folder='templates',
                         static_folder='static')

v1api = Api(v1_blueprint)

v1api.add_namespace(cucm)
v1api.add_namespace(cuc)
v1api.add_namespace(cms)
v1api.add_namespace(wbxt)
