import re
from time import sleep
from flask import jsonify
from flask import request
from flask import Blueprint
from flask_restplus import Namespace, Resource, fields, reqparse
from flaskr.api.v1.config import default_cucm
from flaskr.cucm.v1.cucm import AXL, PAWS, SXML
from flaskr.api.v1.parsers import cucm_add_phone_query_args
from flaskr.api.v1.parsers import cucm_update_phone_query_args
from flaskr.api.v1.parsers import cucm_list_phones_returned_tags_query_args
from flaskr.api.v1.parsers import cucm_list_phones_search_criteria_query_args
from flaskr.api.v1.parsers import cucm_device_search_criteria_query_args
from flaskr.api.v1.parsers import cucm_service_status_query_args
from flaskr.api.v1.parsers import cucm_update_line_query_args

api = Namespace('cucm', description='Cisco Unified Communications Manager APIs')


myAXL = AXL(default_cucm['host'], default_cucm['username'], default_cucm['password'])
myPAWSVersionService = PAWS(default_cucm['host'], default_cucm['username'], default_cucm['password'], 'VersionService')
mySXMLRisPort70Service = SXML(default_cucm['host'], default_cucm['username'], default_cucm['password'], 'realtimeservice2')
mySXMLControlCenterServicesService = SXML(default_cucm['host'], default_cucm['username'], default_cucm['password'], 'controlcenterservice2')
mySXMLPerfMonService = SXML(default_cucm['host'], default_cucm['username'], default_cucm['password'], 'perfmonservice2')


@api.route("/version")
class cucm_get_version_api(Resource):
    def get(self):
        """
        Returns CUCM Active Software version

        This API method utilizes getActiveVersion PAWS requests along with the supplied parameters
        <br>
        https://developer.cisco.com/site/paws/documents/api-reference/
        """
        try:
            version_info = myPAWSVersionService.get_version()
        except Exception as e:
            result = {'success': False, 'message': str(e)}
            return jsonify(result)
        apiresult = {'success': True, 'message': "CUCM Active Version Retrieved Successfully", 'version': version_info['version']}
        return jsonify(apiresult)


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
            SearchItems = []
            if ',' in cucm_device_search_criteria_query_parsed_args['SearchItems']:
                SearchItems_str = cucm_device_search_criteria_query_parsed_args['SearchItems']
                SearchItems = list(map(str.strip, SearchItems_str.split(',')))
            else:
                SearchItems.append(cucm_device_search_criteria_query_parsed_args['SearchItems'])
            ris_search_criteria = {
                'SelectBy': cucm_device_search_criteria_query_parsed_args['SearchBy'],
                'MaxReturnedDevices': 1000,
                'Status': cucm_device_search_criteria_query_parsed_args['Status'],
                'SelectItems': []
            }
            for SearchItem in SearchItems:
                SelectItem_dict = {'item': SearchItem}
                ris_search_criteria['SelectItems'].append(SelectItem_dict)
            risresult = mySXMLRisPort70Service.ris_query(search_criteria=ris_search_criteria)
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "Device Search Results Retrieved Successfully",
                     'TotalDevicesFound': risresult['SelectCmDeviceResult']['TotalDevicesFound'],
                     'ris_search_result': risresult}
        return jsonify(apiresult)


@api.route("/user/<string:user_name>")
@api.param('user_name', description='CUCM User Name')
class cucm_user_api(Resource):
    def get(self, user_name):
        """
        Retrieves a Phone device configuration from CUCM

        This API method executes an getPhone AXL Request with the supplied device_name
        <br>
        https://pubhub.devnetcloud.com/media/axl-schema-reference/docs/Files/AXLSoap_getPhone.html
        """
        try:
            axlresult = myAXL.get_user(user_name)
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "User Data Retrieved Successfully", 'user_data': axlresult['return']['user']}
        return jsonify(apiresult)


@api.route("/service")
class cucm_service_api(Resource):
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


@api.route("/perfmon")
class cucm_perfmon_api(Resource):
    # CUCM Perfmon Query API Payload Model
    cucm_perfmon_post_data = api.model('perfmon_post_data', {
        "perfmon_class": fields.String(description='Performance Class Name', example='Cisco SIP Stack', required=False),
        "perfmon_counters": fields.List(fields.String(description='Performance Counter Class + Instance + Name',
                                                      example='Cisco CallManager\\RegisteredOtherStationDevices', required=False))
    })

    @api.expect(cucm_perfmon_post_data, validate=True)
    def post(self):
        """
        Query Performance Counters via PerfMon service on CUCM

        This API method executes multiple PerfMon API requests to get the Performance Counters values and sets results with returned Response data

        https://developer.cisco.com/docs/sxml/#!perfmon-api-reference

        """
        try:
            if not ('perfmon_class' in api.payload or 'perfmon_counters' in api.payload):
                raise Exception(f"perfmon_class or perfmon_counters are required in the payload")
            if api.payload.get('perfmon_class'):
                perfmon_class_result = mySXMLPerfMonService.perfmon_query_class(perfmon_class_name=api.payload['perfmon_class'])
            else:
                perfmon_class_result = None
            if api.payload.get('perfmon_counters'):
                perfmon_session_handle = mySXMLPerfMonService.perfmon_open_session()
                perfmon_counters = []
                for counter in api.payload['perfmon_counters']:
                    perfmon_counters.append(f"\\\\{default_cucm['host']}\\" + counter)
                if not mySXMLPerfMonService.perfmon_add_counter(session_handle=perfmon_session_handle, counters=perfmon_counters):
                    mySXMLPerfMonService.perfmon_close_session(session_handle=perfmon_session_handle)
                    raise Exception(f"Failed to Query Counters: {api.payload['perfmon_counters']}")
                perfmon_counters_result = mySXMLPerfMonService.perfmon_collect_session_data(session_handle=perfmon_session_handle)
                if any(("%" in counter) or ("Percentage" in counter) for counter in api.payload['perfmon_counters']):
                    sleep(5)
                    perfmon_counters_result = mySXMLPerfMonService.perfmon_collect_session_data(session_handle=perfmon_session_handle)
                mySXMLPerfMonService.perfmon_close_session(session_handle=perfmon_session_handle)
            else:
                perfmon_counters_result = None
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "PerfMon Data Retrieved Successfully",
                     'perfmon_class_result': perfmon_class_result,
                     'perfmon_counters_result': perfmon_counters_result}
        return jsonify(apiresult)


@api.route("/line/<string:directory_num>")
@api.param('directory_num', description='The Line Directory Number')
class cucm_line_api(Resource):
    @api.expect(cucm_update_line_query_args, validate=True)
    def put(self, directory_num):
        """
        Updates a Line Number configuration and Applies it on CUCM

        This API method executes an updateLine and applyLine AXL Requests with the supplied phone_update_data parameter
        <br>
        https://pubhub.devnetcloud.com/media/axl-schema-reference/docs/Files/AXLSoap_updateLine.html
        <br>
        https://pubhub.devnetcloud.com/media/axl-schema-reference/docs/Files/AXLSoap_applyLine.html
        """
        try:
            cucm_update_line_query_parsed_args = cucm_update_line_query_args.parse_args(request)
            callforwardtovm = cucm_update_line_query_parsed_args['callforwardtovm']

            line_update_data = {
                "pattern": directory_num,
                'callForwardBusy': {'forwardToVoiceMail': callforwardtovm},
                'callForwardBusyInt': {'forwardToVoiceMail': callforwardtovm},
                'callForwardNoAnswer': {'forwardToVoiceMail': callforwardtovm},
                'callForwardNoAnswerInt': {'forwardToVoiceMail': callforwardtovm},
                'callForwardNoCoverage': {'forwardToVoiceMail': callforwardtovm},
                'callForwardNoCoverageInt': {'forwardToVoiceMail': callforwardtovm},
                'callForwardOnFailure': {'forwardToVoiceMail': callforwardtovm},
                'callForwardNotRegistered': {'forwardToVoiceMail': callforwardtovm},
                'callForwardNotRegisteredInt': {'forwardToVoiceMail': callforwardtovm}
            }
            axl_update_line_result = myAXL.update_line(line_data=line_update_data)
            myAXL.apply_line(directory_num, 'DN_PT')
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "Line Configuration Updated & Applied Successfully",
                     'uuid': axl_update_line_result['return']}
        return jsonify(apiresult)
