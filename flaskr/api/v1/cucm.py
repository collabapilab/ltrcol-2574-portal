from flask import jsonify
from flask import request
from flask import Blueprint
from flask_restplus import Namespace, Resource, fields, reqparse
from flaskr.cucm.v1.cucm import AXL, PAWS

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
    'pattern': fields.String(description='Line Directory Number', example='', required=True),
    'routePartitionName': fields.String(description='Line Partition', default='', example='', required=True)
} )

add_line_data = api.model('add_line_data', {
    'line': fields.Nested(api.model('add_line_data1', {
            'index': fields.Integer(example=1),
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
    'lines': fields.Nested(add_line_data, required=False)
} )
@api.route("/add_phone")
class cucm_add_phone_api(Resource):
    @api.expect(add_phone_data, validate=True)
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
        Deletes a phone device from CUCM
        """
        try:
            axlresult = myAXL.delete_phone(device_name)
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "Phone Successfully Deleted", 'pkid': axlresult['return']}
        return jsonify(apiresult)

# List Phones querying arguments
list_phones_search_criteria_query_args = reqparse.RequestParser()
list_phones_search_criteria_query_args.add_argument('name', type=str, required=False,
                        help='Name to search', default='%')
list_phones_search_criteria_query_args.add_argument('description', type=str, required=False,
                        help='Description to search')
list_phones_search_criteria_query_args.add_argument('protocol', type=str, required=False, choices=[
                        'SIP', 'SCCP'], help='Device Protocol to search')
list_phones_search_criteria_query_args.add_argument('callingSearchSpaceName', type=str, required=False,
                        help='Device Calling Search Space Name to search')
list_phones_search_criteria_query_args.add_argument('devicePoolName', type=str, required=False,
                        help='Device Pool Name to search')
list_phones_search_criteria_query_args.add_argument('securityProfileName', type=str, required=False,
                        help='Device Security Profile Name to search')

list_phones_returned_tags_query_args = reqparse.RequestParser()
list_phones_returned_tags_query_args.add_argument('returnedTags', type=str, required=False,
                        help='Tags/Fields to Return (Supply a list seperated by comma) ie: name, description, product'
                        )

@api.route("/list_phones")
class cucm_list_phone_api(Resource):
    @api.expect(list_phones_search_criteria_query_args, list_phones_returned_tags_query_args, validate=True)
    def get(self):
        """
        Lists all phone details from CUCM given the search criteria
        """
        try:
            list_phones_search_criteria_query_parsed_args = list_phones_search_criteria_query_args.parse_args(request)
            list_phones_returned_tags_query_parsed_args = list_phones_returned_tags_query_args.parse_args(request)
            returned_tags = None
            if list_phones_returned_tags_query_parsed_args['returnedTags'] is not None:
                returned_tags_str = list_phones_returned_tags_query_parsed_args['returnedTags']
                returned_tags = list(map(str.strip,returned_tags_str.split(',')))
            axlresult = myAXL.list_phone(search_criteria_data=list_phones_search_criteria_query_parsed_args, 
                                         returned_tags=returned_tags)
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "Phone List Retrieved Successfully", 
                     'phone_list_count': len(axlresult['return']['phone']),
                     'phone_list_data': axlresult['return']['phone']}
        return jsonify(apiresult)
@api.route("/edit_phone")
class cucm_edit_phone_api(Resource):
    def put(self):
        """
        Modifies a phone device to CUCM
        """
        pass