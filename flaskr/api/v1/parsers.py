from flask_restplus import reqparse, inputs

"""
Arguments for all API functions. Functions that have parameters will have this a decorator such as
    @api.expect(user_filter_args, validate=True)
To document and limit what can be entered on the /api/v1/ Swagger web page
"""

# CUCM API Arguments
# CUCM Add Phone Query arguments
cucm_add_phone_query_args = reqparse.RequestParser()
cucm_add_phone_query_args.add_argument('description', type=str, required=False, help='Phone Device Description', default='Cisco Live LTRCOL2574 - pod31user2')
cucm_add_phone_query_args.add_argument('phonetype', type=str, required=False, help='Phone Device Type', default='Cisco Unified Client Services Framework')
cucm_add_phone_query_args.add_argument('devicecss', type=str, required=False, help='Phone Device Calling Search Space')
cucm_add_phone_query_args.add_argument('ownerUserName', type=str, required=True, help='Device Owner User Name', default='pod31user2')
cucm_add_phone_query_args.add_argument('calleridname', type=str, required=True, help='Line 1 Caller ID Name', default='Pod31 User2')

# CUCM Update Phone Query arguments
cucm_update_phone_query_args = reqparse.RequestParser()
cucm_update_phone_query_args.add_argument('description', type=str, required=False, help='Phone Device Description')
cucm_update_phone_query_args.add_argument('isActive', type=inputs.boolean, required=False, help='Phone License Activation Status', default=True)
cucm_update_phone_query_args.add_argument('callingSearchSpaceName', type=str, required=False, help='Phone Device Calling Search Space', default='Unrestricted_CSS')

# CUCM Update Line Query arguments
cucm_update_line_query_args = reqparse.RequestParser()
cucm_update_line_query_args.add_argument('callforwardtovm', type=inputs.boolean, required=False, help='Enable Call Forward to Voicemail', default=True)

# CUCM List Phones Query arguments
cucm_list_phones_search_criteria_query_args = reqparse.RequestParser()
cucm_list_phones_search_criteria_query_args.add_argument('name', type=str, required=False, help='Name to search', default='%')
cucm_list_phones_search_criteria_query_args.add_argument('description', type=str, required=False, help='Description to search')
cucm_list_phones_search_criteria_query_args.add_argument('protocol', type=str, required=False, choices=['SIP', 'SCCP'], help='Device Protocol to search')
cucm_list_phones_search_criteria_query_args.add_argument('callingSearchSpaceName', type=str, required=False, help='Device Calling Search Space Name to search')
cucm_list_phones_search_criteria_query_args.add_argument('devicePoolName', type=str, required=False, help='Device Pool Name to search')
cucm_list_phones_search_criteria_query_args.add_argument('securityProfileName', type=str, required=False, help='Device Security Profile Name to search')

cucm_list_phones_returned_tags_query_args = reqparse.RequestParser()
cucm_list_phones_returned_tags_query_args.add_argument('returnedTags', type=str, required=False,
                                                       help='Tags/Fields to Return (Supply a list seperated by comma) ie: name, description, product')

# CUCM Device Search Query arguments
cucm_device_search_criteria_query_args = reqparse.RequestParser()
cucm_device_search_criteria_query_args.add_argument('SearchBy', type=str, required=True,
                                                    choices=['Name', 'IPV4Address', 'IPV6Address', 'DirNumber', 'Description', 'SIPStatus'],
                                                    help='Device Search Field', default='Name')
cucm_device_search_criteria_query_args.add_argument('SearchItems', type=str, required=True,
                                                    help='List of Device Search Items, comma seperated (* wildcards are accepted)', default='*')
cucm_device_search_criteria_query_args.add_argument('Status', type=str, required=False,
                                                    choices=['Any', 'Registered', 'UnRegistered', 'Rejected', 'PartiallyRegistered', 'Unknown'],
                                                    help='Device Status to Search', default='Any')

# CUCM Service Status Query arguments
cucm_service_status_query_args = reqparse.RequestParser()
cucm_service_status_query_args.add_argument('Services', type=str, required=False,
                                            help='List of Services seperated by commas, Leave blank to receive the service status information for all services in the system')

# Cisco Meeting Server API Arguments
cms_spaces_post_args = reqparse.RequestParser()
cms_spaces_post_args.add_argument('name', type=str, help='Name of the Space')
cms_spaces_post_args.add_argument('uri', type=str,
                                  help='User URI part for SIP call to reach Space')
cms_spaces_post_args.add_argument('secondaryUri', type=str,
                                  help='Secondary URI for SIP call to reach Space')
cms_spaces_post_args.add_argument('passcode', type=str,
                                  help='Security code for this Space')
cms_spaces_post_args.add_argument('defaultLayout', type=str, default='automatic',
                                  choices=['automatic', 'allEqual', 'speakerOnly',
                                           'telepresence', 'stacked', 'allEqualQuarters'],
                                  help='Default Layout for this Space')

cms_spaces_get_args = reqparse.RequestParser()
cms_spaces_get_args.add_argument('filter', type=str,
                                 help='String to search for in Name, URI, and secondaryUri fields')
cms_spaces_get_args.add_argument('limit', type=int, required=False, default=10,
                                 help='Maximum results to return. Note that CMS has an internal limit \
                                       of 10 even though a larger limit can be requested')
cms_spaces_get_args.add_argument('offset', type=int, default=0,
                                 help='Return results starting with the offset specified')

# Cisco Unity Connection API Arguments

cuc_importldap_user_post_args = reqparse.RequestParser()
cuc_importldap_user_post_args.add_argument('templateAlias', type=str, default='voicemailusertemplate',
                                           help='User template alias to create the account with')
cuc_importldap_user_post_args.add_argument('ListInDirectory', type=bool, default=True,
                                           help='List in the Unity Connection Auto Attendant Directory')
cuc_importldap_user_post_args.add_argument('IsVmEnrolled', type=bool, default=True,
                                           help='Play initial enrollment conversation (to record a name, \
                                                 request new password, etc)')

cuc_users_get_args = reqparse.RequestParser()
cuc_users_get_args.add_argument('column', type=str, default='alias',
                                help='CUC database column to search')
cuc_users_get_args.add_argument('match_type', type=str, choices=['startswith', 'is'],
                                help='How to perform the search query (column match_type search)')
cuc_users_get_args.add_argument('search', type=str, help='The string to search for')
cuc_users_get_args.add_argument('sortorder', type=str, choices=['asc', 'desc'],
                                help='Order of return values (ascending or descending)', default='asc')
cuc_users_get_args.add_argument('rowsPerPage', type=int,
                                help='Maximum number of rows to return', default=100)
cuc_users_get_args.add_argument('pageNumber', type=int,
                                help='Page number to return', default=1)

cuc_users_put_args = reqparse.RequestParser()
cuc_users_put_args.add_argument('ListInDirectory', type=bool,
                                help='List in the Unity Connection Auto Attendant Directory')
cuc_users_put_args.add_argument('IsVmEnrolled', type=bool,
                                help='Play initial enrollment conversation (to record a name, request new \
                                      password, etc)')
cuc_users_put_args.add_argument('PIN', type=int, help='New PIN for the voicemail account')
cuc_users_put_args.add_argument('ResetMailbox', type=bool, help='Reset mailbox')

# Webex Teams API Arguments
wbxt_messages_post_args = reqparse.RequestParser()
wbxt_messages_post_args.add_argument('room_name', type=str, required=True, help='The Space (Room) title to send the message to')
wbxt_messages_post_args.add_argument('text', type=str, help='The message, in plain text')
