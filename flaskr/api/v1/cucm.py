from flask import jsonify
from flask import request
from flask import Blueprint
from flask_restplus import Namespace, Resource, fields
from flaskr.cucm.v1.cucm import AXL, PAWS
import xmltodict

api = Namespace('cucm', description='Cisco Unified Communications Manager APIs')

default_cucm = {
#    'host': 'cucm1a.pod31.col.lab',
   'host': '10.0.131.41',
   'port': 8443,
   'username': 'admin',
   'password': 'c1sco123'
}

system_status_data = api.model('CUCM System', {
    'host': fields.String(description='CUCM host/IP', default=default_cucm['host'], required=False),
    'port': fields.Integer(description='port', default=default_cucm['port'], required=False),
    'username': fields.String(description='CUCM API user name', default=default_cucm['username'], required=False),
    'password': fields.String(description='CUCM API user password', default='********', required=False),
})

myAXL = AXL(default_cucm['host'], default_cucm['username'], default_cucm['password'])
myPAWSVersionService = PAWS(default_cucm['host'], default_cucm['username'], default_cucm['password'], 'VersionService')

@api.route("/get_version")
class cucm_get_version_api(Resource):
    def get(self):
        """
        Returns CUCM Active Software version
        """
        try:
            version_info = myPAWSVersionService.get_version()
        except Exception as e:
            result = {'success': False, 'message': str(e)}
            return jsonify(result)
        if version_info['version']:
            try:
                result = {'success': True, 'version': version_info['version']}
            except KeyError:
                pass
        return jsonify(result)
@api.route("/get_phone/<device_name>")
class cucm_get_phone_api(Resource):
    def get(self, device_name):
        """
        Finds a phone device in CUCM
        """
        try:
            phone = myAXL.get_phone(device_name)
        except Exception as e:
            result = {'success': False, 'message': str(e)}
            return jsonify(result)
        return jsonify(phone)

@api.route("/list_phones")
class cucm_add_phone_api(Resource):
    def get(self, **kwargs):
        """
        Lists all phone devices to CUCM
        """
        phones = list_phones()
            
        return jsonify(phones)
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


