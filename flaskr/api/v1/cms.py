
from flask import jsonify, request
from flask import Blueprint
from flaskr.sql.v1.cms import *
from flaskr.sql.v1.editor import *
from flask_restplus import Namespace, Resource

api = Namespace('cms', description='Cisco Meeting Server APIs')

@api.route("/create_space")
class cms_create_space_api(Resource):
    def post(self, **kwargs):
        """
        Returns Editor Create
        """

        print('*****')
        print('request:\n', request.form)
        data = parse_DT_request(request.form)

        print(data)
        print('*****')
        return jsonify(editor_create('cms_space', data))

@api.route("/get_spaces")
class cms_get_spaces_api(Resource):
    def get(self):
        """
        Returns Spaces.
        """
        return jsonify(cms_get_spaces_sql())

@api.route("/remove_space")
class cms_remove_space_api(Resource):
    def delete(self):
        """
        Returns Editor Remove
        """

        print('request:\n', request.form)
        data = parse_DT_request(request.form)

        print(data)
        return jsonify(editor_remove('cms_space', data))

@api.route("/edit_space")
class cms_edit_api(Resource):
    def put(self):
        """
        Returns Editor Create
        """

        print('request:\n', request.form)
        data = parse_DT_request(request.form)

        print(data)
        return jsonify(editor_edit('cms_space', data))

