
"""
Sample Oauth authentication flow using Integration to create a Webex Meeting
"""
import requests
import os
import logging
from datetime import datetime, timezone, timedelta
from flask import Flask, redirect, request, session, url_for
from urllib.parse import quote
from wxc_sdk import WebexSimpleApi

# Flask app setup
app = Flask(__name__)
app.secret_key = os.urandom(32)  # Secure session data

# Webex OAuth Configuration (Replace with your credentials)
client_id = "___PASTE_INTEGRATION_CLIENT_ID___"
client_secret = "___PASTE_INTEGRATION_CLIENT_SECRET___"
redirect_url = "___PASTE_WEBEX_REDIRECT_URI___"
scopes = quote("___PASTE_WEBEX_SCOPE_FOR_INTEGRATION___")

# Set up logging with a default level of INFO
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
# The logging levels for individual components can be adjusted
logging.getLogger('wxc_sdk.rest').setLevel(logging.DEBUG)
# Create a logging instance
log = logging.getLogger(__name__)


@app.route("/")
def home():
    """
    Homepage presenting Login or Create Meeting button, depending on whether
    an access token was found for this session.
    """
    if "access_token" in session:
        access_token = session["access_token"]
        try:
            # Fetch user details using WebexSimpleApi
            api = WebexSimpleApi(tokens=access_token)
            user = api.people.me()  # Fetch authenticated user's details
            user_name = user.display_name  # Extract display name

            return f"""
            <h2>Welcome, {user_name}!</h2>
            <p><strong>Access Token:</strong> <code>{access_token}</code></p>
            <a href='/create_meeting'><button>Create Meeting</button></a>
            """
        except Exception as e:
            return f"<h2>Error fetching user details</h2><p>{str(e)}</p><a href='/login'><button>Login Again</button></a>"

    return """
    <h2>Webex OAuth Authentication</h2>
    <a href='/login'><button>Login with Webex</button></a>
    """

@app.route("/login")
def login():
    """
    Step 1: Redirect user to Webex OAuth authorization page to log in.
    """
    return ("***** Authorization redirect not yet implemented!")

@app.route("/redirect")
def oauth_redirect():
    """
    Step 2: After authorization, Webex redirects here with an authorization code.
    - The app exchanges the code for an access token.
    - The access token is used to fetch the authenticated user's details.
    - Redirects back to the login page once completed successfully.
    """
    error = request.args.get("error")
    if error:
        return f"Error: {error}"

    code = request.args.get("code")
    if not code:
        return "Authorization code not received."

    # Exchange authorization code for access token
    log.info(f'***** Requesting access token for authorization code : {code}')
    return ("***** Access token request not yet implemented!")

@app.route("/create_meeting")
def create_meeting():
    """
    Step 3: Create a Webex meeting using obtained access token.
    """
    if "access_token" not in session:
        return redirect(url_for("home"))  # Redirect to login if not authenticated

    # Retrieve the access token from the session and create an instance of the WebexSimpleApi
    access_token = session["access_token"]
    api = WebexSimpleApi(tokens=access_token)

    # Create variables for start and end times and meeting title

    try:
        log.info("Creating a meeting")
        # Create Meeting using the create meeting API

        # Generate the join links for the meeting
    
    except Exception as e:
        log.error(f"Error creating meeting: {e}")
        return f"<h2>Error Creating Meeting</h2><p>{str(e)}</p><a href='/'><button>Go Back</button></a>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
