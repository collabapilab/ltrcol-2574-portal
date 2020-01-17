from flask import request
from flask_restplus import Namespace, Resource
from flaskr.api.v1.config import wbxt_access_token
from flaskr.api.v1.parsers import wbxt_messages_post_args
from webexteamssdk import WebexTeamsAPI, ApiError

api = Namespace('wbxt', description='Webex Teams APIs')


@api.route("/send_message")
class wbxt_send_api(Resource):
    @api.expect(wbxt_messages_post_args, Validate=True)
    def post(self):
        '''
        Sends Message to Webex Teams Room by Room title
        '''
        args = request.args.to_dict()
        # Populate the text key if not specified
        if 'text' not in args:
            args['text'] = ''

        # Initialize the webex teams API with our token
        api = WebexTeamsAPI(access_token=wbxt_access_token)

        try:
            # Get the Rooms list (only group type, not direct)
            rooms = api.rooms.list(type='group')

            # Search through the Rooms to match the room title
            for room in rooms:
                if args['room_name'].strip() == room.title.strip():
                    # Found the room, send a message
                    api.messages.create(roomId=room.id, text=args['text'])
                    return {'success': True, 
                            'messages': 'Successfully sent message', 
                            'response': ''}
            # Room was not found
            return {'success': False, 
                    'messages': 'Could not find Room "{}"'.format(args['room_name']),
                    'response': ''}

        # Return any API error that may have been raised
        except ApiError as e:
            return {'success': False,
                    'messages': 'ApiError encountered',
                    'response': '{}'.format(e)}
