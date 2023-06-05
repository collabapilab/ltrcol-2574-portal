import logging
from flask_restx import reqparse, inputs
from os import getenv

"""
Arguments for all API functions. Functions that have parameters will have this a decorator such as
    @api.expect(user_filter_args, validate=True)
To document and limit what can be entered on the /api/v1/ Swagger web page
"""

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(threadName)s %(levelname)s %(name)s %(message)s')
logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)
# Change to DEBUG for detailed REST interaction output
logging.getLogger('wxc_sdk.rest').setLevel(logging.INFO)

log = logging.getLogger(__name__)

# Read the POD_NUM environment variable. Fail if it does not exist.
pod_num = getenv('POD_NUM')
if not str(pod_num).isdigit():
    log.error(f'Error reading POD_NUM environment variable.')
    quit()
pod_num_padded = pod_num.zfill(2)

# CUCM API Arguments
# CUCM Add Phone Query arguments
cucm_add_phone_query_args = reqparse.RequestParser()
cucm_add_phone_query_args.add_argument('description', type=str, required=False, help='Phone Device Description', default=f'Cisco Live LTRCOL2574 - pod{pod_num}ucmuser', location='args')
cucm_add_phone_query_args.add_argument('phonetype', type=str, required=False, help='Phone Device Type', default='Cisco Unified Client Services Framework', location='args')
cucm_add_phone_query_args.add_argument('devicecss', type=str, required=False, help='Phone Device Calling Search Space', location='args')
cucm_add_phone_query_args.add_argument('ownerUserName', type=str, required=True, help='Device Owner User Name', default=f'pod{pod_num}ucmuser', location='args')
cucm_add_phone_query_args.add_argument('calleridname', type=str, required=True, help='Line 1 Caller ID Name', default=f'Pod{pod_num} UCM User', location='args')

# CUCM Update Phone Query arguments
cucm_update_phone_query_args = reqparse.RequestParser()
cucm_update_phone_query_args.add_argument('description', type=str, required=False, help='Phone Device Description', location='args')
cucm_update_phone_query_args.add_argument('isActive', type=inputs.boolean, required=False, help='Phone License Activation Status', default=True, location='args')
cucm_update_phone_query_args.add_argument('callingSearchSpaceName', type=str, required=False, help='Phone Device Calling Search Space', default='Unrestricted_CSS', location='args')

# CUCM Update Line Query arguments
cucm_update_line_query_args = reqparse.RequestParser()
cucm_update_line_query_args.add_argument('callforwardtovm', type=inputs.boolean, required=False, help='Enable Call Forward to Voicemail', default=True, location='args')

# CUCM Update User Query arguments
cucm_update_user_query_args = reqparse.RequestParser()
cucm_update_user_query_args.add_argument('homecluster', type=inputs.boolean, required=False, help='Enable Home Cluster for user', default=True, location='args')

# CUCM List Phones Query arguments
cucm_list_phones_search_criteria_query_args = reqparse.RequestParser()
cucm_list_phones_search_criteria_query_args.add_argument('name', type=str, required=False, help='Name to search', default='%', location='args')
cucm_list_phones_search_criteria_query_args.add_argument('description', type=str, required=False, help='Description to search', location='args')
cucm_list_phones_search_criteria_query_args.add_argument('protocol', type=str, required=False, choices=['SIP', 'SCCP'], help='Device Protocol to search', location='args')
cucm_list_phones_search_criteria_query_args.add_argument('callingSearchSpaceName', type=str, required=False, help='Device Calling Search Space Name to search', location='args')
cucm_list_phones_search_criteria_query_args.add_argument('devicePoolName', type=str, required=False, help='Device Pool Name to search', location='args')
cucm_list_phones_search_criteria_query_args.add_argument('securityProfileName', type=str, required=False, help='Device Security Profile Name to search', location='args')

cucm_list_phones_returned_tags_query_args = reqparse.RequestParser()
cucm_list_phones_returned_tags_query_args.add_argument('returnedTags', type=str, required=False,
                                                       help='Tags/Fields to Return (Supply a list seperated by comma) ie: name, description, product', location='args')

# CUCM Device Search Query arguments
cucm_device_search_criteria_query_args = reqparse.RequestParser()
cucm_device_search_criteria_query_args.add_argument('SearchBy', type=str, required=True,
                                                    choices=['Name', 'IPV4Address', 'IPV6Address', 'DirNumber', 'Description', 'SIPStatus'],
                                                    help='Device Search Field', default='Name', location='args')
cucm_device_search_criteria_query_args.add_argument('SearchItems', type=str, required=True,
                                                    help='List of Device Search Items, comma seperated (* wildcards are accepted)', default='*', location='args')
cucm_device_search_criteria_query_args.add_argument('Status', type=str, required=False,
                                                    choices=['Any', 'Registered', 'UnRegistered', 'Rejected', 'PartiallyRegistered', 'Unknown'],
                                                    help='Device Status to Search', default='Any', location='args')

# CUCM Service Status Query arguments
cucm_service_status_query_args = reqparse.RequestParser()
cucm_service_status_query_args.add_argument('Services', type=str, required=False,
                                            help='List of Services seperated by commas, Leave blank to receive the service status information for all services in the system',
                                            location='args')

# Cisco Meeting Server API Arguments
cms_spaces_post_args = reqparse.RequestParser()
cms_spaces_post_args.add_argument('name', type=str, store_missing=False, help='Name of the Space', location='args')
cms_spaces_post_args.add_argument('uri', type=str, store_missing=False,
                                  help='User URI part for SIP call to reach Space', location='args')
cms_spaces_post_args.add_argument('secondaryUri', type=str, store_missing=False,
                                  help='Secondary URI for SIP call to reach Space', location='args')
cms_spaces_post_args.add_argument('passcode', type=str, store_missing=False,
                                  help='Security code for this Space', location='args')
cms_spaces_post_args.add_argument('defaultLayout', type=str, store_missing=False, default='automatic',
                                  choices=['automatic', 'allEqual', 'speakerOnly',
                                           'telepresence', 'stacked', 'allEqualQuarters'],
                                  help='Default Layout for this Space', location='args')

cms_spaces_get_args = reqparse.RequestParser()
cms_spaces_get_args.add_argument('filter', type=str,
                                 help='String to search for in Name, URI, and secondaryUri fields', location='args')
cms_spaces_get_args.add_argument('limit', type=int, store_missing=False, default=10,
                                 help='Maximum results to return. Note that CMS has an internal limit \
                                       of 10 even though a larger limit can be requested', location='args')
cms_spaces_get_args.add_argument('offset', type=int, store_missing=False, default=0,
                                 help='Return results starting with the offset specified', location='args')

# Cisco Unity Connection API Arguments

cuc_importldap_user_post_args = reqparse.RequestParser()
cuc_importldap_user_post_args.add_argument('templateAlias', type=str, default='voicemailusertemplate',
                                           help='User template alias to create the account with', location='args')
cuc_importldap_user_post_args.add_argument('ListInDirectory', type=inputs.boolean, default=True,
                                           help='List in the Unity Connection Auto Attendant Directory', location='args')
cuc_importldap_user_post_args.add_argument('IsVmEnrolled', type=inputs.boolean, default=True,
                                           help='Play initial enrollment conversation (to record a name, \
                                                 request new password, etc)', location='args')

cuc_users_get_args = reqparse.RequestParser()
cuc_users_get_args.add_argument('column', type=str, default='alias',
                                help='CUC database column to search', location='args')
cuc_users_get_args.add_argument('match_type', type=str, choices=['startswith', 'is'],
                                help='How to perform the search query (column match_type search)', location='args')
cuc_users_get_args.add_argument('search', type=str, help='The string to search for', location='args')
cuc_users_get_args.add_argument('sortorder', type=str, choices=['asc', 'desc'],
                                help='Order of return values (ascending or descending)', default='asc', location='args')
cuc_users_get_args.add_argument('rowsPerPage', type=int,
                                help='Maximum number of rows to return', default=100, location='args')
cuc_users_get_args.add_argument('pageNumber', type=int,
                                help='Page number to return', default=1, location='args')

cuc_users_put_args = reqparse.RequestParser()
cuc_users_put_args.add_argument('ListInDirectory', type=inputs.boolean, store_missing=False,
                                help='List in the Unity Connection Auto Attendant Directory', location='args')
cuc_users_put_args.add_argument('IsVmEnrolled', type=inputs.boolean, store_missing=False,
                                help='Play initial enrollment conversation (to record a name, request new \
                                      password, etc)', location='args')
cuc_users_put_args.add_argument('PIN', type=int, store_missing=False,
                                help='New PIN for the voicemail account', location='args')
cuc_users_put_args.add_argument('ResetMailbox', type=inputs.boolean, store_missing=False,
                                help='Reset mailbox', location='args')

# Webex Messaging API Arguments
wbxt_messages_post_args = reqparse.RequestParser()
wbxt_messages_post_args.add_argument('room_name', type=str, required=True,
                                     help='The Space (Room) title to send the message to',
                                     location='args')
wbxt_messages_post_args.add_argument('text', type=str,
                                     help='The message, in plain text or in markdown.',
                                     location='args')


# Webex Calling API Arguments
wbxc_enable_user_args = reqparse.RequestParser()
wbxc_enable_user_args.add_argument('location', type=str, required=False,
                                   choices=[
                                        'Pod01', 'Pod02', 'Pod03', 'Pod04', 'Pod05', 'Pod06', 'Pod07', 'Pod08',
                                        'Pod09', 'Pod10', 'Pod11', 'Pod12', 'Pod13', 'Pod14', 'Pod15', 'Pod16',
                                        'Pod17', 'Pod18', 'Pod19', 'Pod20', 'Pod21', 'Pod22', 'Pod23', 'Pod24',
                                        'Pod25', 'Pod26', 'Pod27', 'Pod28', 'Pod29', 'Pod30', 'Pod31'
                                   ],
                                   default='Pod' + pod_num_padded,
                                   help='Webex Calling Location name',
                                   location='args')
