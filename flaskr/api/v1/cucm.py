import re
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
mySXMLPerfMonService = SXML(default_cucm['host'], default_cucm['username'], default_cucm['password'], 'perfmonservice2')


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


@api.route("/phone/<string:device_name>")
@api.param('device_name', description='The Name of the Phone Device')
class cucm_phone_api(Resource):
    @api.expect(cucm_add_phone_query_args, validate=True)
    def post(self, device_name):
        """
        Adds a new Phone Device to CUCM

        This API method utilizes AXL addPhone and getUser requests along with the supplied parameters
        <br>
        https://pubhub.devnetcloud.com/media/axl-schema-reference/docs/Files/AXLSoap_addPhone.html
        <br>
        https://pubhub.devnetcloud.com/media/axl-schema-reference/docs/Files/AXLSoap_getUser.html
        """
        try:
            cucm_add_phone_query_parsed_args = cucm_add_phone_query_args.parse_args(request)
            axl_get_user_result = myAXL.get_user(userid=cucm_add_phone_query_parsed_args['ownerUserName'])
            user_telephoneNumber = None
            if axl_get_user_result['return']['user'].get('telephoneNumber'):
                user_telephoneNumber = re.sub(r"^\+", "\\+", axl_get_user_result['return']['user']['telephoneNumber'])
            user_associatedDevices = []
            if axl_get_user_result['return']['user']['associatedDevices']:
                user_associatedDevices = axl_get_user_result['return']['user']['associatedDevices']['device']

            cucm_add_phone_data_dict = {
                "name": device_name,
                "description": cucm_add_phone_query_parsed_args['description'],
                "product": cucm_add_phone_query_parsed_args['phonetype'],
                "class": "Phone",
                "protocol": "SIP",
                "protocolSide": "User",
                "commonPhoneConfigName": "Standard Common Phone Profile",
                "devicePoolName": "Default",
                "locationName": "Hub_None",
                "securityProfileName": "Universal Device Template - Model-independent Security Profile",
                "sipProfileName": "Standard SIP Profile",
                "ownerUserName": cucm_add_phone_query_parsed_args['ownerUserName'],
                "lines": {
                    "line": {
                        "index": "1",
                        "dirn": {
                            "pattern": user_telephoneNumber,
                            "routePartitionName": 'DN_PT'
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

            axl_add_phone_result = myAXL.add_phone(phone_data=cucm_add_phone_data_dict)
            user_associatedDevices.append(device_name)
            cucm_update_user_data_dict = {
                "userid": cucm_add_phone_query_parsed_args['ownerUserName'],
                "associatedDevices": {
                    'device': user_associatedDevices
                }
            }
            axl_update_user_result = myAXL.update_user(user_data=cucm_update_user_data_dict)
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "Phone Added Successfully",
                     'phone_uuid': axl_add_phone_result['return'],
                     'user_uuid': axl_update_user_result['return']}
        return jsonify(apiresult)

    def get(self, device_name):
        """
        Retrieves a Phone device configuration from CUCM

        This API method executes an getPhone AXL Request with the supplied device_name
        <br>
        https://pubhub.devnetcloud.com/media/axl-schema-reference/docs/Files/AXLSoap_getPhone.html
        """
        try:
            axlresult = myAXL.get_phone(device_name)
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "Phone Data Retrieved Successfully", 'phone_data': axlresult['return']['phone']}
        return jsonify(apiresult)

    def delete(self, device_name):
        """
        Deletes a Phone device from CUCM

        This API method executes an removePhone AXL Request with the supplied device_name
        <br>
        https://pubhub.devnetcloud.com/media/axl-schema-reference/docs/Files/AXLSoap_removePhone.html
        """
        try:
            axlresult = myAXL.delete_phone(device_name)
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "Phone Successfully Deleted", 'uuid': axlresult['return']}
        return jsonify(apiresult)

    @api.expect(cucm_update_phone_query_args, validate=True)
    def put(self, device_name):
        """
        Updates a Phone Device configuration and Applies it on CUCM

        This API method executes an updatePhone and applyPhone AXL Requests with the supplied phone_update_data parameter
        <br>
        https://pubhub.devnetcloud.com/media/axl-schema-reference/docs/Files/AXLSoap_updatePhone.html
        <br>
        https://pubhub.devnetcloud.com/media/axl-schema-reference/docs/Files/AXLSoap_applyPhone.html
        """
        try:
            cucm_update_phone_query_parsed_args = cucm_update_phone_query_args.parse_args(request)
            phone_update_data = {
                "name": device_name,
                "description": cucm_update_phone_query_parsed_args["description"],
                "isActive": cucm_update_phone_query_parsed_args["isActive"],
                "callingSearchSpaceName": cucm_update_phone_query_parsed_args["callingSearchSpaceName"]
            }
            axl_update_phone_result = myAXL.update_phone(phone_data=phone_update_data)
            myAXL.apply_phone(device_name)
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "Phone Configuration Updated & Applied Successfully",
                     'uuid': axl_update_phone_result['return']}
        return jsonify(apiresult)


@api.route("/apply_phone/<string:device_name>")
@api.param('device_name', description='The Name of the Phone Device')
class cucm_apply_phone_api(Resource):
    def put(self, device_name):
        """
        Applies a Phone Device Configuration on CUCM
        """
        try:
            axlresult = myAXL.apply_phone(device_name)
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "Phone Configuration Applied Successfully", 'uuid': axlresult['return']}
        return jsonify(apiresult)


@api.route("/phones")
class cucm_list_phone_api(Resource):
    @api.expect(cucm_list_phones_search_criteria_query_args, cucm_list_phones_returned_tags_query_args, validate=True)
    def get(self):
        """
        Lists all provisioned phone details from CUCM

        This API method executes listPhone AXL Request with the supplied search criteria
        <br>
        https://pubhub.devnetcloud.com/media/axl-schema-reference/docs/Files/AXLSoap_listPhone.html#Link986

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


@api.route("/perfmon_query")
class cucm_perfmon_query_api(Resource):
    def get(self):
        """
        Perform a Perfmon Query via PerfMon service on CUCM

        This API method executes a perfmonCollectCounterData Request and sets results with returned Response data

        https://developer.cisco.com/docs/sxml/#!perfmon-api-reference

        """
        try:
            perfmonresult = mySXMLPerfMonService.perfmon_query(perfmon_object="Cisco CallManager")
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "PerfMon Data Retrieved Successfully",
                     'perfmon_data': perfmonresult}
        return jsonify(apiresult)
