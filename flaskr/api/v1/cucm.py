import re
from time import sleep
from flask import jsonify
from flask import request
from flask import Blueprint
from flask_restx import Namespace, Resource, fields, reqparse
from flaskr.cucm.v1.cucm import AXL, PAWS, SXML
from flaskr.api.v1.parsers import cucm_add_phone_query_args
from flaskr.api.v1.parsers import cucm_update_phone_query_args
from flaskr.api.v1.parsers import cucm_list_phones_returned_tags_query_args
from flaskr.api.v1.parsers import cucm_list_phones_search_criteria_query_args
from flaskr.api.v1.parsers import cucm_device_search_criteria_query_args
from flaskr.api.v1.parsers import cucm_service_status_query_args
from flaskr.api.v1.parsers import cucm_update_line_query_args
from flaskr.api.v1.parsers import cucm_update_user_query_args
from os import getenv

api = Namespace('cucm', description='Cisco Unified Communications Manager APIs')

# Read environment variables
cucm_host = getenv('CUCM_HOSTNAME')
cucm_user = getenv('CUCM_USERNAME')
cucm_pass = getenv('CUCM_PASSWORD')

# Core CUCM SOAP API Python Class Instances

###########################################


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
    def get(self, device_name):
        """
        Retrieves a Phone device configuration from CUCM

        This API method executes an getPhone AXL Request with the supplied device_name
        <br>
        https://pubhub.devnetcloud.com/media/axl-schema-reference/docs/Files/AXLSoap_getPhone.html
        """
        try:
            raise Exception('Not implemented yet!!')
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "Phone Data Retrieved Successfully", 'phone_data': axlresult['return']['phone']}
        return jsonify(apiresult)

    @api.expect(cucm_add_phone_query_args, validate=True)
    def post(self, device_name):
        """
        Adds a new Phone Device to CUCM

        This API method utilizes AXL getUser, addPhone and updateUser requests along with the supplied parameters
        <br>
        https://pubhub.devnetcloud.com/media/axl-schema-reference/docs/Files/AXLSoap_getUser.html
        <br>
        https://pubhub.devnetcloud.com/media/axl-schema-reference/docs/Files/AXLSoap_addPhone.html
        <br>
        https://pubhub.devnetcloud.com/media/axl-schema-reference/docs/Files/AXLSoap_updateUser.html
        <br>
        """
        try:
            raise Exception('Not implemented yet!!')
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "Phone Added Successfully",
                     'phone_uuid': axl_add_phone_result['return'],
                     'user_uuid': axl_update_user_result['return']}
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
            raise Exception('Not implemented yet!!')
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "Phone Configuration Updated & Applied Successfully",
                     'uuid': axl_update_phone_result['return']}
        return jsonify(apiresult)

    def delete(self, device_name):
        """
        Deletes a Phone device from CUCM

        This API method executes an removePhone AXL Request with the supplied device_name
        <br>
        https://pubhub.devnetcloud.com/media/axl-schema-reference/docs/Files/AXLSoap_removePhone.html
        """
        try:
            raise Exception('Not implemented yet!!')
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "Phone Successfully Deleted", 'uuid': axlresult['return']}
        return jsonify(apiresult)


@api.route("/user/<string:userid>")
@api.param('userid', description='CUCM End User ID')
class cucm_user_api(Resource):
    def get(self, userid):
        """
        Retrieves an End User's configuration from CUCM

        This API method executes an getUser AXL Request with the supplied userid
        <br>
        https://pubhub.devnetcloud.com/media/axl-schema-reference/docs/Files/AXLSoap_getUser.html
        """
        try:
            raise Exception('Not implemented yet!!')
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "User Data Retrieved Successfully", 'user_data': axlresult['return']['user']}
        return jsonify(apiresult)

    @api.expect(cucm_update_user_query_args, validate=True)
    def put(self, userid):
        """
        Updates an End User's Home Cluster configuration on CUCM

        This API method executes an updateUser AXL Request with the supplied userid
        <br>
        https://pubhub.devnetcloud.com/media/axl-schema-reference/docs/Files/AXLSoap_updateUser.html
        """
        try:
            cucm_update_user_query_args_parsed_args = cucm_update_user_query_args.parse_args(request)         
            user_data = {
                'userid': userid,
                'homeCluster': cucm_update_user_query_args_parsed_args['homecluster']
            }
            axlresult = myAXL.update_user(user_data=user_data)
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "User Updated Successfully", 'user_data': axlresult['return']}
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
            raise Exception('Not implemented yet!!')
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "Device Search Results Retrieved Successfully",
                     'TotalDevicesFound': risresult['SelectCmDeviceResult']['TotalDevicesFound'],
                     'ris_search_result': risresult}
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
            raise Exception('Not implemented yet!!')
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
    def post(self, perfmon_class=None, perfmon_counters=None):

        """
        Query Performance Counters via PerfMon service on CUCM

        This API Method needs to be a POST method even though we are not creating any new items/resources because Swagger UI does
        not allow a payload body for GET requests.

        This API method executes multiple PerfMon API requests to get the Performance Counters values and sets results with returned Response data

        https://developer.cisco.com/docs/sxml/#!perfmon-api-reference

        """
        try:
            raise Exception('Not implemented yet!!')
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "PerfMon Data Retrieved Successfully",
                     'perfmon_class_result': perfmon_class_result,
                     'perfmon_counters_result': perfmon_counters_result}
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
