from flask import jsonify
from flask import request
from flask import Blueprint
from flask_restplus import Namespace, Resource
from flaskr.cuc.v1.cuc import *
import flask

api = Namespace('cuc', description='Cisco Unity Connection APIs')

# @api.route("/version")
# class cuc_get_version_api(Resource):
#     def get(self):
#         """
#         Returns CUC Version
#         """

#         return jsonify(status['status']['softwareVersion'])

@api.route("/users")
class cuc_get_user_api(Resource):
    def get(self, op=None, val=None, host=default_cuc['host'], port=default_cuc['port'], 
            username=default_cuc['username'], password=default_cuc['password']):
        """
        Searches for CUC users.  

        YOu can filter using following query parameters (start with ? then add & for each additional element pair):
            filter=text_to_filter (default = '')
            column=column_to_search (default = 'alias'; sometimes dtmfaccessid is useful)
            match=matchtype  (default = 'startswith', also supports 'is'; how to perform the search on the filtered text)
            sortorder=order (default = 'asc', also supports 'desc'); how to sort the results
            
        For example:

          ?filter=operator  - would find all users whose alias that start with operator (operator, operator1, etc)
          ?filter=operator&match=is  - would find a user whose alias  is exactly 'operator'
          ?filter=99999&column=dtmfaccessid&match=is  - would find the user with dtmfaccessid = 99999

        If filter is not specified (or blank), then all other parameters are ignored and all users are returned.
        
        """
        base_url = '/vmrest/users'
        args = flask.request.args.to_dict()

        # query = (column[is | startswith] value)
        # args: -> ?query=alias&is=operator;  ?filter=operator&match=exact  query=(alias%20is%20operator)
        # ?query=(dtmfaccessid%20startswith%2099999) <--> ?filter=2099999&match=exact
        # base_url = '/vmrest/users?query=(alias%20is%20operator)'

        base_url = '/vmrest/users'
        result = cuc_send_request(host=host, username=username,
                                  password=password, port=port, base_url=base_url, parameters=args)

        return result


# @api.route("/create_mailbox")
# class cuc_create_mailbox_api(Resource):
#     def post(self, **kwargs):
#         """
#         Returns CUC Mailbox
#         """
         
#         return jsonify(editor_create('cms_spaces', data))

# @api.route("/list_mailboxes")
# class cuc_get_mailboxes_api(Resource):
#     def get(self):
#         """
#         Lists CUC mailboxes
#         """
#         return jsonify(cms_get_spaces_sql())

# @api.route("/find_mailbox")
# class cuc_get_mailboxes_api(Resource):
#     def get(self):
#         """
#         Gets CUC mailbox
#         """
#         return jsonify(cms_get_spaces_sql())

# @api.route("/delete_mailbox")
# class cuc_delete_mailbox_api(Resource):
#     def delete(self):
#         """
#         Deletes CUC mailbox
#         """

#         pass

# @api.route("/edit_mailbox")
# class cms_edit_api(Resource):
#     def put(self):
#         """
#         Modifies a CUC mailbox
#         """
#         pass
