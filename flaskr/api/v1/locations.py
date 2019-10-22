
from flask import jsonify, request
from flask import Blueprint
from flaskr.sql.v1.locations import *
from flaskr.sql.v1.editor import *
from flask_restplus import Namespace, Resource

api = Namespace('locations', description='Locations APIs')



@api.route("/create")
class locations_create_api(Resource):
    def post(self, **kwargs):
        """
        Returns Editor Create
        """

        print('request:\n', request.form)
        data = parse_DT_request(request.form)

        print(data)
        return jsonify(editor_create('locations', data))

@api.route("/edit")
class locations_edit_api(Resource):
    def put(self):
        """
        Returns Editor Create
        """

        print('request:\n', request.form)
        data = parse_DT_request(request.form)

        print(data)
        return jsonify(editor_edit('locations', data))

@api.route("/remove")
class locations_remove_api(Resource):
    def post(self):
        """
        Returns Editor Remove
        """

        print('request:\n', request.form)
        data = parse_DT_request(request.form)

        print(data)
        return jsonify(editor_remove('locations', data))




@api.route("/all_locations")
class call_flows_api(Resource):
    def get(self):
        """
        Returns Call Flows.
        """
        return jsonify(locations_all_locations_sql())

@api.route("/update_schema_locations")
class schema_locations_api(Resource):
    def get(self):
        """
        Updates schema of results table.
        """
        return jsonify(results_update_schema_locations_sql())


@api.route("/<name>/get_locations")
class call_flows_get_api(Resource):
    def get(self, name):
        """
        Returns Call Flows.
        """
        return jsonify(locations_get_location_sql(name))


@api.route("/location_names")
class call_flow_names_api(Resource):
    def get(self):
        """
        Returns location names.
        """
        return jsonify(locations_location_names_sql())

