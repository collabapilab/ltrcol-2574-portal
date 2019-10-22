import json

from flask import jsonify, request
from flask import Blueprint
from flaskr.sql.v1.results import *
from flaskr.sql.v1.editor import *
from flask_restplus import Namespace, Resource

api = Namespace('results', description='Call Flows APIs')




@api.route("/all_results",
            "/<name>/all_results"
            )
class results_api(Resource):
    def get(self, name=''):
        """
        Returns Wave file processing results.
        """
        return jsonify(results_all_results_sql(name))

@api.route("/save_results",
            "/save_results/<data>"
            )
class results_save_api(Resource):
    def post(self):
        """
        Returns Wave file processing results.
        """

        data = request.form.to_dict()

        try:
            data = json.loads(data['data'])
        except Exception as e:
            data = []

        return jsonify(results_save_results_sql(data))

@api.route("/update_schema_results")
class results_api(Resource):
    def get(self):
        """
        Updates schema of results table.
        """
        return jsonify(results_update_schema_results_sql())

@api.route("/remove")
class results_remove_api(Resource):
    def post(self):
        """
        Returns Editor Remove
        """

        print('request:\n', request.form)
        data = parse_DT_request(request.form)

        print(data)
        return jsonify(editor_remove('results', data))