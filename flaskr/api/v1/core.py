import re
from flask import json
from flask import jsonify
from flask import request
from flask import Blueprint
from flask_restplus import Namespace, Resource, fields, reqparse, inputs
from flaskr.api.v1.cms import myCUCMuds
from flaskr.api.v1.cucm import cucm_get_version_api
from flaskr.api.v1.cucm import cucm_line_api
from flaskr.api.v1.cuc import cuc_version_api
from flaskr.api.v1.cuc import cuc_user_api
from flaskr.api.v1.parsers import cucm_update_line_query_args
from flaskr.api.v1.parsers import cuc_importldap_user_post_args

api = Namespace('core', description='Core APIs')


@api.route("/versions")
class core_versions_api(Resource):
    def get(self):
        """
        Core Function that demonstrates utilizing multiple Flask Rest APIs
        """
        try:
            cucm_version_data = cucm_get_version_api.get(Resource)
            if not cucm_version_data['success']:
                raise Exception(cucm_version_data['message'])
            cuc_version_data = cuc_version_api.get(Resource)
            if not cuc_version_data['success']:
                raise Exception(cuc_version_data['message'])
        except Exception as e:
            result = {'success': False, 'message': str(e)}
            return result
        apiresult = {'success': True, 'message': "Active Versions Retrieved Successfully",
                     'cucm_version': cucm_version_data['version'],
                     'cuc_version': cuc_version_data['response']['version']}
        return apiresult


@api.route("/vmusers/<string:userid>")
@api.param('userid', 'The userid (alias) of the user')
class core_vmusers_api(Resource):
    @api.expect(cuc_importldap_user_post_args, cucm_update_line_query_args, validate=True)
    def put(self, userid):
        """
        Enable User's VoiceMail Services and forwarding to Voicemail
        """
        try:
            # Look up user via CUCM UDS, if wrong user no need to proceed
            user_data = myCUCMuds.get_user(userid)
            if not user_data['success']:
                raise Exception(user_data['message'])
            # Enable User's VoiceMail account
            cuc_user_api_result = cuc_user_api.post(Resource, userid=userid)
            if not cuc_user_api_result['success']:
                raise Exception(cuc_user_api_result['message'])
            user_dn = user_data['response']['phoneNumber']
            # Forward User's DN to VoiceMail
            cucm_line_api_result = cucm_line_api.put(Resource, directory_num=user_dn)
            if not cucm_line_api_result['success']:
                raise Exception(cucm_line_api_result['message'])
        except Exception as e:
            result = {'success': False, 'message': str(e)}
            return result
        apiresult = {'success': True, 'message': "Successfully enabled User for VoiceMail Services"}
        return apiresult

    def delete(self, userid):
        """
        Disable User's VoiceMail Services and forwarding to Voicemail
        """
        try:
            # Look up user via CUCM UDS, if wrong user no need to proceed
            user_data = myCUCMuds.get_user(userid)
            if not user_data['success']:
                raise Exception(user_data['message'])
            user_dn = user_data['response']['phoneNumber']
            # Disable User's VoiceMail account
            cuc_user_api_result = cuc_user_api.delete(Resource, userid=userid)
            if not cuc_user_api_result['success']:
                raise Exception(cuc_user_api_result['message'])
            # Disable Forwarding to VoiceMail
            cucm_update_line_query_args.replace_argument('callforwardtovm', type=inputs.boolean, default=False)
            cucm_line_api_result = cucm_line_api.put(Resource, directory_num=user_dn)
            if not cucm_line_api_result['success']:
                raise Exception(cucm_line_api_result['message'])
        except Exception as e:
            result = {'success': False, 'message': str(e)}
            return result
        apiresult = {'success': True, 'message': "Successfully disabled User for VoiceMail Services"}
        return apiresult
