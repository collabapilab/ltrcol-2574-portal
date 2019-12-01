
from flask import jsonify, request
from flask import Blueprint
from flask_restplus import Namespace, Resource
from flaskr.wbxt.v1.wbxt import WBXT

api = Namespace('wbxt', description='Webex Teams APIs')

@api.route("/rooms")
class wbxt_get_rooms_api(Resource):
    def get(self):
        wbxt = WBXT()
        return wbxt.get_rooms()

@api.route("/create_message")
class wbxt_create_message_api(Resource):
    def post(self):
        wbxt = WBXT()
        return wbxt.create_message(payload=self.api.payload)

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
