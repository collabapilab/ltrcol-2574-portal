from flask import jsonify
from flask import request
from flask import Blueprint
from flask_restplus import Namespace, Resource, reqparse
from flaskr.cuc.v1.cupi import CUPI
# import flask
# from flaskr.rest.v1.rest import *

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
        Returns list of Unity Connection users (with and without voicemail mailboxes).
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
ldapusers_post_args.add_argument('payload', type=str, required=True, location='json', 
                                 help='Desired user object settings in JSON format. The pkid value is \
                                      <strong>required</strong>. Example:\n<pre>\
{\n\
    "pkid": "dbc37047-7565-6b29-3327-18850f64d406"\n\
}\
                                      </pre>')

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
        # return cuc.import_ldapuser(parameters=args, payload=request.json)
        return cuc.import_ldapuser(parameters=args, payload=self.api.payload)


update_pin_args = reqparse.RequestParser()
update_pin_args.add_argument('payload', type=str, required=True, location='json',
                                 help='User PIN settings in JSON format. Sample payload:\n<pre>\
{\n\
  "Credentials": "14235834",\n\
  "HackCount": 0,\n\
  "TimeHacked": []\n\
}\
</pre>')


@api.route("/update_pin/<pkid>")
class cuc_update_pin_api(Resource):
    @api.expect(update_pin_args, validate=True)
    def put(self, pkid, host=default_cuc['host'], port=default_cuc['port'],
            username=default_cuc['username'], password=default_cuc['password']):
        """
        Update Unity Connection user PIN credential settings using user object ID.
        """
        cuc = CUPI(default_cuc['host'], default_cuc['username'],
                   default_cuc['password'], port=default_cuc['port'])
        return cuc.update_pin(id=pkid, payload=self.api.payload)


user_put_args = reqparse.RequestParser()
user_put_args.add_argument('payload', type=str, required=True, location='json',
                                 help='Desired user object settings in JSON format. Sample payload:\n<pre>\
{\n\
    "DisplayName": "Modified User Display Name",\n\
    "ListInDirectory": "false"\n\
}\
                                      </pre>')


@api.route("/user/<pkid>")
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
        cuc = CUPI(default_cuc['host'], default_cuc['username'],
                   default_cuc['password'], port=default_cuc['port'])
        return cuc.update_user(id=pkid, payload=self.api.payload)

    def delete(self, pkid, host=default_cuc['host'], port=default_cuc['port'],
               username=default_cuc['username'], password=default_cuc['password']):
        """
        Delete user from Unity Connection.
        """
        cuc = CUPI(default_cuc['host'], default_cuc['username'],
                   default_cuc['password'], port=default_cuc['port'])
        return cuc.delete_user(id=pkid)
