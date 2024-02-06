"""
Sample Oauth authentication flow using Integration

1. Log into https://developer.webex.com
2. Click the picture at the top right corner, then choose "My Webex Apps"
3. Create an Integration with the following mandatory parameters:
   - An integration name
   - An icon
   - An app description
   - The Redirect URI set to "http://localhost:5002/redirect"
   - The following scope checked: "spark:people_read"
4. Copy the Client ID and Client Secret from the Integration page into the variables below
5. Start this program
6. In another browser tab, paste the "OAuth Authorization URL" from the Integration page.
7. This program will receive the redirect of your browser's authorization request, reads the authorization code,
    retrieves an access code and finally uses the access code to show the user who performed the Oauth authentication
"""
import http.server
import json
import logging
import re
import requests
import socketserver
from wxc_sdk import WebexSimpleApi

# Replace with your values from the Integration
client_id = '___PASTE_SERVICE_APP_CLIENT_ID___'
client_secret = '___PASTE_SERVICE_APP_CLIENT_SECRET___'

redirect_url = "http://localhost:5002/redirect"
scopes = 'spark:kms spark:people_read'

server_port = 5002
# If specified, this code will be used to retrieve an authentication token instead of starting the web server to
# handle the authorization redirect and collecting it from there.
authorization_code = None

# Set up logging with a default level of INFO
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
# The logging levels for individual components can be adjusted
# logging.getLogger('wxc_sdk.rest').setLevel(logging.DEBUG)
# Create a logging instance
log = logging.getLogger(__name__)


def get_access_token(code):
    """
    Retrieves an access token given an authorization code
    """
    log.info(f'Requesting authentication token for authorization code: {code}')
    token = None
    # Gets access token and refresh token
    headers = {'accept': 'application/json', 'content-type': 'application/x-www-form-urlencoded'}
    payload = f"grant_type=authorization_code&client_id={client_id}&client_secret={client_secret}&code={code}" \
              f"&redirect_uri={redirect_url}"
    req = requests.post(url='https://webexapis.com/v1/access_token', data=payload, headers=headers)
    results = json.loads(req.text)
    log.info(json.dumps(results, indent=4))  # Prettier way of printing the response data
    if req.status_code == 200:
        token = results["access_token"]
    return token


class Server(socketserver.TCPServer):

    # Avoid "address already used" error when frequently restarting the script
    allow_reuse_address = True


# If the authorization code was manually specified, no need to start up the web server to wait for the redirect
if authorization_code is None:
    class RedirectHandler(http.server.BaseHTTPRequestHandler):
        """
        Handle incoming server request to the redirect url
        """

        def do_GET(self):
            """
            Parses an incoming request and sets the authorization code, if found
            """

            global authorization_code

            self.send_response(200, "OK")
            self.end_headers()
            self.wfile.write(f"Got the redirect: {self.requestline}".encode("utf-8"))
            authorization_code = re.search('^.*code=([^&$]+)', self.requestline).group(1)


    logging.info(f'Starting web server on port {server_port}')
    # Start up a simple web server that will terminate when an authorization code received
    with Server(("", server_port), RedirectHandler) as httpd:
        while not authorization_code:
            httpd.handle_request()

# Retrieve an access code given the authorization code
access_token = get_access_token(authorization_code)

if access_token:
    api = WebexSimpleApi(tokens=access_token)
    try:
        me = api.people.me()
        log.info(f'Authenticated to Webex as {me.emails[0]}')
    except Exception as e:
        log.info(f'Exception encountered: {e}')
else:
    log.error(f'No access token available')
