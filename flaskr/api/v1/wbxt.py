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
    pass

def create_webhooks():
    """
    Create the Webex webhooks using the Bot: one for messages, another one for the adaptive card
    """
    pass


# Delete and recreate all webhooks with a given name every time the flask app is restarted


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


@api.route('/events', doc=False)
class wbxt_events_api(Resource):
    def send_card(self, room_id: str):
        """
        Post the adaptive card to the specified room.
        """
        pass


    def respond_to_message(self, wh_event: WebhookEvent):
        """
        Respond to a message to the bot. Retrieve the Room, message, and sender information from the webhook payload and
        the corresponding message id
        """

        # Read the Webhook event Data
        pass


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

                # Take action on the 'get_ucm_reg_phones' action
                elif attachment_action.inputs['action'] == 'get_ucm_reg_phones':
                    # Retrieve the CUCM registered phones, in this case, we'll add up the RegisteredHardwarePhones and
                    # RegisteredOtherStationDevices perfmon counters
                    log.info('Creating response for get_ucm_reg_phones')

                # Take action on the 'user_search' action
                elif attachment_action.inputs['action'] == 'user_search':
                    # Call the core user search, this will search both CUCM and Webex Calling
                    log.info(f'User Search for: {attachment_action.inputs["user"]}')

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

        except Exception as e:
            log.error(f'Failed to parse: {e}')

        return 'Ok'
