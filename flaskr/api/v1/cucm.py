from flask import jsonify
from flask import request
from flask import Blueprint
import flask
from flask_restplus import Namespace, Resource, fields
from flaskr.cucm.v1.cucm import *
import xmltodict

api = Namespace('cucm', description='Cisco Unified Communications Manager APIs')

system_status_data = api.model('CUCM System', {
    'host': fields.String(description='CUCM host/IP', default=default_cucm['host'], required=False),
    'port': fields.Integer(description='port', default=default_cucm['port'], required=False),
    'username': fields.String(description='CUCM API user name', default=default_cucm['username'], required=False),
    'password': fields.String(description='CUCM API user password', default='********', required=False),
})

@api.route("/get_version")
class cucm_get_version_api(Resource):
    def get(self, host=default_cucm['host'], port=default_cucm['port'], username=default_cucm['username'], password=default_cucm['password']):
        """
        Returns CUCM Active Software version
        """
        result = cucm_get_version(host=host, username=username, password=password, port=port)
        if result['success']:
            try:
                result = {'success': True, 'version': result['response']['version']}
            except KeyError:
                pass
        return jsonify(result)

@api.route("/list_phones")
class cucm_add_phone_api(Resource):
    def get(self, **kwargs):
        """
        Lists all phone devices to CUCM
        """
        phones = list_phones()
            
        return jsonify(phones)

@api.route("/find_phone")
class cucm_add_phone_api(Resource):
    def get(self, **kwargs):
        """
        Finds a phone device in CUCM
        """
        phone = find_phone_api()
            
        return jsonify(phone)

    
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


