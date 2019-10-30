
from flask import jsonify, request
from flask import Blueprint
from flask_restplus import Namespace, Resource
from flaskr.cucm.v1 import *

api = Namespace('cucm', description='Cisco Unified Communications Manager APIs')

@api.route("/get_version")
class cms_get_version_api(Resource):
    def get(self):
        """
        Returns Editor
        """
        # print('request:\n', request.form)
        # data = parse_DT_request(request.form)

        # print(data)
        status = get_cms_system_status(ip='10.0.131.43')

        return jsonify(status['status']['softwareVersion'])

@api.route("/create_space")
class cms_create_space_api(Resource):
    def post(self, **kwargs):
        """
        Returns Editor Create
        """
        print('request:\n', request.form)
        data = parse_DT_request(request.form)
        print(data)
            
        return jsonify(editor_create('cms_spaces', data))

@api.route("/get_spaces")
class cms_get_spaces_api(Resource):
    def get(self):
        """
        Returns Spaces.
        """
        return jsonify(cms_get_spaces_sql())

@api.route("/remove_space")
class cms_remove_space_api(Resource):
    def post(self):
        """
        Returns Editor Remove
        """

        print('request:\n', request.form)
        data = parse_DT_request(request.form)

        print(data)
        return jsonify(editor_remove('cms_spaces', data))

@api.route("/edit_space")
class cms_edit_api(Resource):
    def put(self):
        """
        Returns Editor Create
        """

        print('request:\n', request.form)
        data = parse_DT_request(request.form)

        print(data)
        return jsonify(editor_edit('cms_spaces', data))

