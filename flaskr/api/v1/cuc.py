from flask import request
from flask_restplus import Namespace, Resource
from flaskr.api.v1.config import default_cuc
from flaskr.cuc.v1.cupi import CUPI
from flaskr.api.v1.parsers import cuc_importldap_user_post_args
from flaskr.api.v1.parsers import cuc_users_get_args
from flaskr.api.v1.parsers import cuc_users_put_args

api = Namespace('cuc', description='Cisco Unity Connection APIs')


def get_search_params(args):
    """
    Returns CUC search parameters from request arguments as a dictionary. 
    Builds a valid query parameter from column/match_type/search string.
    """
    params = {'sortorder': args.get('sortorder'),
              'rowsPerPage': args.get('rowsPerPage'),
              'pageNumber': args.get('pageNumber')}

    # Make sure if search is supplied that the 'query' is built properly
    if args.get('search') is not None:
        params['query'] = '({} {} {})'.format(args.get('column'), args.get('match_type'), args.get('search'))
    return params


@api.route("/ldap_users")
class cuc_import_ldapuser_api(Resource):
    @api.expect(cuc_users_get_args, validate=True)
    def get(self, host=default_cuc['host'], port=default_cuc['port'],
            username=default_cuc['username'], password=default_cuc['password']):
        """
        Retrieves LDAP users synched to Unity Connection.
        """
        args = cuc_users_get_args.parse_args(request)
        params = get_search_params(args)

        cuc = CUPI(default_cuc['host'], default_cuc['username'],
                   default_cuc['password'], port=default_cuc['port'])
        return cuc.get_ldapusers(parameters=params)


@api.route("/users")
class cuc_get_user_api(Resource):
    @api.expect(cuc_users_get_args, validate=True)
    def get(self):
        """
        Returns Unity Connection users (with and without voicemail mailboxes).
        """
        args = cuc_users_get_args.parse_args(request)
        params = get_search_params(args)

        cuc = CUPI(default_cuc['host'], default_cuc['username'],
                   default_cuc['password'], port=default_cuc['port'])
        return cuc.get_users(parameters=params)


@api.route("/users/<userid>")
@api.param('userid', 'The userid (alias) of the user')
class cuc_user_api(Resource):
    def get(self, userid, host=default_cuc['host'], port=default_cuc['port'],
            username=default_cuc['username'], password=default_cuc['password']):
        """
        Get user from Unity Connection using the user ID / alias.
        """
        cuc = CUPI(default_cuc['host'], default_cuc['username'],
                   default_cuc['password'], port=default_cuc['port'])
        return cuc.get_user_by_id(userid)

    @api.expect(cuc_importldap_user_post_args, validate=True)
    def post(self, userid, host=default_cuc['host'], port=default_cuc['port'],
            username=default_cuc['username'], password=default_cuc['password']):
        """
        Import Unity Connection user from LDAP using the user ID / alias.
        """
        args = request.args.to_dict()
        if 'templateAlias' not in args:
            args['templateAlias'] = 'voicemailusertemplate'
        cuc = CUPI(default_cuc['host'], default_cuc['username'],
                   default_cuc['password'], port=default_cuc['port'])

        # Look up pkid from user ID
        params = {'query': '(alias is {})'.format(userid)}
        user = cuc.get_ldapusers(parameters=params)

        # Either a single user was returned, no users were found, or an error occurred.
        try:
            # Single user found.  Import the user using the pkid and settings
            if user['response']['@total'] == '1':
                args['pkid'] = user['response']['ImportUser'][0]['pkid']                    
                return cuc.import_ldapuser(parameters={'templateAlias': args['templateAlias']}, payload=args)
            else:
                # No users were found
                return {'success': False,
                        'msg': 'Found {} users to import with user id {}'.format(user['response']['@total'], userid), 
                        'response': user['response']}
        except KeyError:
            # Return the errored user look up data
            return user

    @api.expect(cuc_users_put_args, validate=True)
    def put(self, userid, host=default_cuc['host'], port=default_cuc['port'],
            username=default_cuc['username'], password=default_cuc['password']):
        """
        Update user from Unity Connection using the user ID / alias.
        """
        user_settings = ['ListInDirectory', 'IsVmEnrolled']
        args = request.args.to_dict()
        if len(args) > 0:
            cuc = CUPI(default_cuc['host'], default_cuc['username'],
                    default_cuc['password'], port=default_cuc['port'])
            # Look up the CUC user
            user = cuc.get_user_by_id(userid)

            # Either a single user was returned, no users were found, or an error occurred.
            try:
                # Single user returned, process it
                if user['response']['@total'] == '1':

                    # Check if any user settings were supplied
                    if any(user_setting in args for user_setting in user_settings):
                        payload = {}
                        for user_setting in user_settings:
                            if user_setting in args:
                                payload[user_setting] = args[user_setting]
                        user_result = cuc.update_user(id=user['response']['ObjectId'], payload=payload)
                        # If the update failed, return; don't continue to try to update again with creds
                        if not user_result['success']:
                            return user_result

                    # Check if PIN or ResetMailbox were supplied
                    if 'PIN' in args or 'ResetMailbox' in args:
                        cred_payload = {}
                        if 'PIN' in args:
                            cred_payload['Credentials'] = args['PIN']                            
                        if 'ResetMailbox' in args:
                            # ResetMailbox is actually a matter of resetting HackCount and TImeHacked
                            cred_payload['HackCount'] = 0
                            cred_payload['TimeHacked'] = []
                        # Update the user's credentials
                        return cuc.update_pin(id=user['response']['ObjectId'], payload=cred_payload)
                else:
                    # Zero users returned
                    return {'success': False,
                            'msg': 'Found {} users with user id {}'.format(user['response']['@total'], userid), 
                            'response': user['response']}
            except KeyError:
                # Error in the user query, no @total key found
                return user
        else:
            # No arguments supplied besides the userid
            return {'success': True, 'message': 'No changes specified for {}'.format(userid), 'response': ''}

    def delete(self, userid, host=default_cuc['host'], port=default_cuc['port'],
               username=default_cuc['username'], password=default_cuc['password']):
        """
        Delete user from Unity Connection using the user ID / alias.
        """
        cuc = CUPI(default_cuc['host'], default_cuc['username'],
                   default_cuc['password'], port=default_cuc['port'])
        # Look up the CUC user
        user = cuc.get_user_by_id(userid)

        # Either a single user was returned, no users were found, or an error occurred.
        try:
            # Single user found.  Delete the user using the object ID
            if user['response']['@total'] == '1':
                return cuc.delete_user(id=user['response']['ObjectId'])
            else:
                # No users were found
                return {'success': False,
                        'msg': 'Found {} users to import with user id {}'.format(user['response']['@total'], userid),
                        'response': user['response']}
        except KeyError:
            # Return the errored user look up data
            return user
