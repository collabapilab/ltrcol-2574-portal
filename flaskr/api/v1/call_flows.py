
from flask import jsonify, request
from flask import Blueprint
from flaskr.sql.v1.call_flows import *
from flaskr.sql.v1.editor import *
from flask_restplus import Namespace, Resource

api = Namespace('call_flows', description='Call Flows APIs')



@api.route("/create")
class call_flow_create_api(Resource):
    def post(self, **kwargs):
        """
        Returns Editor Create
        """

        print('request:\n', request.form)
        data = parse_DT_request(request.form)

        print(data)
        return jsonify(editor_create('call_flows', data))

@api.route("/edit")
class call_flow_edit_api(Resource):
    def put(self):
        """
        Returns Editor Create
        """

        print('request:\n', request.form)
        data = parse_DT_request(request.form)

        print(data)
        return jsonify(editor_edit('call_flows', data))

@api.route("/remove")
class call_flows_remove_api(Resource):
    def post(self):
        """
        Returns Editor Remove
        """

        print('request:\n', request.form)
        data = parse_DT_request(request.form)

        print(data)
        return jsonify(editor_remove('call_flows', data))




@api.route("/all_call_flows")
class call_flows_api(Resource):
    def get(self):
        """
        Returns Call Flows.
        """
        return jsonify(call_flows_all_call_flows_sql())

@api.route("/<name>/get_call_flows")
class call_flows_get_api(Resource):
    def get(self, name):
        """
        Returns Call Flows.
        """
        return jsonify(call_flows_get_call_flows_sql(name))


@api.route("/call_flow_names")
class call_flow_names_api(Resource):
    def get(self):
        """
        Returns Call Flow names.
        """
        return jsonify(call_flows_call_flow_names_sql())

