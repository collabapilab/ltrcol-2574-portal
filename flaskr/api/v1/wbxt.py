import logging
import json
from flask import request
from flask_restx import Namespace, Resource
from flaskr.api.v1.parsers import wbxt_messages_post_args
from flaskr.api.v1.cucm import cucm_get_version_api, cucm_perfmon_api
from flaskr.api.v1.core import core_users_api
from os import getenv
from wxc_sdk import WebexSimpleApi
from wxc_sdk.webhook import WebhookEvent, WebhookResource, WebhookEventType

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(threadName)s %(levelname)s %(name)s %(message)s')
logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)
# Change to DEBUG for detailed REST interaction output
logging.getLogger('wxc_sdk.rest').setLevel(logging.INFO)

log = logging.getLogger(__name__)

api = Namespace('wbxt', description='Webex APIs')

# Create the Webex wxc_sdk API connection object for the Bot
wbx_bot_api = WebexSimpleApi(tokens=getenv('WBX_BOT_ACCESS_TOKEN'))

# Get the details for the Bot account whose access token we are using
bot = wbx_bot_api.people.me()

# Read an adaptive card JSON from a file
with open('flaskr/api/v1/adaptive_card.json') as json_file:
    adaptive_card_content = json.load(json_file)

# Read environment variables
webhook_name = getenv('WBX_WEBHOOK_NAME')
webhook_url = getenv('WBX_WEBHOOK_URL')


def delete_webhooks_by_name():
    """
    Retrieve all webhooks that are owned by the Bot, then delete the ones matching our webhook name.
    """
    for webhook in wbx_bot_api.webhook.list():
        if webhook.name == webhook_name:
            wbx_bot_api.webhook.webhook_delete(webhook_id=webhook.webhook_id)
            log.info(f'Webhook "{webhook.name}" for "{webhook.resource}" deleted. Callback URL="{webhook.target_url}"')


def create_webhooks():
    """
    Create the Webex webhooks using the Bot: one for messages, another one for the adaptive card
    """
    for resource_type in ['messages', 'attachmentActions']:
        webhook = wbx_bot_api.webhook.create(
            resource=WebhookResource(resource_type),
            event=WebhookEventType.created,
            name=webhook_name,
            target_url=webhook_url
        )
        log.info(f'Webhook "{webhook_name}" for "{webhook.resource}" created. Callback URL="{webhook_url}".')


# Delete and recreate all webhooks with a given name every time the flask app is restarted
delete_webhooks_by_name()
create_webhooks()


@api.route('/send_message')
class wbxt_send_api(Resource):
    """
    Notification actions. Used for sending notifications/updates via the Bot
    """
    @api.expect(wbxt_messages_post_args, Validate=True)
    def post(self):
        """
        Sends Message to a Webex Space (Room) by Room Title
        """
        args = wbxt_messages_post_args.parse_args(request)
        # Populate the text key if not specified
        if 'text' not in args:
            args['text'] = ''

        # Get the Rooms list (only group type, not direct)
        rooms = list(wbx_bot_api.rooms.list(type='group'))

        # Search through the Rooms to match the room title
        for room in rooms:
            if args['room_name'].strip() == room.title.strip():
                # Found the room, send a message
                message = wbx_bot_api.messages.create(room_id=room.id, markdown=args['text'])
                return {'success': True,
                        'message': f'Successfully sent message {message.id}',
                        'response': ''}

        # Room was not found
        return {'success': False,
                'message': f'Could not find Room "{args["room_name"]}"',
                'response': ''}


@api.route('/events', doc=False)
class wbxt_events_api(Resource):
    def send_card(self, room_id: str):
        """
        Post the adaptive card to the specified room.
        """
        wbx_bot_api.messages.create(
            room_id=room_id,
            text='Your Webex client cannot display this card',
            attachments=[{
                'contentType': 'application/vnd.microsoft.card.adaptive',
                'content': adaptive_card_content
            }]
        )


    def respond_to_message(self, wh_event: WebhookEvent):
        """
        Respond to a message to the bot. Retrieve the Room, message, and sender information from the webhook payload and
        the corresponding message id
        """

        # Read the Webhook event Data
        wh_data = wh_event.data

        # Get the room to which this active card submission was posted to from the webhook data
        room = wbx_bot_api.rooms.details(room_id=wh_data.room_id)

        # Look up the message from the data in the webhook
        message = wbx_bot_api.messages.details(message_id=wh_data.id)

        # Look up the sender of this message
        sender = wbx_bot_api.people.details(person_id=message.person_id)

        # ONLY reply if the message is from someone in the same Webex org AND the message is not from the Bot itself
        if (bot.org_id == sender.org_id) and (message.person_id != bot.person_id):
            log.info(f'Message received from {sender.display_name}:\n{message.text}')

            # Send a message in reply to the same room
            wbx_bot_api.messages.create(room_id=room.id, text='Your available options are:')

            # Send the contact card to the room which originated the active card submission
            self.send_card(room_id=room.id)


    def respond_to_button_press(self, wh_event: WebhookEvent):
        """
        Respond to an adaptive card submission
        """

        # Read the Webhook event Data
        wh_data = wh_event.data

        # Get the room to which this message was posted to from the webhook data
        room = wbx_bot_api.rooms.details(room_id=wh_data.room_id)

        # Look up the attachment from the data in the webhook
        attachment_action = wbx_bot_api.attachment_actions.details(action_id=wh_data.id)
        # Look up the sender of the submission/attachment
        sender = wbx_bot_api.people.details(person_id=attachment_action.person_id)

        # Only reply if the submission was from someone in the same Webex org as the Bot
        if bot.org_id == sender.org_id:

            log.info(f'attachmentAction received from {sender.display_name}:\n'
                     f'{attachment_action.inputs}')
            try:
                # Evaluate the contents of the submission and take action on them
                if attachment_action.inputs['action'] == 'get_ucm_version':
                    # Retrieve the CUCM version from the API created previously
                    log.info('Creating response for get_ucm_version')
                    cucm_version_data = cucm_get_version_api.get(Resource).json
                    if cucm_version_data['success']:
                        wbx_bot_api.messages.create(
                            room.id,
                            markdown=f'The Unified CM version is **{cucm_version_data["version"]}**'
                        )
                    else:
                        wbx_bot_api.messages.create(
                            room_id=room.id,
                            markdown=f'Failed to retrieve The Unified CM version\n \
                                       Error Message:\n \
                                       ```{cucm_version_data["message"]}```'
                        )

                # Take action on the 'get_ucm_reg_phones' action
                elif attachment_action.inputs['action'] == 'get_ucm_reg_phones':
                    # Retrieve the CUCM registered phones, in this case, we'll add up the RegisteredHardwarePhones and
                    # RegisteredOtherStationDevices perfmon counters
                    log.info('Creating response for get_ucm_reg_phones')
                    perfmon_counters = [
                        'Cisco CallManager\RegisteredOtherStationDevices',
                        'Cisco CallManager\RegisteredHardwarePhones'
                    ]
                    cucm_perfmon_data = cucm_perfmon_api.post(Resource, perfmon_counters=perfmon_counters).json

                    if cucm_perfmon_data['success']:
                        num_reg_devices = sum(item['Value'] for item in cucm_perfmon_data['perfmon_counters_result'])
                        wbx_bot_api.messages.create(
                            room_id=room.id,
                            markdown=f'The number of registered devices is **{num_reg_devices}**'
                        )
                    else:
                        wbx_bot_api.messages.create(
                            room_id=room.id,
                            markdown=f'Failed to retrieve the number of registered devices\n \
                                       Error Message:\n \
                                       ```{cucm_perfmon_data["message"]}```'
                        )

                # Take action on the 'user_search' action
                elif attachment_action.inputs['action'] == 'user_search':
                    # Call the core user search, this will search both CUCM and Webex Calling
                    log.info(f'User Search for: {attachment_action.inputs["user"]}')
                    user_data = core_users_api.get(Resource, userid=attachment_action.inputs['user']).json

                    if user_data['success']:
                        wbx_bot_api.messages.create(
                            room.id,
                            text=f'User {attachment_action.inputs["user"]} is configured in {user_data["phonesystem"]}'
                        )
                        # Output full user data if Details checkbox selected
                        if attachment_action.inputs['user_details'].lower() == 'true':
                            if 'wbxc_user_data' in user_data:
                                wbx_bot_api.messages.create(
                                    room_id=room.id,
                                    markdown=f'Webex Calling user details:\n'
                                             f'```\n{json.dumps(user_data["wbxc_user_data"], indent=4)}\n```'
                                )

                            if 'cucm_user_data' in user_data:
                                wbx_bot_api.messages.create(
                                    room_id=room.id,
                                    markdown=f'Unified CM user details:\n'
                                             f'```\n{json.dumps(user_data["cucm_user_data"], indent=4)}\n```'
                                )
                    else:
                        wbx_bot_api.messages.create(
                            room_id=room.id,
                            text=f'User {attachment_action.inputs["user"]} lookup failed: {user_data["message"]}'
                        )

            # Any error in looking up a value will simply be ignored.
            except KeyError:
                pass

            # Post the adaptive card again, since quite a bit of data may have been returned
            self.send_card(room_id=room.id)


    # Receive a Webex Webhook POST
    def post(self):
        """
        Receives a Webex Webhook POST. Evaluates the event, in all cases, on will only process 'created' events, but
        depending on the resource type (messages or attachmentActions), will respond accordingly
        """

        try:
            # Log inbound POST data
            log.debug(f'Received inbound POST with data:\n' + json.dumps(request.json, indent=4))

            # Parse the incoming Webhook request as a WebhookEvent
            webhook_event = WebhookEvent.parse_obj(request.json)

            # Handle a new message event
            if webhook_event.resource == 'messages':
                self.respond_to_message(webhook_event)

            # Handle an active card submission event
            elif webhook_event.resource == 'attachmentActions':
                self.respond_to_button_press(webhook_event)

        except Exception as e:
            log.error(f'Failed to parse: {e}')

        return 'Ok'
