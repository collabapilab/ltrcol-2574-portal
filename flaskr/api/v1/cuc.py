
from flask import jsonify, request
from flask import Blueprint
from flask_restplus import Namespace, Resource
from flaskr.cuc.v1 import *

api = Namespace('cuc', description='Cisco Unity Connection APIs')

@api.route("/get_version")
class cuc_get_version_api(Resource):
    def get(self):
        """
        Returns CUC Version
        """

        return jsonify(status['status']['softwareVersion'])

@api.route("/create_mailbox")
class cuc_create_mailbox_api(Resource):
    def post(self, **kwargs):
        """
        Returns CUC Mailbox
        """
            
        return jsonify(editor_create('cms_spaces', data))

@api.route("/list_mailboxes")
class cuc_get_mailboxes_api(Resource):
    def get(self):
        """
        Lists CUC mailboxes
        """
        return jsonify(cms_get_spaces_sql())

@api.route("/find_mailbox")
class cuc_get_mailboxes_api(Resource):
    def get(self):
        """
        Gets CUC mailbox
        """
        return jsonify(cms_get_spaces_sql())

@api.route("/delete_mailbox")
class cuc_delete_mailbox_api(Resource):
    def delete(self):
        """
        Deletes CUC mailbox
        """

        pass

@api.route("/edit_mailbox")
class cms_edit_api(Resource):
    def put(self):
        """
        Modifies a CUC mailbox
        """
        pass

