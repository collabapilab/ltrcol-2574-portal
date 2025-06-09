"""
Sample authentication/refresh flow using Webex Service App

1. Log into https://developer.webex.com
2. Click the picture at the top right corner, then choose "My Webex Apps"
3. Create an Service App with the following mandatory parameters:
   - An App name
   - An icon
   - An app description
   - A contact email
   - Any needed scopes
4. Copy the Client ID and Client Secret from the Service App page into the variables below
5. Have the Service App authorized by a Full Administrator (in Control Hub under Management > Apps > Service Apps tab
6. Return to the Service App page, under Org Authorizations, select the org the app was authorized in
7. Paste the Client Secret from earlier and click Generate Tokens
8. Copy the refresh_token to the variable below
9. Run this python script. A new access token will be generated and access verified
"""
import json
import logging
import requests
from wxc_sdk import WebexSimpleApi

# Replace with your Service App's parameters
client_id = '___REPLACE_WITH_SERVICE_APP_CLIENT_ID___'
client_secret = "___REPLACE_WITH_SERVICE_APP_CLIENT_SECRET___"
refresh_token = "___REPLACE_WITH_SERVICE_APP_REFRESH_TOKEN___"

# Set up logging with a default level of INFO
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
# The logging levels for individual components can be adjusted
# logging.getLogger('wxc_sdk.rest').setLevel(logging.DEBUG)
# Create a logging instance
log = logging.getLogger(__name__)


log.info(f'Requesting access token with refresh token')
headers = {
    'accept': 'application/json',
    'content-type': 'application/x-www-form-urlencoded'
}

# Request a new access token and refresh token

results = json.loads(response.text)
log.info(f'Response:\n{json.dumps(results, indent=4)}')  # Prettier way of printing the response data
if response.status_code == 200:
    log.info(f'Your new Service App access token is:\n\n{results["access_token"]}\n')

    # Attempt to get a user list using the new access token
    api = WebexSimpleApi(tokens=results["access_token"])
    try:
        users = list(api.people.list())
        log.info(f'Logged into Webex as a Service App and found {len(users)} users')
    except Exception as e:
        log.info(f'Exception encountered: {e}')
else:
    log.error(f'Unexpected response status code: {response.status_code}')
