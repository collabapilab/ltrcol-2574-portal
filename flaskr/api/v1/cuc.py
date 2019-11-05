from flask import jsonify
from flask import request
from flask import Blueprint
from flask_restplus import Namespace, Resource
from flaskr.cuc.v1.cuc import *

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
    def get(self, op=None, val=None, host=default_cuc['host'], port=default_cuc['port'], username=default_cuc['username'], password=default_cuc['password']):
        """
        Returns CUC user
        """
        base_url = '/vmrest/users'

        # query = (column[is | startswith] value)
        base_url = '/vmrest/users?query=(alias%20is%20operator)'
        result = cuc_send_request(host=host, username=username, password=password, port=port, location=base_url)

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
