
from flask import request
from flask_restplus import Namespace, Resource, reqparse
from flaskr.wbxt.v1.wbxt import WBXT
from flaskr.api.v1.parsers import wbxt_rooms_get_args, wbxt_messages_post_args

api = Namespace('wbxt', description='Webex Teams APIs')


@api.route("/rooms")
class wbxt_get_rooms_api(Resource):
    @api.expect(wbxt_rooms_get_args, Validate=True)
    def get(self):
        '''
        Retrieves Webex Teams Rooms
        '''
        args = request.args.to_dict()
        wbxt = WBXT()
        return wbxt.get_rooms(parameters=args)


@api.route("/messages")
class wbxt_create_message_api(Resource):
    @api.expect(wbxt_messages_post_args, Validate=True)
    def post(self):
        '''
        Sends a message to a Webex Teams Rooms using the Room ID.
        '''
        args = request.args.to_dict()
        wbxt = WBXT()
        return wbxt.create_message(payload=args)
