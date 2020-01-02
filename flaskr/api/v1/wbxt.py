
from flask import request
from flask_restplus import Namespace, Resource, reqparse
from flaskr.wbxt.v1.wbxt import WBXT

api = Namespace('wbxt', description='Webex Teams APIs')


get_rooms_args = reqparse.RequestParser()
get_rooms_args.add_argument('teamId', type=str, required=False, help='List rooms associated with a team, by ID')
get_rooms_args.add_argument('type', type=str, required=False, help='List rooms by type',
                            choices=['direct', 'group'])
get_rooms_args.add_argument('sortBy', type=str, required=False, help='Sort results',
                            choices=['id', 'lastactivity', 'created'])
get_rooms_args.add_argument('max', type=int, required=False,
                            help='Maximum number of rooms in the response', default=100)


@api.route("/rooms")
class wbxt_get_rooms_api(Resource):
    @api.expect(get_rooms_args)    
    def get(self):
        '''
        Retrieves Webex Teams Rooms
        '''
        args = request.args.to_dict()
        wbxt = WBXT()
        return wbxt.get_rooms(parameters=args)


message_post_args = reqparse.RequestParser()
message_post_args.add_argument('teamId', type=str, required=True, help='The room ID of the message')
message_post_args.add_argument('text', type=str, required=False, help='The message, in plain text')
message_post_args.add_argument('markdown', type=str, required=False,
                               help='The message, in Markdown format. The maximum message length is 7439 bytes')


@api.route("/create_message")
class wbxt_create_message_api(Resource):
    @api.expect(message_post_args)
    def post(self):
        '''
        Sends a message to a Webex Teams Rooms using the Room ID.
        '''
        args = request.args.to_dict()
        wbxt = WBXT()
        return wbxt.create_message(payload=args)
