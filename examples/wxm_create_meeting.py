
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
import logging


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
    auth_redirect_url =  "https://webexapis.com/v1/authorize" + \
        f"?client_id={client_id}" + \
        "&response_type=code" + \
        f"&redirect_uri={redirect_url}" + \
        f"&scope={scopes}" + \
        "&state=random_state_string"

    log.info(f'Redirecting login request to: {auth_redirect_url}')
    return redirect(auth_redirect_url)

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
    response = requests.post(
        "https://webexapis.com/v1/access_token",
        data={
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": redirect_url
        }
    )

    # Retrieve access token from response and store it in the session
    token_data = response.json()

    if "access_token" in token_data:
        access_token = token_data["access_token"]
        log.info(f'Received access token: {access_token}')
        session["access_token"] = access_token  # Store token in session
        return redirect(url_for("home"))  # Redirect to login/home
    else:
        return f"Error retrieving access token: {token_data}"

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
    start_time = datetime.now(timezone.utc).replace(microsecond=0) + timedelta(minutes=5)
    end_time = start_time + timedelta(minutes=30)
    meeting_title = "Lab Test Meeting"

    try:
        log.info("Creating a meeting")
        # Create Meeting using the create meeting API
        meeting_response = api.meetings.create(title=meeting_title, start=start_time, end=end_time)
        log.info(meeting_response.model_dump_json(indent=4))
        log.info(f'Meeting ID: {meeting_response.id}')
        log.info(f'Meeting Number: {meeting_response.meeting_number}')
        log.info(f'Meeting Link: {meeting_response.web_link}')

        # Generate the join links for the meeting
        join_response = api.meetings.join(meeting_id=meeting_response.id, join_directly=False)
        log.info(join_response)

        return f"""
        <h2>Meeting Created Successfully!</h2>
        <p><strong>Meeting Title:</strong> {meeting_title}</p>
        <p><strong>Meeting ID:</strong> {meeting_response.id}</p>
        <p><strong>Meeting Number:</strong> {meeting_response.meeting_number}</p>
        <p><strong>Meeting Link:</strong> <a href="{meeting_response.web_link}" target="_blank">{meeting_response.web_link}</a></p>
        <p><strong>Join Link:</strong> <a href="{join_response.join_link}" target="_blank">{join_response.join_link}</a></p>
        <a href='/'><button>Go Back</button></a>
        """
    except Exception as e:
        log.error(f"Error creating meeting: {e}")
        return f"<h2>Error Creating Meeting</h2><p>{str(e)}</p><a href='/'><button>Go Back</button></a>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
