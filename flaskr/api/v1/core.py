from flask import jsonify
from flask import request
from werkzeug.datastructures import ImmutableMultiDict
from flask_restx import Namespace, Resource, fields, reqparse, inputs
from flaskr.api.v1.cms import myCUCMuds
from flaskr.api.v1.cucm import cucm_get_version_api, cucm_user_api
from flaskr.api.v1.cucm import cucm_line_api, cucm_phone_api
from flaskr.api.v1.cuc import cuc_version_api
from flaskr.api.v1.wbxc import wbxc_user_api, wbxc_user_enable_api, wbxc_user_disable_api
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
            cucm_version_data = cucm_get_version_api.get(Resource).json
            if not cucm_version_data['success']:
                raise Exception(cucm_version_data['message'])
            cuc_version_data = cuc_version_api.get(Resource)
            if not cuc_version_data['success']:
                raise Exception(cuc_version_data['message'])
        except Exception as e:
            apiresult = {'success': False, 'message': str(e)}
            return jsonify(apiresult)
        apiresult = {'success': True, 'message': "Active Versions Retrieved Successfully",
                     'cucm_version': cucm_version_data['version'],
                     'cuc_version': cuc_version_data['response']['version']}
        return jsonify(apiresult)


@api.route("/users/<string:userid>")
@api.param('userid', description='End user ID')
class core_users_api(Resource):
    def get(self, userid):
        """
        Retrieves user data based on where the user is configured (Webex Calling or UCM)
        """
        try:
            is_ucm_user = False
            is_wbxc_user = False

            # Retrieve Webex Calling user data
            wbxc_user_data = wbxc_user_api.get(Resource, userid).json
            if wbxc_user_data['success']:
                is_wbxc_user = True
            else:
                if 'no user found' not in wbxc_user_data['message'].lower():
                    # wbxc_user_api reported a failure other than user not found
                    raise Exception(wbxc_user_data['message'])

            # Retrieve CUCM user data
            cucm_user_data = cucm_user_api.get(Resource, userid).json
            if cucm_user_data['success']:
                is_ucm_user = True
            else:
                if 'not found' not in cucm_user_data['message'].lower():
                    # cucm_user_api.get reported a failure other than user not found
                    raise Exception(cucm_user_data['message'])

            # Check if user does not exist in either place
            if not is_ucm_user and not is_wbxc_user:
                result = {'success': True,
                          'message': f"User {userid} not found",
                          'is_wbxc_user': is_wbxc_user,
                          'is_wbxc_enabled': False,
                          'is_ucm_user': is_ucm_user,
                          'is_ucm_enabled': False,
                          'phonesystem': 'User not found on either system'}

            else:
                # Decide if this user is a UCM user based on the home cluster field being set
                is_ucm_enabled = True if cucm_user_data['user_data']['homeCluster'].lower() == "true" else False
                try:
                    # Decide if this user is a Webex Calling user based on the locationID field being set
                    is_wbxc_enabled = True if wbxc_user_data['user_data']['locationId'] else False
                except KeyError:
                    is_wbxc_enabled = False

                if is_wbxc_enabled and is_ucm_enabled:
                    # Both CUCM and Webex Calling
                    result = {'success': True,
                              'message': f"Located {userid} on both Webex Calling and CUCM",
                              'is_wbxc_user': is_wbxc_user,
                              'is_wbxc_enabled': is_wbxc_enabled,
                              'is_ucm_user': is_ucm_user,
                              'is_ucm_enabled': is_wbxc_enabled,
                              'phonesystem': 'Both Webex Calling and Unified CM',
                              'wbxc_user_data': wbxc_user_data, 'cucm_user_data': cucm_user_data}
                elif is_wbxc_enabled:
                    # Webex Calling user
                    result = {'success': True,
                              'message': f"Successfully located {userid} on Webex Calling",
                              'is_wbxc_user': is_wbxc_user,
                              'is_wbxc_enabled': is_wbxc_enabled,
                              'is_ucm_user': is_ucm_user,
                              'is_ucm_enabled': is_ucm_enabled,
                              'phonesystem': 'Webex Calling', 'wbxc_user_data': wbxc_user_data['user_data']}
                elif is_ucm_enabled:
                    # CUCM User
                    result = {'success': True,
                              'message': f"Successfully located {userid} on Unified CM",
                              'is_wbxc_user': is_wbxc_user,
                              'is_wbxc_enabled': is_wbxc_enabled,
                              'is_ucm_user': is_ucm_user,
                              'is_ucm_enabled': is_ucm_enabled,
                              'phonesystem': 'Unified CM', 'cucm_user_data': cucm_user_data['user_data']}
                else:
                    # Neither CUCM nor Webex Calling
                    result = {'success': True,
                              'message': f"Located {userid} on neither Webex Calling nor CUCM",
                              'is_wbxc_user': is_wbxc_user,
                              'is_wbxc_enabled': is_wbxc_enabled,
                              'is_ucm_user': is_ucm_user,
                              'is_ucm_enabled': is_ucm_enabled,
                              'phonesystem': 'Neither Webex Calling nor Unified CM'}

        except Exception as e:
            result = {'success': False, 'message': str(e)}

        return jsonify(result)


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


@api.route("/migrate_cloud/<string:userid>")
@api.param('userid', 'The userid (alias) of the user')
class core_migrate_cloud_api(Resource):
    def put(self, userid):
        """
        Migrates a user from UCM to Webex Calling
        Performs the following:
        1. WxC: Activate user for WxC
        2. UCM: Updates User turning off homeCluster setting
        3. UCM: Delete UCM CSF Device
        """
        try:
            # Enable user for Webex Calling
            wbxc_user_result = wbxc_user_enable_api.put(Resource, userid).json
            if not wbxc_user_result['success']:
                raise Exception(wbxc_user_result['message'])

            # UCM: Updates User with homeCluster setting
            request.args = ImmutableMultiDict([('homecluster', 'false')])
            cucm_user_api_result = cucm_user_api.put(Resource, userid=userid).json
            if not cucm_user_api_result['success']:
                raise Exception(cucm_user_api_result['message'])

            # UCM: Delete CSF Device
            cucm_phone_api_result = cucm_phone_api.delete(Resource, device_name='CSF' + userid.upper()).json
            if not cucm_phone_api_result['success']:
                raise Exception(cucm_phone_api_result['message'])

        except Exception as e:
            result = {'success': False, 'message': str(e)}
            return result
        return {'success': True, 'message': f"Successfully migrated {userid} to Webex Calling"}


@api.route("/migrate_onprem/<string:userid>")
@api.param('userid', 'The userid (alias) of the user')
class core_migrate_onprem_api(Resource):
    def put(self, userid):
        """
        Migrates a user from Webex Calling to UCM
        Performs the following:
        1. UCM: Creates UCM CSF Device with DN
        2. UCM: Updates User with homeCluster setting
        3. WxC: Deactivate user
        """
        try:
            # Set defaults for CSF device to be added
            request.args = ImmutableMultiDict([('description', 'Cisco Live LTRCOL2574 - ' + userid),
                                               ('phonetype', 'Cisco Unified Client Services Framework'),
                                               ('ownerUserName', userid),
                                               ('calleridname', userid)])

            # UCM: Add CSF Device
            cucm_phone_api_result = cucm_phone_api.post(Resource, device_name='CSF' + userid.upper()).json
            if not cucm_phone_api_result['success']:
                raise Exception(cucm_phone_api_result['message'])

            # UCM: Updates User with homeCluster setting
            request.args = ImmutableMultiDict([('homecluster', 'true')])
            cucm_user_api_result = cucm_user_api.put(Resource, userid=userid).json
            if not cucm_user_api_result['success']:
                raise Exception(cucm_user_api_result['message'])

            # WxC: Deactivate for Webex Calling
            wbxc_user_result = wbxc_user_disable_api.put(Resource, userid).json
            if not wbxc_user_result['success']:
                raise Exception(wbxc_user_result['message'])

        except Exception as e:
            result = {'success': False, 'message': str(e)}
            return result
        return {'success': True, 'message': f"Successfully migrated {userid} to Unified CM"}
