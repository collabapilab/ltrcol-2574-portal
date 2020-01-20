from flask import request
from flask_restplus import Namespace, Resource
from flaskr.api.v1.config import wbxt_access_token
from flaskr.api.v1.parsers import wbxt_messages_post_args

api = Namespace('wbxt', description='Webex Teams APIs')


@api.route("/send_message")
class wbxt_send_api(Resource):
    @api.expect(wbxt_messages_post_args, Validate=True)
    def post(self):
        '''
        Sends Message to Webex Teams Space (Room) by Room Title
        '''
        pass
