from flask import jsonify
from flask import request
from flask import Blueprint
from flask_restplus import Namespace, Resource, fields, reqparse
from flaskr.cucm.v1.cucm import AXL, PAWS, SXML
from flaskr.api.v1.parsers import cucm_add_phone_query_args
from flaskr.api.v1.parsers import cucm_update_phone_query_args
from flaskr.api.v1.parsers import cucm_list_phones_returned_tags_query_args
from flaskr.api.v1.parsers import cucm_list_phones_search_criteria_query_args
from flaskr.api.v1.parsers import cucm_device_search_criteria_query_args
from flaskr.api.v1.parsers import cucm_service_status_query_args

api = Namespace('cucm', description='Cisco Unified Communications Manager APIs')


# default_cucm = {
#    'host': 'cucm1a.pod31.col.lab',
#    'port': 8443,
#    'username': 'admin',
#    'password': 'c1sco123'
# }

default_cucm = {
   'host': '10.0.131.41',
   'port': 8443,
   'username': 'admin',
   'password': 'c1sco123'
}

myAXL = AXL(default_cucm['host'], default_cucm['username'], default_cucm['password'])
myPAWSVersionService = PAWS(default_cucm['host'], default_cucm['username'], default_cucm['password'], 'VersionService')
mySXMLRisPort70Service = SXML(default_cucm['host'], default_cucm['username'], default_cucm['password'], 'realtimeservice2')
mySXMLControlCenterServicesService = SXML(default_cucm['host'], default_cucm['username'], default_cucm['password'], 'controlcenterservice2')


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
        apiresult = {'success': True, 'message': "Phone Added Successfully", 'uuid': axlresult['return']}
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
        apiresult = {'success': True, 'message': "Phone Successfully Deleted", 'uuid': axlresult['return']}
        return jsonify(apiresult)


@api.route("/apply_phone/<device_name>")
class cucm_apply_phone_api(Resource):
    def put(self, device_name):
        """
        Applies a Phone Configuration on CUCM
        """
        try:
            axlresult = myAXL.apply_phone(device_name)
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "Phone Configuration Applied Successfully", 'uuid': axlresult['return']}
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
                returned_tags = list(map(str.strip, returned_tags_str.split(',')))
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
    @api.expect(cucm_update_phone_query_args, validate=True)
    def put(self, device_name):
        """
        Updates a Phone Configuration on CUCM
        """
        try:
            cucm_update_phone_query_parsed_args = cucm_update_phone_query_args.parse_args(request)
            cucm_update_phone_query_parsed_args['name'] = device_name
            phone_update_data = {
                "name": device_name,
                "description": cucm_update_phone_query_parsed_args["description"],
                "isActive": cucm_update_phone_query_parsed_args["isActive"]
            }
            axlresult = myAXL.update_phone(phone_data=phone_update_data)
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "Phone Configuration Updated Successfully", 'uuid': axlresult['return']}
        return jsonify(apiresult)


@api.route("/device_search")
class cucm_device_search_api(Resource):
    @api.expect(cucm_device_search_criteria_query_args, validate=True)
    def get(self):
        """
        Perform a Device Search via RisPort70 (Real-Time Information Port) service on CUCM given the search criteria

        This API method executes a SelectCMDevice Request and sets results with returned Response data

        https://developer.cisco.com/docs/sxml/#!risport70-api-reference/selectcmdevice

        """
        try:
            cucm_device_search_criteria_query_parsed_args = cucm_device_search_criteria_query_args.parse_args(request)
            ris_search_criteria = {
                'SelectBy': 'Description',
                'MaxReturnedDevices': 1000,
                'Status': cucm_device_search_criteria_query_parsed_args['Status'],
                'SelectItems': [
                    {
                        'item': [cucm_device_search_criteria_query_parsed_args['Description']]
                    }
                ]
            }
            risresult = mySXMLRisPort70Service.ris_query(search_criteria=ris_search_criteria)
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "Device Search Results Retrieved Successfully",
                     'TotalDevicesFound': risresult['SelectCmDeviceResult']['TotalDevicesFound'],
                     'ris_search_result': risresult}
        return jsonify(apiresult)


@api.route("/service_status")
class cucm_service_status_api(Resource):
    @api.expect(cucm_service_status_query_args, validate=True)
    def get(self):
        """
        Perform a Service Status Query via ControlCenterServicesPort service on CUCM given the service_name

        This API method executes a soapGetServiceStatus Request and sets results with returned Response data

        https://developer.cisco.com/docs/sxml/#!control-center-services-api-reference

        """
        try:
            cucm_service_status_query_parsed_args = cucm_service_status_query_args.parse_args(request)
            service_list = None
            if cucm_service_status_query_parsed_args['Services'] is not None:
                services_str = cucm_service_status_query_parsed_args['Services']
                service_list = list(map(str.strip, services_str.split(',')))
            ccsresult = mySXMLControlCenterServicesService.ccs_get_service_status(service_list=service_list)
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "Service(s) Status Info Retrieved Successfully",
                     'service_info': ccsresult}
        return jsonify(apiresult)
