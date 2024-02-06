from flask import request
from flask_restx import Namespace, Resource
from flaskr.cuc.v1.cupi import CUPI
from flaskr.api.v1.parsers import cuc_importldap_user_post_args
from flaskr.api.v1.parsers import cuc_users_get_args
from flaskr.api.v1.parsers import cuc_users_put_args
from os import getenv

api = Namespace('cuc', description='Cisco Unity Connection APIs')


@api.route("/version")
class cuc_version_api(Resource):
    def get(self):
        """
        Retrieves Unity Connection version.
        """
        pass

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
    def get(self):
        """
        Retrieves LDAP users synched to Unity Connection.
        """
        # Read arguments: column, match_type, search, sortorder, rowsPerPage, pageNumber
        args = cuc_users_get_args.parse_args(request)
        params = get_search_params(args)


def get_user_by_id(userid):
    '''
    Get a voicemail user from the Unity Connection system by user alias.

    Reference:
    https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/connection/REST-API/CUPI_API/b_CUPI-API/b_CUPI-API_chapter_0111.html#id_38638
    '''

    # Build the parameter dictionary for the request
    pass


@api.route("/users/<userid>")
@api.param('userid', 'The userid (alias) of the user')
class cuc_user_api(Resource):
    def get(self, userid):
        """
        Get user from Unity Connection using the user ID / alias.
        """
        pass

    @api.expect(cuc_importldap_user_post_args, validate=True)
    def post(self, userid):
        """
        Import Unity Connection user from LDAP using the user ID / alias.
        """
        # Read arguments: ListInDirectory, IsVmEnrolled, PIN, and/or ResetMailbox
        args = cuc_importldap_user_post_args.parse_args(request)
        if 'templateAlias' not in args:
            args['templateAlias'] = 'voicemailusertemplate'

        # Look up pkid from user ID

    @api.expect(cuc_users_put_args, validate=True)
    def put(self, userid):
        """
        Update user from Unity Connection using the user ID / alias.
        """
        # Need to distinguish which arguments go with which update, since they're different methods
        user_settings = ['ListInDirectory', 'IsVmEnrolled']
        pin_settings = ['PIN', 'ResetMailbox']
        # Read arguments: ListInDirectory, IsVmEnrolled, PIN, and/or ResetMailbox
        args = cuc_users_put_args.parse_args(request)

        # If no arguments were detected, there's nothing to do

    def delete(self, userid):
        """
        Delete user from Unity Connection using the user ID / alias.
        """
        # Look up the CUC user
        pass
