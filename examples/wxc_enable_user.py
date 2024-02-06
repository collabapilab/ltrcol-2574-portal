"""
Sample python script demonstrating querying and updating a person in Webex using wxc_sdk
"""
import logging

# Set up logging with a default level of INFO
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
# The logging levels for individual components can be adjusted
logging.getLogger('wxc_sdk.rest').setLevel(logging.DEBUG)
# Create a logging instance
log = logging.getLogger(__name__)

# Replace with your temporary personal access token (from developer.webex.com) or your Service app access token
access_token = '___PASTE_YOUR_ACCESS_TOKEN_HERE___'

# Create an instance of the WebexSimpleApi with your access token

# Query the API for people with that email address
email_to_search = '___REPLACE_WITH_EMAIL_ADDRESS___'

# Iterate through each element (should be only one)

# Retrieve a list of all Webex Licenses for this Org

# Retrieve the pod location name
pod_loc_name = '___REPLACE_WITH_LOCATION_NAME___'

# Append the license ID to the user's list of licenses and remove the UCM license

# Modify the location for the user

# Update the user in Webex
