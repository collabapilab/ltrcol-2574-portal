from flask import Flask, Blueprint
from flask_restplus import Api, Resource

from flaskr.api.v1.upload import api as upload 
from flaskr.api.v1.call_flows import api as call_flows 
from flaskr.api.v1.process import api as process 
from flaskr.api.v1.results import api as results 
from flaskr.api.v1.locations import api as locations 
from flaskr.api.v1.speech_to_text import api as stt 
from flaskr.api.v1.cms import api as cms 

v1_blueprint = Blueprint('api_v1', __name__,                 
                template_folder='templates',
                static_folder='static')
v1api = Api(v1_blueprint)


v1api.add_namespace(upload)
v1api.add_namespace(call_flows)
v1api.add_namespace(process)
v1api.add_namespace(results)
v1api.add_namespace(locations)
v1api.add_namespace(cms)
