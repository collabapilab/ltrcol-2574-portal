
from flask import request
from flask_restplus import Namespace, Resource
from flaskr.api.v1.config import default_cucm
from flaskr.rest.v1.rest import REST
from flaskr.uds.v1.uds import UDS

api = Namespace('uc', description='UC Solution Tasks API')


@api.route("/vm/<userid>")
class uc_vm_api(Resource):
    def delete(self, userid):
        '''
        Add/remove voicemail capabilities for a user
        '''

        # query UDS for user & directory_num
        cucm_uds = UDS(default_cucm['host'])
        user = cucm_uds.get_user(parameters={'username': userid})
        if user['success']:
            # Make sure one user was found
            if user['response']['users']['@totalCount'] == '1':
                directory_num = user['response']['users']['user'][0]['phoneNumber']
                uc_portal = REST('0.0.0.0', secure=False,
                                 base_url='/api/v1', port=5000)
                # disable the vm account
                cuc_user = uc_portal._send_request(
                    http_method='DELETE', api_method='cuc/users/' + userid)
                if cuc_user['success']:
                    cuc_user = uc_portal._check_response(cuc_user)
                if cuc_user['success']:
                    cucm_line = uc_portal._send_request(http_method='PUT',
                                                        api_method='cucm/line/' +
                                                        directory_num + '?callforwardtovm=false')
                    print(cucm_line)
                    if cucm_line['success']:
                        return {'success': True, 'message': 'Successfully disabled voicemail for {}'.format(userid)}
                    else:
                        return cucm_line
                else:
                    return cuc_user

            else:
                return {'success': False,
                        'message': 'Found {} users with userid "{}"'.format(
                            user['response']['users']['@totalCount'], args['userid'])}
        else:
            # User lookup failed completely
            return user


    def post(self, userid):
        '''
        Add/remove voicemail capabilities for a user
        '''

        # query UDS for user & directory_num
        cucm_uds = UDS(default_cucm['host'])
        user = cucm_uds.get_user(parameters={'username': userid})
        if user['success']:
            # Make sure one user was found
            if user['response']['users']['@totalCount'] == '1':
                directory_num = user['response']['users']['user'][0]['phoneNumber']
                uc_portal = REST('0.0.0.0', secure=False, base_url='/api/v1', port=5000)

                # enable the vm account
                cuc_user = uc_portal._send_request(
                    http_method='POST', api_method='cuc/users/' + userid)
                if cuc_user['success']:
                    cuc_user = uc_portal._check_response(cuc_user)

                if cuc_user['success']:
                    cucm_line = uc_portal._send_request(http_method='PUT',
                                                        api_method='cucm/line/' + 
                                                        directory_num + '?callforwardtovm=true')
                    print(cucm_line)
                    if cucm_line['success']:
                        return {'success': True, 'message': 'Successfully enabled voicemail for {}'.format(userid)}
                    else:
                        return cucm_line
                else:
                    return cuc_user

            else:
                return {'success': False,
                        'message': 'Found {} users with userid "{}"'.format(
                            user['response']['users']['@totalCount'], args['userid'])}
        else:
            # User lookup failed completely
            return user
