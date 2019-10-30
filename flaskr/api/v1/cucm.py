
from flask import jsonify, request
from flask import Blueprint
from flask_restplus import Namespace, Resource
from flaskr.cucm.v1 import *

api = Namespace('cucm', description='Cisco Unified Communications Manager APIs')

@api.route("/get_version")
class cucm_get_version_api(Resource):
    def get(self):
        """
        Returns CUCM Software version
        """
        version = get_cucm_version()

        return jsonify(version)

@api.route("/add_phone")
class cucm_add_phone_api(Resource):
    def post(self, **kwargs):
        """
        Adds a phone device to CUCM
        """
        status = post_add_phone()
            
        return jsonify(status)

@api.route("/edit_phone")
class cucm_edit_phone_api(Resource):
    def put(self):
        """
        Modifies a phone device to CUCM
        """
        pass

@api.route("/delete_phone")
class cucm_delete_phone_api(Resource):
    def delete(self):
        """
        Deletes a phone device from CUCM
        """
        pass 


