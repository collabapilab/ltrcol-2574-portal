from flask import Flask, Blueprint
from flask_restx import Api, Resource

from flaskr.api.v1.cucm import api as cucm
from flaskr.api.v1.cuc import api as cuc
from flaskr.api.v1.cms import api as cms
from flaskr.api.v1.wbxt import api as wbxt
from flaskr.api.v1.wbxc import api as wbxc
from flaskr.api.v1.core import api as core


v1_blueprint = Blueprint('api_v1', __name__,
                         template_folder='templates',
                         static_folder='static')

v1api = Api(v1_blueprint, title="LTRCOL-2574 Portal APIs", version='1.0')

v1api.add_namespace(cucm)
v1api.add_namespace(cuc)
v1api.add_namespace(cms)
v1api.add_namespace(wbxt)
v1api.add_namespace(wbxc)
v1api.add_namespace(core)
