from flask import jsonify
from flask import request
from flask import Blueprint
from flask_restplus import Namespace, Resource, fields, reqparse
from flaskr.cucm.v1.cucm import AXL, PAWS
from flaskr.api.v1.parsers import cucm_add_phone_query_args, cucm_list_phones_returned_tags_query_args, cucm_list_phones_search_criteria_query_args

api = Namespace('cucm', description='Cisco Unified Communications Manager APIs')

default_cucm = {
#    'host': 'cucm1a.pod31.col.lab',
   'host': '10.0.131.41',
   'port': 8443,
   'username': 'admin',
   'password': 'c1sco123'
}

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
@api.route("/add_phone")
class cucm_add_phone_api(Resource):
    @api.expect(cucm_add_phone_query_args, validate=True)
    def post(self):
        """
        Adds a new Phone to CUCM
        """
        try:
            cucm_add_phone_query_parsed_args = cucm_add_phone_query_args.parse_args(request)
            cucm_add_phone_data_dict = {
                "name": cucm_add_phone_query_parsed_args['name'],
                "description": cucm_add_phone_query_parsed_args['description'],
                "product": "Cisco Unified Client Services Framework",
                "class": "Phone",
                "protocol": "SIP",
                "protocolSide": "User",
                "commonPhoneConfigName": "Standard Common Phone Profile",
                "devicePoolName": "Default",
                "locationName": "Hub_None",
                "securityProfileName": "Cisco Unified Client Services Framework - Standard SIP Non-Secure Profile",
                "sipProfileName": "Standard SIP Profile",
                "ownerUserName": cucm_add_phone_query_parsed_args['ownerUserName'],
                "lines": {
                    "line": {
                        "index": "1",
                        "dirn": {
                            "pattern": cucm_add_phone_query_parsed_args['directorynumber']
                        },
                        "display": cucm_add_phone_query_parsed_args['calleridname'],
                        "displayAscii": cucm_add_phone_query_parsed_args['calleridname'],
                        "associatedEndusers": {
                                "enduser": {
                                    "userId": cucm_add_phone_query_parsed_args['ownerUserName']
                                }
                        }
                    }
                }
            }
            axlresult = myAXL.add_phone(phone_data=cucm_add_phone_data_dict)
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
@api.route("/list_phones")
class cucm_list_phone_api(Resource):
    @api.expect(cucm_list_phones_search_criteria_query_args, cucm_list_phones_returned_tags_query_args, validate=True)
    def get(self):
        """
        Lists all phone details from CUCM given the search criteria
        """
        try:
            list_phones_search_criteria_query_parsed_args = cucm_list_phones_search_criteria_query_args.parse_args(request)
            list_phones_returned_tags_query_parsed_args = cucm_list_phones_returned_tags_query_args.parse_args(request)
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
@api.route("/edit_phone/<device_name>")
class cucm_edit_phone_api(Resource):
    def put(self):
        """
        Updates a Phone Configuration
        """
        