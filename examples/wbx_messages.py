"""
Sample python script demonstrating Webex messaging using wxc_sdk
"""
import logging
from wxc_sdk import WebexSimpleApi

# Set up logging with a default level of INFO
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
# The logging levels for individual components can be adjusted
logging.getLogger('wxc_sdk.rest').setLevel(logging.DEBUG)
# Create a logging instance
log = logging.getLogger(__name__)

# Replace with your Bot's access token
wbx_bot_access_token = '___PASTE_YOUR_BOT_ACCESS_TOKEN_HERE___'

# Create an instance of the WebexSimpleApi with your Bot
api = WebexSimpleApi(tokens=wbx_bot_access_token)

# Get the Bot's Rooms list (only group type, not direct)
rooms = list(api.rooms.list(type='group'))

# Search through rooms
for room in rooms:
    log.info(room.json(indent=4))

# Send a message to this Room
msg = api.messages.create(room_id=room.id, text='Hello!')
log.info(f'Message sent:\n{msg.json(indent=4)}')
