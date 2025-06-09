"""
Sample python script demonstrating querying and updating a person in Webex using wxc_sdk
"""
import logging
from pprint import pformat
from wxc_sdk import WebexSimpleApi

# Set up logging with a default level of INFO
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
# The logging levels for individual components can be adjusted
logging.getLogger('wxc_sdk.rest').setLevel(logging.DEBUG)
# Create a logging instance
log = logging.getLogger(__name__)

# Replace with your temporary personal access token (from developer.webex.com) or your Service app access token
access_token = '___PASTE_YOUR_ACCESS_TOKEN_HERE___'

# Create an instance of the WebexSimpleApi with your access token
api = WebexSimpleApi(tokens=access_token)

# Query the API for people with that email address
email_to_search = '___REPLACE_WITH_EMAIL_ADDRESS___'
webex_user_list = list(api.people.list(email=email_to_search))

# Iterate through each element (should be only one)
for webex_user in webex_user_list:
    # Dump user data
    log.info(webex_user.model_dump_json(indent=4))

    # Get detailed user information
    webex_user_det = api.people.details(person_id=webex_user.person_id, calling_data=True)
    log.info(f'Detailed User information found for "{webex_user_det.display_name}":')
    log.info(pformat(vars(webex_user_det), indent=4))

# Retrieve a list of all Webex Licenses for this Org
webex_license_list = list(api.licenses.list())
for wxc_license in webex_license_list:
    if wxc_license.name == 'Webex Calling - Professional':
        wxc_pro_license = wxc_license
        log.info(f'\n  License name: {wxc_pro_license.name}\n  License ID: {wxc_pro_license.license_id}')
    if wxc_license.name == 'Unified Communication Manager (UCM)':
        ucm_license = wxc_license
        log.info(f'\n  License name: {ucm_license.name}\n  License ID: {ucm_license.license_id}')

# Retrieve the pod location name
pod_loc_name = '___REPLACE_WITH_LOCATION_NAME___'
webex_location = api.locations.by_name(pod_loc_name)
log.info(f'\n  Location name: {webex_location.name}\n  Location ID: {webex_location.location_id}')

# Append the license ID to the user's list of licenses and remove the UCM license
if wxc_pro_license.license_id not in webex_user_det.licenses:
    webex_user_det.licenses.append(wxc_pro_license.license_id)
if ucm_license.license_id in webex_user_det.licenses:
    webex_user_det.licenses.remove(ucm_license.license_id)

# Modify the location for the user
webex_user_det.location_id = webex_location.location_id

# Update the user in Webex
modified_webex_user = api.people.update(person=webex_user_det, calling_data=True)
log.info(modified_webex_user.model_dump_json(indent=4))
