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

directory_number_data = api.model('directory_number_data', {
    'pattern': fields.String(description='Line Directory Number', default='', required=True),
    'routePartitionName': fields.String(description='Line Partition', default='', example='', required=False)
} )

add_line_data = api.model('add_line_data', {
    'line': fields.Nested(api.model('add_line_data1', {
            'index': fields.Integer(default=1),
            'dirn': fields.Nested(directory_number_data)
    }))
} )
add_phone_data = api.model('add_phone_data', {
    'name': fields.String(description='Phone Device Name', default='', example='CSFTEST1', required=True),
    'description': fields.String(description='Phone Device Description', default='', required=False),
    'product': fields.String(description='Phone Device Type', example='Cisco Unified Client Services Framework', required=True),
    'class': fields.String(description='Device Class', example='Phone', required=True),
    'protocol': fields.String(description='Device Protocol', example='SIP', required=True),
    'protocolSide': fields.String(description='Device Protocol Side', example='User', required=True),
    'commonPhoneConfigName': fields.String(description='Common Phone Config Name', example='Standard Common Phone Profile', required=True),
    'devicePoolName': fields.String(description='Device Pool Name', example='Default', required=True),
    'locationName': fields.String(description='Location Name', example='Hub_None', required=True),
    'securityProfileName': fields.String(description='Security Profile Name', example='Cisco Unified Client Services Framework - Standard SIP Non-Secure Profile', required=True),
    'sipProfileName': fields.String(description='SIP Profile Name', example='Standard SIP Profile', required=True),
    'lines': fields.Nested(add_line_data)
} )
@api.route("/add_phone")
class cucm_add_phone_api(Resource):
    @api.expect(add_phone_data)
    def post(self, **kwargs):
        """
        Adds a new Phone to CUCM

        * Send a JSON object

        ```
        {
        "name": "makmantest",
        "description": "Test Phone",
        "product": "Cisco Unified Client Services Framework",
        "class": "Phone",
        "protocol": "SIP",
        "protocolSide": "User",
        "commonPhoneConfigName": "Standard Common Phone Profile",
        "devicePoolName": "Default",
        "locationName": "Hub_None",
        "securityProfileName": "Cisco Unified Client Services Framework - Standard SIP Non-Secure Profile",
        "sipProfileName": "Standard SIP Profile"
        "lines": {
            "line": {
                "index": "1",
                "dirn": {
                    "pattern": "1111",
                    "routePartitionName": ""
                }
            }
        }
        }
        ```

        * Returns a dictionary with a 'success' (boolean) element.  If success is true, then the pkid of the new Phone is returned.

        """

        try:
            axlresult = myAXL.add_phone(phone_data=self.api.payload)
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "Phone Added Successfully", 'pkid': axlresult['return']}
        return jsonify(apiresult)
@api.route("/get_phone/<device_name>")
class cucm_get_phone_api(Resource):
    def get(self, device_name):
        """
        Finds a phone device from CUCM
        """
        try:
            axlresult = myAXL.get_phone(device_name)
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "Phone Data Retrieved Successfully", 'phone_data': axlresult['return']['phone']}
        return jsonify(apiresult)
@api.route("/delete_phone/<device_name>")
class cucm_delete_phone_api(Resource):
    def delete(self, device_name):
        """
        Deletes a phone device in CUCM
        """
        try:
            axlresult = myAXL.delete_phone(device_name)
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "Phone Successfully Deleted", 'pkid': axlresult['return']}
        return jsonify(apiresult)
@api.route("/list_phones")
class cucm_add_phone_api(Resource):
    def get(self, **kwargs):
        """
        Lists all phone devices to CUCM
        """
        phones = list_phones()
            
        return jsonify(phones)
@api.route("/edit_phone")
class cucm_edit_phone_api(Resource):
    def put(self):
        """
        Modifies a phone device to CUCM
        """
        pass