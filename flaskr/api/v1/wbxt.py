
# from flask import jsonify
# from flask import request
# from flask import Blueprint
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
