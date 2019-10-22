import json
import re
import gzip

from flask import jsonify, request
from flask import Blueprint
from flaskr.sql.v1.upload import *
from flask_restplus import Namespace, Resource

from flaskr.utils import get_project_root

api = Namespace('process', description='Process Call Flows')


def find_calls(number, filename):

    print('** filename', filename)
    count = 0
    calls = []
    #pattern = re.compile(r"(CC\|OFFERED)\|\S+\|\S+\|\S+(" +number.replace('X', '.') + ")\|(\S+)?\|(\S+)?\|")
    pattern = re.compile(r"(\d+\/\d+\/\d+\s+\d+:\d+:\d+.\d+)\|(CC\|OFFERED)\|.*?(?:\|\S{0,2}(?P<calling>" + number.replace('X', '.') + r"))\|(?P<ocalled>.*?)\|(?P<fcalled>.*?)\|")
    filepath = f'{str(get_project_root())}/flaskr/data/uploads/traces/{filename}'

    for i, line in enumerate(gzip.open(filepath) if filename[-3:] == '.gz' else open(filepath)):

        try:
            str_line = line.decode("utf-8")
        except:
            str_line = line
        for match in re.finditer(pattern, str_line):
            count += 1
            #print('Found on line %s: %s' % (i+1, match.group()))

            calls.append({
                'timestamp': match.group(1),
                'calling': match.group(3),
                'ocalled': match.group(4),
                'fcalled': match.group(5)
            })

    return calls

@api.route("/find_calls/<name>"
            )
class results_find_calls_api(Resource):
    def post(self, name):
        """
        Returns Wave file processing results.
        """

        #print('** number', number)
        #print(name)

        data = request.form.to_dict()

        number = data.get('number', '')

        #print('*** number', number)

        files = upload_all_files_sql(name);

        found_calls = []

        for file in files:

            if 'calllogs_' in file:
                found_calls.extend(find_calls(number, file))
        #print('returning', found_calls)

        return jsonify(found_calls)



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