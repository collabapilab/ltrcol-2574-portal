from flask import request
from flask_restplus import Namespace, Resource, reqparse
from flaskr.cuc.v1.cupi import CUPI

api = Namespace('cuc', description='Cisco Unity Connection APIs')

default_cuc = {
    'host': 'cuc1a.pod31.col.lab',
    'port': 443,
    'username': 'admin',
    'password': 'c1sco123'
}


def get_search_params(args):
    """
      Returns search parameters from request arguments and returns them in a parameter
      dictionary. Determines if all the column/match_type/search string have been
      supplied to build a query parameter
    """
    params = {'sortorder': args.get('sortorder'),
              'rowsPerPage': args.get('rowsPerPage'),
              'pageNumber': args.get('pageNumber')}

    if args.get('search') is not None:
      params['query'] = '({} {} {})'.format(args.get('column'), args.get('match_type'), args.get('search'))

    return params


# CUC querying arguments
query_args = reqparse.RequestParser()
query_args.add_argument('column', type=str, required=False,
                        help='Column to search', default='alias')
query_args.add_argument('match_type', type=str, required=False, choices=[
                        'startswith', 'is'], help='Order of return values', default='is')
query_args.add_argument('search', type=str, required=False, help='Query string')
query_args.add_argument('sortorder', type=str, required=False, choices=[
                        'asc', 'desc'], help='Order of return values', default='asc')
query_args.add_argument('rowsPerPage', type=int, required=False,
                        help='Number of rows to return', default=100)
query_args.add_argument('pageNumber', type=int, required=False,
                        help='Page # to return', default=1)


@api.route("/users")
class cuc_get_user_api(Resource):
    @api.expect(query_args, validate=True)
    def get(self):
        """
        Returns Unity Connection users (with and without voicemail mailboxes).
        """
        args = query_args.parse_args(request)
        params = get_search_params(args)

        cuc = CUPI(default_cuc['host'], default_cuc['username'],
                   default_cuc['password'], port=default_cuc['port'])
        return cuc.get_users(parameters=params)


@api.route("/ldapusers")
class cuc_get_ldapuser_api(Resource):
    @api.expect(query_args, validate=True)
    def get(self, host=default_cuc['host'], port=default_cuc['port'],
            username=default_cuc['username'], password=default_cuc['password']):
        """
        Retrieves LDAP users synched to Unity Connection.
        """
        args = query_args.parse_args(request)
        params = get_search_params(args)

        cuc = CUPI(default_cuc['host'], default_cuc['username'],
                   default_cuc['password'], port=default_cuc['port'])
        return cuc.get_ldapusers(parameters=params)


ldapusers_post_args = reqparse.RequestParser()
ldapusers_post_args.add_argument('templateAlias', type=str, required=True,
                                 help='User template alias',
                                 default='voicemailusertemplate')
ldapusers_post_args.add_argument('pkid', type=str, required=True,
                                 help='PKID of the user to be imported')
ldapusers_post_args.add_argument('IsVmEnrolled', type=str, required=False,
                                 help='Play initial enrollment conversation (to record a name, request new password, etc)',
                                 choices=['true', 'false'], default = 'true')
ldapusers_post_args.add_argument('ListInDirectory', type=str, required=False,
                                 help='List in the Unity Connection Auto Attendant Directory', 
                                 choices=['true', 'false'], default='true')
ldapusers_post_args.add_argument('Inactive', type=str, required=False,
                                 help='Status of user account', choices=['true', 'false'],
                                 default='false')


@api.route("/import_ldapuser")
class cuc_import_ldapuser_api(Resource):
    @api.expect(ldapusers_post_args, validate=True)
    def post(self, host=default_cuc['host'], port=default_cuc['port'],
             username=default_cuc['username'], password=default_cuc['password']):
        """
        Import LDAP user to Unity Connection.
        """
        args = request.args.to_dict()
        cuc = CUPI(default_cuc['host'], default_cuc['username'],
                   default_cuc['password'], port=default_cuc['port'])
        return cuc.import_ldapuser(parameters={'templateAlias': args['templateAlias']}, payload=args)


update_pin_args = reqparse.RequestParser()
update_pin_args.add_argument('Credentials', type=int, required=True, help='PIN of the voicemail box')
update_pin_args.add_argument('ResetMailbox', type=bool, required=False, help='Reset mailbox', default=True)


@api.route("/update_pin/<pkid>")
@api.param('pkid', 'The pkid of the user object')
class cuc_update_pin_api(Resource):
    @api.expect(update_pin_args, validate=True)
    def put(self, pkid, host=default_cuc['host'], port=default_cuc['port'],
            username=default_cuc['username'], password=default_cuc['password']):
        """
        Update Unity Connection user PIN credential settings using user object ID.
        """
        args = request.args.to_dict()
        payload = {'Credentials': args['Credentials']}
        if args['ResetMailbox']:
            payload['HackCount'] = 0
            payload['TimeHacked'] = []
        cuc = CUPI(default_cuc['host'], default_cuc['username'],
                   default_cuc['password'], port=default_cuc['port'])
        return cuc.update_pin(id=pkid, payload=payload)


user_put_args = reqparse.RequestParser()
user_put_args.add_argument('ListInDirectory', type=str, required=False, 
                           help='List in the Unity Connection Auto Attendant Directory',
                           choices=['true', 'false'], default='true')
user_put_args.add_argument('IsVmEnrolled', type=str, required=False,
                           help='Play initial enrollment conversation (to record a name, request new password, etc)',
                           choices=['true', 'false'], default='true')
user_put_args.add_argument('Inactive', type=str, required=False,
                           help='Status of user account', choices=['true', 'false'],
                           default='false')


@api.route("/user/<pkid>")
@api.param('pkid', 'The pkid of the user object')
class cuc_user_api(Resource):
    def get(self, pkid, host=default_cuc['host'], port=default_cuc['port'],
            username=default_cuc['username'], password=default_cuc['password']):
        """
        Get user from Unity Connection using user object ID.
        """
        cuc = CUPI(default_cuc['host'], default_cuc['username'],
                   default_cuc['password'], port=default_cuc['port'])
        return cuc.get_user(id=pkid)

    @api.expect(user_put_args, validate=True)
    def put(self, pkid, host=default_cuc['host'], port=default_cuc['port'],
            username=default_cuc['username'], password=default_cuc['password']):
        """
        Update user from Unity Connection using user object ID.
        """
        args = request.args.to_dict()
        cuc = CUPI(default_cuc['host'], default_cuc['username'],
                   default_cuc['password'], port=default_cuc['port'])
        return cuc.update_user(id=pkid, payload=args)

    def delete(self, pkid, host=default_cuc['host'], port=default_cuc['port'],
               username=default_cuc['username'], password=default_cuc['password']):
        """
        Delete user from Unity Connection using user object ID.
        """
        cuc = CUPI(default_cuc['host'], default_cuc['username'],
                   default_cuc['password'], port=default_cuc['port'])
        return cuc.delete_user(id=pkid)
