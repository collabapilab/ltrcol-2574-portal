from requests import get, post, put, delete, packages,request
from requests.exceptions import RequestException, HTTPError
from base64 import b64encode
from requests.auth import HTTPBasicAuth
# from requests.packages.urllib3.exceptions import InsecureRequestWarning
# import xmltodict
# import xml.etree.ElementTree as ET
# from flask import jsonify
# from flask import render_template
# import json
# import urllib.parse
# import base64
# packages.urllib3.disable_warnings(InsecureRequestWarning)
# from urllib.request import urlopen, Request
# import sys, re, ssl, urllib.parse, base64, json, xmltodict, urllib, xml.etree.ElementTree as ET
# from requests import exceptions
# from xml.dom import minidom
# import xml.parsers.expat


class REST:
    """The REST Server class

    Use this class to connect and make API calls to an most REST-based devices.

    :param host: The Hostname / IP Address of the server
    :param username: The username of an account with access to the API.
    :param password: The password for your user account
    :param port: (optiona) The server port for API access (default: 443)
    :type host: String
    :type username: String
    :type password: String
    :type port: Integer
    :returns: return an REST object
    :rtype: REST

    """

    def __init__(self, host, username=None, password=None, access_token=None, base_url=None, port=443):
        self.host = host
        # self.username = username
        # self.password = password
        self.port = str(port)
        self.base_url = base_url
        
        if access_token:
            self.auth = "Bearer " + access_token
        else:
            self.auth = "Basic " + b64encode(str.encode(username + ":" + password)).decode("utf-8")
            # self.auth = HTTPBasicAuth(self.username, self.password)


    def _send_request(self, api_method, parameters={}, payload=None, headers={}, HTTPmethod='GET'):

        # Build a URL, such as https//host:8443/api/v1/api_method
        url = "https://{}:{}{}/{}".format(self.host, self.port, self.base_url, api_method)

        # auth = HTTPBasicAuth(self.username, self.password)
        headers['Authorization'] = self.auth
        try:
            # print("Sending {} request to {} with params: {}".format(HTTPmethod, url, parameters))
            # if payload:
            # 	print("  Payload:")
            # 	print(payload)
            # print("---")
            # Send the request and handle any exception that may occur
            resp = request(HTTPmethod, url, data=payload, params=parameters,
                           headers=headers, verify=False, timeout=2)
            # resp = request(HTTPmethod, url, auth=self.auth, data=payload, params=parameters,
            #                headers=headers, verify=False, timeout=2)
            result = {
                'success': True, 
                'response': resp
                }

        except RequestException as e:
            result = {
                'success': False,
                'message': 'EXCEPTION: ' + str(e)
                }
        return result


    def _check_non2XX_response(self, resp):
        result = {
            'success': resp['success'],
            'server_response': resp['response'].status_code
        }

        # Look for non-2XX HTTP Errors
        try:
            # Raise HTTPError error for non-2XX responses
            resp['response'].raise_for_status()
        except HTTPError as e:
            # Response outside for 2XX range
            result['success'] = False
            result['message'] = 'HTTP EXCEPTION: ' + str(e)
        return result



# class CUPI(REST):
#     """The CUPI Server class

#     Use this class to connect and make API calls using the Cisco Unity Provisioning Interface.

#     :param host: The Hostname / IP Address of the server
#     :param username: The username of an account with access to the API.
#     :param password: The password for your user account
#     :param port: (optiona) The server port for API access (default: 443)
#     :type host: String
#     :type username: String
#     :type password: String
#     :type port: Integer
#     :returns: return an CUPI object
#     :rtype: CUPI

#     """

#     def __init__(self, host, username, password, port=443):
#         # Create a super class, where the CUPI class inherits from the REST class.  This will allow us to 
#         # add CUPI-specific items.
#         # Reference:  https://realpython.com/python-super/
#         super().__init__(host, username, password, base_url='/vmrest', port=port)

#         self.headers = {
#             'Accept': 'application/json',
#             'Connection': 'keep-alive',
#             'Content-Type': 'application/json'
#         }


#     def _cupi_parse_response(self, resp):
#         '''
#         When requested, CUPI will respond with JSON payload.  However in some cases, such as importing a user, the payload
#         may just be a binary string, since it is only returning the object's ID.
#         '''

#         result = {
#             'success': False
#         }
#         try:
#             result['server_response'] = resp.status_code
#             # Raise HTTPError error for non-2XX responses
#             resp.raise_for_status()
#             result['success'] = True
#             # parse response
#             # json.loads(json.dumps(xml... in order to convert from OrderedDict to dict
#             response = json.loads(resp.content.decode("utf-8"))
#             try:
#                 # check if there is only one element, meaning xmltodict would not have created a list
#                 if(str(response["@total"]) == "1"):
#                     # Get the child key nested under the root (e.g. 'Users')
#                     rootobj = [key for key in response.keys() if key not in '@total'][0]
#                     # Force the child element to be a list
#                     response[rootobj] = [response[rootobj]]

#             # Maybe the @total key didn't exist; we'll just return the result
#             except KeyError:
#                 pass
#             result['results'] = json.loads(json.dumps(response))
                
#         except json.decoder.JSONDecodeError as e:
#             # Could not decode as JSON; that means the result was most likely a binary string
#             result['message'] = resp.content.decode()
#         except exceptions.HTTPError as e:
#             # Response outside for 2XX range
#             result['message'] = 'HTTP Exception: ' + str(e)
#         except xml.parsers.expat.ExpatError as e:
#             result['message'] = 'XML Parse Error: ' + str(e)

#         return result

#     def _cupi_request(self, api_method, parameters={}, payload=None, HTTPmethod='GET'):
#         # Create a line of URL paramters from the dictionary, however only convert the spaces to %20
#         # parameters = "&".join("{}={}".format(*i) for i in parameters.items()).replace(' ', '%20')
#         resp = self._send_request(api_method, parameters=parameters, payload=json.dumps(payload), headers=self.headers, HTTPmethod=HTTPmethod)
#         if resp['success']:
#             resp = self._cupi_parse_response(resp['response'])
#         return resp

#     def get_users(self, parameters={}):
#         """Get a list of users on the Unity Connection system.

#         See also:  
#         https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/connection/REST-API/CUPI_API/b_CUPI-API/b_CUPI-API_chapter_011101.html#reference_E4DD44846143441C8FB01478AB71476B
#         """
#         return self._cupi_request("users", parameters=parameters)

#     def get_ldapusers(self, parameters={}):
#         """Get a list of users on the Unity Connection system.

#         See also:  
#         https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/connection/REST-API/CUPI_API/b_CUPI-API/b_CUPI-API_chapter_011101.html#reference_E4DD44846143441C8FB01478AB71476B
#         """
#         return self._cupi_request("import/users/ldap", parameters=parameters)

#     def import_ldapuser(self, parameters={}, payload=None):
#         """Get a list of users on the Unity Connection system.

#         See also:  
#         https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/connection/REST-API/CUPI_API/b_CUPI-API/b_CUPI-API_chapter_011101.html#reference_E4DD44846143441C8FB01478AB71476B
#         """
#         return self._cupi_request("import/users/ldap", parameters=parameters, payload=payload, HTTPmethod='POST')

#     def get_user(self, id):
#         """Get a voicemail user from the Unity Connection system by user id.

#         See also:  
#         https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/connection/REST-API/CUPI_API/b_CUPI-API/b_CUPI-API_chapter_011101.html#reference_E4DD44846143441C8FB01478AB71476B
#         """
#         return self._cupi_request("users/" + str(id))

#     def update_user(self, id, payload=None):
#         """Modify a user on the Unity Connection system.

#         See also:  
#         https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/connection/REST-API/CUPI_API/b_CUPI-API/b_CUPI-API_chapter_011101.html#reference_E4DD44846143441C8FB01478AB71476B
#         """
#         return self._cupi_request("users/" + str(id), payload=payload, HTTPmethod='PUT')

#     def delete_user(self, id):
#         """Delete a user from the Unity Connection system.

#         See also:  
#         https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/connection/REST-API/CUPI_API/b_CUPI-API/b_CUPI-API_chapter_011101.html#reference_E4DD44846143441C8FB01478AB71476B
#         """
#         return self._cupi_request("users/" + str(id), HTTPmethod='DELETE')






# class CMS(REST):
#     """The CMS Server class

#     Use this class to connect and make API calls to an most REST-based devices.

#     :param host: The Hostname / IP Address of the server
#     :param username: The username of an account with access to the API.
#     :param password: The password for your user account
#     :param port: (optiona) The server port for API access (default: 443)
#     :type host: String
#     :type username: String
#     :type password: String
#     :type port: Integer
#     :returns: return an CMS object
#     :rtype: CMS

#     """

#     def __init__(self, host, username, password, port=443):
#         super().__init__(host, username, password, base_url='/api/v1', port=port)
#         self.headers = {
#             'Accept': 'application/xml',
#             'Connection': 'keep-alive',
#             'Content-Type': 'application/json'
#         }

#         self.error_codes = {
#                 "accessMethodDoesNotExist": "You tried to modify or remove an accessMethod using an ID that did not correspond to a valid access method",
#                 "callBrandingProfileDoesNotExist": "You tried to modify or remove a call branding profile using an ID that did not correspond to a valid call branding profile",
#                 "callBridgeDoesNotExist": "You tried to modify or remove a configured clustered Call Bridge using an ID that did not correspond to a valid clustered Call Bridge",
#                 "callDoesNotExist": "You tried to perform a method on a call object using an ID that did not correspond to a currently active call",
#                 "callRecordingCannotBeModified": "You tried to start/stop recording a call that cannot be modified. Present from R1.9",
#                 "callLegCannotBeDeleted": "You tried to delete a call leg that can't be deleted. Present from R1.8",
#                 "callLegDoesNotExist": "You tried to perform a method on a call leg object using an ID that did not correspond to a currently active call leg",
#                 "callLegProfileDoesNotExist": "You tried to modify or remove a callLegProfile using an ID that did not correspond to a valid call leg profile",
#                 "callProfileDoesNotExist": "You tried to modify or remove a callProfile using an ID that is not valid",
#                 "cdrReceiverDoesNotExist": "You tried to modify or remove a CDR receiver using an ID that did not correspond to a valid CDR receiver. Present from R1.8",
#                 "coSpaceDoesNotExist": "You tried to modify or remove a coSpace using an ID that did not correspond to a valid coSpace on the system",
#                 "coSpaceUserDoesNotExist": "You tried to modify or remove a coSpace user using an ID that did not correspond to a valid coSpace user",
#                 "databaseNotReady": "You tried a method (e.g. initiation of an LDAP sync method) before the database was ready",
#                 "directorySearchLocationDoesNotExist": " You tried to reference, modify or remove a directory search location using an ID that did not correspond to a valid directory search location. Present from R1.8",
#                 "dtmfProfileDoesNotExist": " You tried to reference, modify or remove a DTMF profile using an ID that did not correspond to a valid DTMF profile",
#                 "duplicateCallBridgeName": "You tried to create or modify a clustered Call Bridge to use a name that would clash with an existing configured clustered Call Bridge",
#                 "duplicateCoSpaceId": "You tried to create or modify a coSpace call ID to use a call ID that clashed with one used by another coSpace",
#                 "duplicateCoSpaceUri": " You tried to create or modify a coSpace to use a URI that clashed with one that corresponds to another coSpace. (Two coSpaces can't share the same URI, because the Meeting Server must be able to uniquely resolve an incoming call to a coSpace URI)",
#                 "duplicateCoSpaceSecret": " You tried to modify a coSpace, or create or modify a coSpace access method, using a secret that clashed with one that is already used by that coSpace or one of its access methods",
#                 "forwardingDialPlanRuleDoesNotExist": "You tried to modify or remove an forwarding dial plan rule using an ID that did not correspond to a valid forwarding dial plan rule",
#                 "inboundDialPlanRuleDoesNotExist": "You tried to modify or remove an inbound dial plan rule using an ID that did not correspond to a valid inbound dial plan rule",
#                 "inboundDialPlanRuleUriConflict": " You tried to make modifications to an inbound dial plan rule which would have caused a URI conflict. For example, this can happen if you try to add a rule which matches multiple tenants and more than one tenant has a coSpace with the same URI",
#                 "invalidOperation": " You tried an operation which isn't supported; for example, you attempted to POST to /api/v1/system/profiles or issue a DELETE for a configured user generated from an LDAP sync",
#                 "invalidVersion": "You attempted an operation with an invalid API version. Present from R1.8",
#                 "ivrBrandingProfileDoesNotExist": "You tried to modify or remove an IVR branding profile object using an ID that did not correspond to a valid IVR branding profile on the system",
#                 "ivrDoesNotExist": "You tried to modify or remove an IVR object using an ID that did not correspond to a valid IVR on the system",
#                 "ivrUriConflict": "You tried to make modifications to an IVR object which would have caused a URI conflict",
#                 "ldapMappingDoesNotExist": "You tried to modify or remove an LDAP mapping using an ID that did not correspond to a valid LDAP mapping",
#                 "ldapServerDoesNotExist": "You tried to modify or remove an LDAP server using an ID that did not correspond to a valid LDAP server",
#                 "ldapSourceDoesNotExist": "You tried to modify or remove an LDAP source using an ID that did not correspond to a valid LDAP source",
#                 "ldapSyncCannotBeCancelled": "You tried to cancel an LDAP synchronization that has either started or completed – only LDAP synchronization methods that have not started yet can be cancelled",
#                 "ldapSyncDoesNotExist": "You tried to query or cancel an LDAP synchronization with an ID that did not correspond to a valid LDAP synchronization",
#                 "messageDoesNotExist": "You tried to remove a coSpace message using an ID that did not correspond to a valid coSpace message",
#                 "outboundDialPlanRuleDoesNotExist": "You tried to modify or remove an outbound dial plan rule using an ID that did not correspond to a valid outbound dial plan rule",
#                 "parameterError": "One or more parameters in a request were found to be invalid. Supporting parameter and error values give more detail about the failure",
#                 "participantLimitReached": "You tried to add a new participant beyond the maximum number allowed for the call",
#                 "recorderDoesNotExist": "You tried to modify or remove a recorder using an ID that did not correspond to a valid recorder. Present from R1.9",
#                 "tenantDoesNotExist": "You tried to modify or remove a tenant using an ID that did not correspond to a valid tenant",
#                 "tenantGroupCoSpaceIdConflict": "Your request to remove or use a tenant group would have resulted in a coSpace ID conflict. Present from R1.8",
#                 "tenantGroupDoesNotExist": " You tried to modify, remove or use a tenant group that does not exist. Present from R1.8",
#                 "tenantParticipantLimitReached": "You tried to add a new participant beyond the maximum number allowed for the owning tenant",
#                 "tooManyCdrReceivers": "You tried to add a new CDR receiver when the maximum number were already present. R1.8 supports up to 2 CDR receivers",
#                 "tooManyLdapSyncs": "A method to create a new LDAP synchronization method failed. Try again later",
#                 "unrecognizedObject": " There are elements in the URI you are accessing that are not recognized; e.g, you tried to perform a GET on /api/v1/system/profile rather than (the correct) /api/v1/system/profiles",
#                 "userDoesNotExist": "You tried to modify or remove a user using an ID that did not correspond to a valid user",
#                 "userProfileDoesNotExist": "You tried to modify a user profile using an ID that did not correspond to a valid user profile"
#             }


#     def _cms_parse_response(self, resp):

#         result = self._check_non2XX_response(resp)

#         try:
#             if resp.status_code in list(range(200, 300)):
#                 # parse response
#                 # json.loads(json.dumps(xml... in order to convert from OrderedDict to dict
#                 response = xmltodict.parse(resp.content.decode("utf-8"))
#                 if len(response) == 0:
#                     try:
#                         result['location'] = response.headers._store['location']
#                     except:
#                         # No location header present
#                         pass
#                     result['message'] = json.loads(json.dumps(response))
#                 else:
#                     try:
#                         # Get the root key from the dictionary (e.g. 'coSpaces')
#                         rootName = list(response.keys())[0]

#                         # check if there is only one element, meaning xmltodict would not have created a list
#                         if(response[rootName]["@total"] == "1"):
#                             # Get the child key nested under the root (e.g. 'coSpace')
#                             childName = list(response[rootName].keys())[1]
#                             # Force the child element to be a list
#                             response = xmltodict.parse(resp.content, force_list={childName: True})

#                     # Maybe the @total key didn't exist; we'll just return the result
#                     except KeyError:
#                         pass
#                     result['message'] = json.loads(json.dumps(response))
#             else:
#                 # Error codes for CMS
#                 try:
#                     root = ET.fromstring(resp.content)
#                     error_tag = root[0].tag
#                     try:
#                         result['success']: False
#                         result['message'] = error_tag + ': ' + self.error_codes[error_tag]
#                     except KeyError:
#                         # We couldn't map that error code, so just return the tag
#                         result['message'] = error_tag
#                 except IndexError:
#                     # We couldn't find the root element item
#                     pass
#                 except ET.ParseError:
#                     # We couldn't parse the XML
#                     result['success']: False
#                     result['message'] = 'Invalid XML received from device'

#         except xml.parsers.expat.ExpatError:
#             try:
#                 result = resp.headers['location'].split("/")[len(resp.headers['location'].split("/"))-1]
#             except:
#                 result = resp.headers['Date']
#         except RequestException as e:
#             result['success']: False
#             result['message'] = 'EXCEPTION: ' + str(e)

#         return result


#     def _cms_request(self, method, parameters={}, payload=None, HTTPmethod='GET'):
#         # Change the parameters from dictionary to an encoded string
#         parameters = urllib.parse.urlencode(parameters)
#         resp = self._send_request(method, parameters=parameters, payload=payload, headers=self.headers, HTTPmethod=HTTPmethod)
#         if resp['success']:
#             resp = self._cms_parse_response(resp['response'])
#         return resp


#     def get_system_status(self):
#         """Get information on the current system status, e.g. software version, uptime etc.
        
#         :Example:
#             >>> print(a.get_system_status())

#         .. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=68
#         .. note:: v1.8 upward
#         """
#         # return self._send_request("system/status")
#         return self._cms_request("system/status")

#     def get_coSpaces(self, parameters={}):
#         """Get the coSpaces within the Acano VM. These are returned in an arbitrary order.

#         :param parameters: A dictionary of parameters, per the Acano API.
#         :type parameters: Dict
        
#         :Example:
#             >>> print(a.get_coSpaces())

#         :Example:

#             >>> print(a.get_coSpaces(parameters = {
#             >>> 'offset' : 5
#             >>> }))

#         .. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=25
#         .. note:: v1.8 upward

#         """
#         return self._cms_request("coSpaces", parameters=parameters)

#     def create_coSpace(self, payload={}):
#         """Create a new coSpace

#         :param payload: Details the initial state of the newly created coSpace
#         :type payload: Dict
        
#         :Example:
#             >>> print(a.create_coSpace())

#         :Example:

#             >>>	print(a.create_coSpace(payload = {
#             >>>	'name' : 'Emergency meeting'
#             >>>	}))

#         .. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=25
#         .. note:: v1.8 upward

#         """
#         return self._cms_request("coSpaces", payload=payload, HTTPmethod='POST')

#     def modify_coSpace(self, coSpace_id, payload):
#         """Make changes to an existing coSpace, using the coSpace ID as the identifier.

#         :param coSpace_id: The ID of the coSpace to modify. This can be returned from the get_coSpaces()["coSpaces"]["coSpace"][i]["@id"]
#         :type coSpace_id: String

#         :param payload: Details the new state of the identified coSpace
#         :type payload: Dict
        
#         :Example:
#             >>>	print(a.modify_coSpace("3b8dfa05-f7b6-41f2-b14a-739a0d015b90", payload = {
#             >>>	"name" : "Modified coSpace"
#             >>>	}))

#         .. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=25
#         .. note:: v1.8 upward
#         """
#         return self._send_request(("coSpaces/" + coSpace_id), payload=payload, HTTPmethod='PUT')

#     def get_coSpace(self, coSpace_id):
#         """Get the details of a coSpace, using the coSpace ID as the identifier.

#         :param coSpace_id: The ID of the coSpace to modify. This can be returned from the get_coSpaces()["coSpaces"]["coSpace"][i]["@id"]
#         :type coSpace_id: String

#         :param parameters: Filters for the query
#         :type parameters: Dict
        
#         :Example:
#             >>> print(a.get_coSpace("3b8dfa05-f7b6-41f2-b14a-739a0d015b90"))

#         .. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=27
#         .. note:: v1.8 upward
#         """
#         return self._send_request(("coSpaces/" + coSpace_id))

#     def delete_coSpace(self, coSpace_id):
#         """Delete a coSpace, using the coSpace ID as the identifier.

#         :param coSpace_id: The ID of the coSpace to delete. This can be returned from the get_coSpaces()["coSpaces"]["coSpace"][i]["@id"]
#         :type coSpace_id: String
        
#         :Example:
#             >>> print(a.delete_coSpace("3b8dfa05-f7b6-41f2-b14a-739a0d015b90"))

#         .. note:: This function is not explicitly described in the Acano API reference
#         .. note:: v1.8 upward
#         """
#         return self._send_request(("coSpaces/" + coSpace_id), HTTPmethod="delete".upper())

#     # def _coSpaces_coSpaceID_coSpaceUsers_node_(self, coSpace_id, parameters={}, payload={}, HTTPmethod='GET'):
#     # 	return self._send_request(("coSpaces/" + coSpace_id + "/coSpaceUsers"), parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

#     # def get_coSpace_members(self, coSpace_id, parameters={}):
#     # 	"""Get the members in a coSpace, using the coSpace ID as the identifier.

#     # 	:param coSpace_id: The ID of the coSpace for which to get members. This can be returned from the get_coSpaces()["coSpaces"]["coSpace"][i]["@id"]
#     # 	:type coSpace_id: String

#     # 	:param parameters: Details the parameters of the HTTP GET
#     # 	:type parameters: Dict
        
#     # 	:Example:
#     # 	>>> print(a.get_coSpace_members("3b8dfa05-f7b6-41f2-b14a-739a0d015b90"))

#     # 	.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=27
#     # 	.. note:: v1.8 upward
#     # 	"""
#     # 	return self._coSpaces_coSpaceID_coSpaceUsers_node_(coSpace_id, parameters=parameters, HTTPmethod='GET')

#     # def add_member_to_coSpace(self, coSpace_id, payload={}):
#     # 	"""Add a member to the coSpace, using the coSpace ID as the identifier.

#     # 	:param coSpace_id: The ID of the coSpace for which to add a member. This can be returned from the get_coSpaces()["coSpaces"]["coSpace"][i]["@id"]
#     # 	:type coSpace_id: String

#     # 	:param payload: Details the member to add. Must contain the User JID.
#     # 	:type payload: Dict
        
#     # 	:Example:
#     # 		>>> print(a.add_member_to_coSpace("3b8dfa05-f7b6-41f2-b14a-739a0d015b90", payload {
#     # 		>>> 'userJid' : a.get_coSpace_members()["coSpaceMembers]
#     # 		>>> }))

#     # 	.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=30
#     # 	.. note:: v1.8 upward
#     # 	"""
#     # 	return self._coSpaces_coSpaceID_coSpaceUsers_node_(coSpace_id, payload=payload, HTTPmethod='POST')

#     # def _coSpaces_coSpaceID_coSpaceUsers_coSpaceUserID_node_(self, coSpace_id, coSpace_user_id, parameters={}, payload={}, HTTPmethod='GET'):
#     # 	return self._send_request(("coSpaces/" + coSpace_id + "/coSpaceUsers/" + coSpace_user_id), parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

#     # def modify_coSpace_member(self, coSpace_id, coSpace_user_id, payload={}):
#     # 	"""Make changes to the permissions of a user in a coSpace, using the coSpace ID and user ID as the identifiers.

#     # 	:param coSpace_id: The ID of the coSpace for to get the user. This can be returned from the get_coSpaces()["coSpaces"]["coSpace"][i]["@id"]
#     # 	:type coSpace_id: String

#     # 	:param coSpace_user_id: The ID of the user. 
#     # 	:type coSpace_user_id: String

#     # 	:param payload: Details the state to which to update the user. 
#     # 	:type payload: Dict
        
#     # 	:Example:
#     # 		>>> print(a.modify_coSpace_member("3b8dfa05-f7b6-41f2-b14a-739a0d015b90", user_id, payload {
#     # 		>>> 'canDestroy' : 'true'
#     # 		>>> }))

#     # 	.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=30
#     # 	.. note:: v1.8 upward
#     # 	"""
#     # 	return self._coSpaces_coSpaceID_coSpaceUsers_coSpaceUserID_node_(coSpace_id, coSpace_user_id, payload, HTTPmethod='PUT')

#     # def get_coSpace_member(self, coSpace_id, coSpace_user_id):
#     # 	"""Make changes to the permissions of a user in a coSpace, using the coSpace ID and user ID as the identifiers.

#     # 	:param coSpace_id: The ID of the coSpace for to get the user. This can be returned from the get_coSpaces()["coSpaces"]["coSpace"][i]["@id"]
#     # 	:type coSpace_id: String

#     # 	:param coSpace_user_id: The ID of the user. 
#     # 	:type coSpace_user_id: String
        
#     # 	:Example:
#     # 		>>> print(a.get_coSpace_member("3b8dfa05-f7b6-41f2-b14a-739a0d015b90", user_id)

#     # 	.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=31
#     # 	.. note:: v1.8 upward
#     # 	"""
#     # 	return self._coSpaces_coSpaceID_coSpaceUsers_coSpaceUserID_node_(coSpace_id, coSpace_user_id, HTTPmethod='GET')

#     # def _coSpaces_coSpaceID_messages_node_(self, coSpace_id, parameters={}, payload={}, HTTPmethod='GET'):
#     # 	return self._send_request(("coSpaces/" + coSpace_id + "/messages"), parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

#     # def post_message_to_coSpace(self, coSpace_id, payload={}):
#     # 	"""Post a message to the board of a coSpace.

#     # 	:param coSpace_id: The ID of the coSpace. This can be returned from the get_coSpaces()["coSpaces"]["coSpace"][i]["@id"]
#     # 	:type coSpace_id: String

#     # 	:param payload: Details the message to send. 
#     # 	:type payload: Dict
        
#     # 	:Example:
#     # 		>>> print(a.post_message_to_coSpace("3b8dfa05-f7b6-41f2-b14a-739a0d015b90", payload = {
#     # 		>>>	'message' : 'hello world',
#     # 		>>>	'from' : 'George'	
#     # 		>>>	})

#     # 	.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=31
#     # 	.. note:: v1.8 upward
#     # 	"""
#     # 	return self._coSpaces_coSpaceID_messages_node_(coSpace_id, payload, HTTPmethod='POST')

#     # def delete_message_from_coSpace(self, coSpace_id, payload={}):
#     # 	"""Delete messages from the board of a coSpace

#     # 	:param coSpace_id: The ID of the coSpace for to get the user. This can be returned from the get_coSpaces()["coSpaces"]["coSpace"][i]["@id"]
#     # 	:type coSpace_id: String

#     # 	:param payload: Details the messages to remove. 
#     # 	:type payload: Dict
        
#     # 	:Example:
#     # 		>>> print(a.delete_message_from_coSpace("3b8dfa05-f7b6-41f2-b14a-739a0d015b90", payload = {
#     # 		>>>	'maxAge' : 20
#     # 		>>>	})

#     # 	.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=32
#     # 	.. note:: v1.8 upward
#     # 	"""
#     # 	return self._coSpaces_coSpaceID_messages_node_(coSpace_id, payload, HTTPmethod="delete".upper())

#     # def _userProfiles_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
#     # 	return self._send_request("userProfiles", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

#     # def get_user_profiles(self, parameters={}):
#     # 	"""Get the user profiles that exist within the VM.

#     # 	:param parameters: Details filters for the query. 
#     # 	:type parameters: Dict
        
#     # 	:Example:
#     # 		>>> print(a.get_user_profiles()

#     # 	.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=66
#     # 	.. note:: v1.8 upward
#     # 	"""
#     # 	return self._userProfiles_node_(parameters=parameters, HTTPmethod='GET')

#     # def create_user_profile(self, payload={}):
#     # 	"""Create a new user profile

#     # 	:param payload: Details the inital state of the new user profile. 
#     # 	:type payload: Dict
        
#     # 	:Example:
#     # 		>>> print(a.create_user_profile(payload = {
#     # 		>>>	"cancreateCoSpaces" : True	
#     # 		>>>	})

#     # 	.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=66
#     # 	.. note:: v1.8 upward
#     # 	"""
#     # 	return self._userProfiles_node_(payload=payload, HTTPmethod='POST')

#     # def _userProfiles_userProfile_id_node_(self, user_profile_id, parameters={}, payload={}, HTTPmethod='GET'):
#     # 	return self._send_request("userProfiles/" + user_profile_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

#     # def get_user_profile(self, user_profile_id):
#     # 	"""Get a specific existing user profile

#     # 	:param user_profile_id: Identifies the user profile to return
#     # 	:type user_profile_id: String
        
#     # 	:Example:
#     # 		>>> print(a.get_user_profile())

#     # 	.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=67
#     # 	.. note:: v1.8 upward
#     # 	"""
#     # 	return self._userProfiles_userProfile_id_node_(user_profile_id, HTTPmethod='GET')

#     # def modify_user_profile(self, user_profile_id, payload={}):
#     # 	"""Modify an existing user profile

#     # 	:param user_profile_id: Identifies the user profile to modify
#     # 	:type user_profile_id: String

#     # 	:param payload: Details the new state of the user profile. 
#     # 	:type payload: Dict
        
#     # 	:Example:
#     # 		>>> print(a.modify_user_profile(payload = {
#     # 		>>>	"cancreateCoSpaces" : False	
#     # 		>>>	})

#     # 	.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=66
#     # 	.. note:: v1.8 upward
#     # 	"""

#     # 	return self._userProfiles_userProfile_id_node_(user_profile_id, payload=payload, HTTPmethod='PUT')

#     def get_system_alarms(self):
#         """Get information on the current system alarm status.
        
#         :Example:
#             >>> print(a.get_system_alarms())

#         .. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=68
#         .. note:: v1.8 upward
#         """
#         return self._send_request("system/alarms", HTTPmethod='GET')

# # 	def get_system_database(self):
# # 		"""Get information on the system database status.
        
# # 		:Example:
# # 			>>> print(a.get_system_database())

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=70
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._send_request("system/database", HTTPmethod='GET')

# # 	def _system_cdrReceivers_cdrReceiverId_node_(self, cdr_receiver_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("system/cdrReceivers/" + cdr_receiver_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_cdr_receiver(self, cdr_receiver_id):
# # 		"""Get a specific Call Detail Record Receiver by ID

# # 		:param cdr_receiver_id: Identifies the CDR to return
# # 		:type cdr_receiver_id: String

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=71
# # 		.. seealso:: https://www.acano.com/publications/2013/07/Acano-Solution-R1.6-CDR-Guide.pdf#page=6
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._system_cdrReceivers_cdrReceiverId_node_(cdr_receiver_id, HTTPmethod='GET')

# # 	def modify_cdr_receiver(self, cdr_receiver_id, payload={}):
# # 		"""Modify a Call Detail Record Receiver by ID

# # 		:param cdr_receiver_id: Identifies the CDR to return
# # 		:type cdr_receiver_id: String

# # 		:param payload: Details the new state of the CDR receiver. 
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=71
# # 		.. seealso:: https://www.acano.com/publications/2013/07/Acano-Solution-R1.6-CDR-Guide.pdf#page=6
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._system_cdrReceivers_cdrReceiverId_node_(cdr_receiver_id, payload=payload, HTTPmethod='PUT')

# # 	def _system_cdrReceivers_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("system/cdrReceivers", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_cdr_receivers(self, parameters={}):
# # 		"""Get the Call Detail Record receivers

# # 		:param parameters: Details filters for the query 
# # 		:type parameters: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=71
# # 		.. seealso:: https://www.acano.com/publications/2013/07/Acano-Solution-R1.6-CDR-Guide.pdf#page=6
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._system_cdrReceivers_node_(parameters=parameters, HTTPmethod='GET')

# # 	def create_cdr_receiver(self, payload={}):
# # 		"""Create a new Call Detail Record receiver

# # 		:param payload: Details the initial state of the CDR receiver
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=71
# # 		.. seealso:: https://www.acano.com/publications/2013/07/Acano-Solution-R1.6-CDR-Guide.pdf#page=6
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._system_cdrReceivers_node_(payload=payload, HTTPmethod='POST')

# # 	def _system_profiles_node_(self, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("system/profiles", payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_global_profile(self):
# # 		"""Get the global profile

# # 		:Example:
# # 			>>> print(a.get_global_profile())

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=72
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._system_profiles_node_(HTTPmethod='GET')

# # 	def modify_global_profile(self, payload={}):
# # 		"""Modify the global profile

# # 		:param payload: Details the modified state of the global profile
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=72
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._system_profiles_node_(payload=payload, HTTPmethod='PUT')

# # 	def create_global_profile(self, payload={}):
# # 		"""Set up the global profile

# # 		:param payload: Details the inital state of the global profile
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=72
# # 		.. note:: v1.8 upward
# # 		"""

# # 		return self._system_profiles_node_(payload=payload, HTTPmethod='POST')

# # 	def _turnServers_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("turnServers", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_turn_servers(self, parameters={}):
# # 		"""Get the TURN servers. TURN, in this context being Traversal Using Relay NAT

# # 		:param parameters: Details filters for the query
# # 		:type parameters: Dict

# # 		:Example:
# # 			>>> print(a.get_turn_servers())

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=72
# # 		.. seealso:: https://www.acano.com/publications/2013/08/Acano-solution-Deployment-Guide.pdf#page=50
# # 		.. seealso:: http://en.wikipedia.org/wiki/Traversal_Using_Relay_NAT
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._turnServers_node_(parameters=parameters, HTTPmethod='GET')

# # 	def create_turn_server(self, payload={}):
# # 		"""Set up a new TURN server. TURN, in this context being Traversal Using Relay NAT

# # 		:param payload: Details the initial state of the TURN server
# # 		:type payload: Dict

# # 		:Example:
# # 			>>> print(a.create_turn_server(payload = {
# # 			>>>		"ServerAddress" : "192.168.12.50"
# # 			>>>	}))

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=72
# # 		.. seealso:: https://www.acano.com/publications/2013/08/Acano-solution-Deployment-Guide.pdf#page=50
# # 		.. seealso:: http://en.wikipedia.org/wiki/Traversal_Using_Relay_NAT
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._turnServers_node_(payload=payload, HTTPmethod='POST')

# # 	def __turnServers_turnServerId_node__(self, turn_server_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("turnServers/" + turn_server_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def modify_turn_server(self, turn_server_id, payload={}):
# # 		"""Modify an existing TURN server. TURN, in this context being Traversal Using Relay NAT

# # 		:param payload: Details the modified state of the TURN server
# # 		:type payload: Dict

# # 		:Example:
# # 			>>> print(a.create_turn_server(payload = {
# # 			>>>		"ServerAddress" : "192.168.12.50"
# # 			>>>	}))

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=72
# # 		.. seealso:: https://www.acano.com/publications/2013/08/Acano-solution-Deployment-Guide.pdf#page=50
# # 		.. seealso:: http://en.wikipedia.org/wiki/Traversal_Using_Relay_NAT
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self.__turnServers_turnServerId_node__(turn_server_id, payload=payload, HTTPmethod='PUT')

# # 	def get_turn_server(self, turn_server_id):
# # 		"""Return a TURN server, referenced by the TURN server ID. TURN, in this context being Traversal Using Relay NAT

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=72
# # 		.. seealso:: https://www.acano.com/publications/2013/08/Acano-solution-Deployment-Guide.pdf#page=50
# # 		.. seealso:: http://en.wikipedia.org/wiki/Traversal_Using_Relay_NAT
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self.__turnServers_turnServerId_node__(turn_server_id, HTTPmethod='GET')

# # 	#This one returns bad request when presented with a valid TURN server ID. Not sure why...
# # 	def get_turn_server_status(self, turn_server_id):
# # 		print("turnServers/" + turn_server_id + "/status")
# # 		return self._send_request("turnServers/" + turn_server_id + "/status", HTTPmethod='GET')

# # 	def _webBridges_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("webBridges", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_web_bridges(self, parameters={}):
# # 		"""Get information on Web Bridges

# # 		:param parameters: Details filters for the query
# # 		:type parameters: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=74
# # 		.. seealso:: https://www.acano.com/publications/2013/08/Acano-solution-Deployment-Guide.pdf#page=47
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._webBridges_node_(parameters=parameters, HTTPmethod='GET')

# # 	def create_web_bridge(self, payload={}):
# # 		"""Set up a new web bridge

# # 		:param payload: Details the initial state of the Web Bridge
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=75
# # 		.. seealso:: https://www.acano.com/publications/2013/08/Acano-solution-Deployment-Guide.pdf#page=47
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._webBridges_node_(payload=payload, HTTPmethod='POST')

# # 	def _webBridges_webBridgeID_node_(self, web_bridge_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("webBridges/" + web_bridge_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def modify_web_bridge(self, web_bridge_id, payload={}):
# # 		"""Modify an existing web bridge

# # 		:param web_bridge_id: The ID of the web bridge to modify.
# # 		:type web_bridge_id: String

# # 		:param payload: Details the new state of the Web Bridge
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=75
# # 		.. seealso:: https://www.acano.com/publications/2013/08/Acano-solution-Deployment-Guide.pdf#page=47
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._webBridges_webBridgeID_node_(web_bridge_id, payload=payload, HTTPmethod='PUT')

# # 	def get_web_bridge(self, web_bridge_id):
# # 		"""Get information for a specific web bridge, by ID

# # 		:param web_bridge_id: The ID of the web bridge for which to get information.
# # 		:type web_bridge_id: String

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=75
# # 		.. seealso:: https://www.acano.com/publications/2013/08/Acano-solution-Deployment-Guide.pdf#page=47
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._webBridges_webBridgeID_node_(web_bridge_id, parameters=parameters, HTTPmethod='GET')

# # 	def update_web_bridge_customization(self, web_bridge_id):
# # 		"""Reretrieve the configured customisation archive for the specified Web Bridge and push to memory.

# # 		:param web_bridge_id: The ID of the web bridge for which to get information.
# # 		:type web_bridge_id: String

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=76
# # 		.. seealso:: https://www.acano.com/publications/2013/08/Acano-solution-Deployment-Guide.pdf#page=47
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._send_request("webBridges/" + web_bridge_id + "/updateCustomization", HTTPmethod=POST)

# # 	def _callBridges_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("callBridges", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_call_bridges(self, parameters={}):
# # 		"""Get information on Call Bridges

# # 		:param parameters: Details filters for the query
# # 		:type parameters: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=76
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._callBridges_node_(parameters=parameters, HTTPmethod='GET')

# # 	def create_call_bridge(self, payload={}):
# # 		"""Set up a Call Bridge 

# # 		:param payload: Details the initial state of the call bridge
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=76
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._callBridges_node_(payload=payload, HTTPmethod='POST')

# # 	def _callBridges_callBridgeID_node_(self, call_bridge_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("callBridges/" + call_bridge_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def modify_call_bridge(self, call_bridge_id, payload={}):
# # 		"""Modify an existing Call Bridge 

# # 		:param call_bridge_id: The ID of the call bridge to modify
# # 		:type call_bridge_id: String

# # 		:param payload: Details the initial state of the call bridge
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=76
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._callBridges_callBridgeID_node_(call_bridge_id, payload=payload, HTTPmethod='PUT')

# # 	def get_call_bridge(self, call_bridge_id):
# # 		"""Get information on a specific call bridge

# # 		:param call_bridge_id: The ID of the call bridge to modify
# # 		:type call_bridge_id: String

# # 		:param payload: Details the initial state of the call bridge
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=76
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._callBridges_callBridgeID_node_(call_bridge_id, HTTPmethod='GET')

# # 	def _system_configuration_xmpp_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("system/configuration/xmpp", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_xmpp_server(self):
# # 		"""Get information on the XMPP server

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=77
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._system_configuration_xmpp_node_()

# # 	def create_xmpp_server(self, payload={}):
# # 		"""Set up the XMPP server

# # 		:param payload: The initial state of the XMPP server
# # 		:type payload: dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=77
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._system_configuration_xmpp_node_(payload=payload, HTTPmethod='POST')

# # 	def modify_xmpp_server(self, payload={}):
# # 		"""Modify the XMPP server details

# # 		:param payload: The new state of the XMPP server
# # 		:type payload: dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=77
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._system_configuration_xmpp_node_(payload=payload, HTTPmethod='PUT')

# # 	def _system_configuration_cluster_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("system/configuration/cluster", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_call_bridge_cluster(self):
# # 		"""Get information on the call bridge cluster

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=77
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._system_configuration_cluster_node_()

# # 	def create_call_bridge_cluster(self, payload={}):
# # 		"""Set up the call bridge cluster

# # 		:param payload: The initial state of the call bridge cluster
# # 		:type payload: dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=78
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._system_configuration_cluster_node_(payload=payload, HTTPmethod='POST')

# # 	def modify_call_bridge_cluster(self, payload={}):
# # 		"""Modify the existing call bridge cluster

# # 		:param payload: The new state of the call bridge cluster
# # 		:type payload: dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=78
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._system_configuration_cluster_node_(payload=payload, HTTPmethod='PUT')

# # 	def get_system_diagnostics(self):
# # 		"""Retrieve system diagnostics

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=78
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._send_request("system/diagnostics")

# # 	def get_system_diagnostic(self, diagnostic_id):
# # 		"""Retrieve an individual system diagnostic

# # 		:param diagnostic_id: The ID of the diagnostic to retrieve
# # 		:type diagnostic_id: String

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=79
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._send_request("system/diagnostics/" + diagnostic_id)

# # 	def get_system_diagnostic_contents(self, diagnostic_id):
# # 		"""Retrieve the contents of an individual system diagnostic

# # 		:param diagnostic_id: The ID of the diagnostic to retrieve
# # 		:type diagnostic_id: String

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=79
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._send_request("system/diagnostics/" + diagnostic_id + "/contents")

# # 	def _ldapServers_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("ldapServers", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_ldap_servers(self, parameters={}):
# # 		"""Retrieve information on LDAP servers

# # 		:param parameters: Details filters of the query
# # 		:type parameters: dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=79
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._ldapServers_node_(parameters=parameters)

# # 	def create_ldap_server(self, payload={}):
# # 		"""Add an LDAP server

# # 		:param payload: Details the initial state of the LDAP server
# # 		:type payload: dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=81
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._ldapServers_node_(payload=payload, HTTPmethod='POST')

# # 	def _ldapServers_ldapServerID_node_(self, ldap_server_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("ldapServers/" + ldap_server_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def modify_ldap_server(self, ldap_server_id, payload={}):
# # 		"""Modify an existing LDAP server

# # 		:param ldap_server_id: The ID of the LDAP server to modify
# # 		:type ldap_server_id: dict

# # 		:param payload: Details the new state of the LDAP server
# # 		:type payload: dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=81
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._ldapServers_ldapServerID_node_(ldap_server_id, payload=payload, HTTPmethod='PUT')

# # 	def get_ldap_server(self, ldap_server_id):
# # 		"""Get an LDAP server, by ID

# # 		:param ldap_server_id: The ID of the LDAP server to get
# # 		:type ldap_server_id: dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=81
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._ldapServers_ldapServerID_node_(ldap_server_id)

# # 	def _ldapMappings_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("ldapMappings", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_ldap_mappings(self):
# # 		"""Get LDAP mappings

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=84
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._ldapMappings_node_()

# # 	def create_ldap_mapping(self, payload={}):
# # 		"""Create an LDAP mapping

# # 		:param payload: Details the initial state of the LDAP mapping
# # 		:type payload: dict		

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=82
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._ldapMappings_node_(payload=payload, HTTPmethod='POST')

# # 	def _ldapMappings_ldapMappingID_node_(self, ldap_mapping_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("ldapMappings/" + ldap_mapping_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def modify_ldap_mapping(self, ldap_mapping_id, payload={}):
# # 		"""Modify an existing LDAP mapping

# # 		:param ldap_mapping_id: Details the new state of the LDAP mapping
# # 		:type ldap_mapping_id: String	

# # 		:param payload: Details the new state of the LDAP mapping
# # 		:type payload: dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=82
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._ldapMappings_ldapMappingID_node_(ldap_mapping_id, payload=payload, HTTPmethod='PUT')

# # 	def get_ldap_mapping(self, ldap_mapping_id):
# # 		"""Modify an existing LDAP mapping

# # 		:param ldap_mapping_id: Details the ID of the LDAP mapping to get
# # 		:type ldap_mapping_id: String	

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=84
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._ldapMappings_ldapMappingID_node_(ldap_mapping_id)

# # 	def _ldapSources_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("ldapSources", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_ldap_sources(self):
# # 		"""Get LDAP sources

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=84
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._ldapSources_node_()

# # 	def create_ldap_source(self, payload={}):
# # 		"""Create an LDAP source

# # 		:param payload: Details the initial state of the LDAP source
# # 		:type payload: Dict	

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=85
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._ldapSources_node_(payload={}, HTTPmethod='POST')

# # 	def _ldapSources_ldapSourceID_node_(self, ldap_source_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("ldapSources/" + ldap_source_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def modify_ldap_source(self, ldap_source_id, payload={}):
# # 		"""Modify an existing LDAP source

# # 		:param ldap_source_id: The ID of the LDAP source to modify
# # 		:type ldap_source_id: String	

# # 		:param payload: Details the initial state of the LDAP source
# # 		:type payload: Dict	

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=85
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._ldapSources_ldapSourceID_node_(ldap_source_id, payload=payload, HTTPmethod='PUT')

# # 	def get_ldap_source(self, ldap_source_id):
# # 		"""Get an LDAP source, by ID

# # 		:param ldap_source_id: The ID of the LDAP source to get
# # 		:type ldap_source_id: String	

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=85
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._ldapSources_ldapSourceID_node_(ldap_source_id)

# # 	def _ldapSyncs_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("ldapSyncs", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_ldap_syncs(self, parameters={}):
# # 		"""Monitor pending and in-progress LDAP syncs

# # 		:param parameters: Details filters for the query
# # 		:type parameters: Dict	

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=85
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._ldapSyncs_node_(parameters=parameters)

# # 	def initiate_ldap_sync(self, payload={}):
# # 		"""Trigger a new LDAP sync

# # 		:param parameters: Details parameters for the LDAP sync
# # 		:type parameters: Dict	

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=86
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._ldapSyncs_node_(payload=payload, HTTPmethod='POST')

# # 	def _ldapSyncs_ldapSyncID_node_(self, ldap_sync_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("ldapSyncs/" + ldap_sync_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def cancel_ldap_sync(self, ldap_sync_id):
# # 		"""Cancel a scheduled LDAP sync. Will fail if the sync has already started.

# # 		:param ldap_sync_id: The ID of the LDAP sync to cancel
# # 		:type ldap_sync_id: String	

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=86
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._ldapSyncs_ldapSyncID_node_(ldap_sync_id, HTTPmethod='delete'.upper())

# # 	def get_ldap_sync(self, ldap_sync_id, parameters={}):
# # 		"""Get information on a single LDAP sync

# # 		:param ldap_sync_id: The ID of the LDAP sync to cancel
# # 		:type ldap_sync_id: String	

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=86
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._ldapSyncs_ldapSyncID_node_(ldap_sync_id, parameters=parameters)

# # 	def _directorySearchLocations_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("directorySearchLocations", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_directory_search_locations(self):
# # 		"""Get information on external directory search locations: additional directory search locations to be consulted when users of Acano clients perform searches

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=87
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._directorySearchLocations_node_()

# # 	def create_directory_search_location(self, payload={}):
# # 		"""Add an external directory search location

# # 		:param payload: Details the initial state of the directory search location
# # 		:type payload: Dict			

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=88
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._directorySearchLocations_node_(payload=payload, HTTPmethod='POST')

# # 	def _directorySearchLocations_directorySearchLocationID_node_(self, directory_search_location_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("directorySearchLocations/" + directory_search_location_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def modify_directory_search_location(self, directory_search_location_id, payload={}):
# # 		"""Modify an existing external directory search location

# # 		:param directory_search_location_id: The ID of the directory search location to modify
# # 		:type directory_search_location_id: String	

# # 		:param payload: Details the new state of the directory search location
# # 		:type payload: Dict			

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=88
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._directorySearchLocations_directorySearchLocationID_node_(directory_search_location_id, payload=payload, HTTPmethod='PUT')

# # 	def get_directory_search_location(self, directory_search_location_id):
# # 		"""Get a single external directory search location

# # 		:param directory_search_location_id: The ID of the directory search location to get
# # 		:type directory_search_location_id: String		

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=88
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._directorySearchLocations_directorySearchLocationID_node_(directory_search_location_id)

# # 	def _tenants_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("tenants", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_tenants(self, parameters={}):
# # 		"""Retrieve tenants in the system

# # 		:param parameters: Details filters for the query
# # 		:type parameters: Dict		

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=93
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._tenants_node_(parameters=parameters)

# # 	def create_tenant(self, payload={}):
# # 		"""Create a new tenant

# # 		:param payload: Details the initial state of the tenant
# # 		:type payload: Dict		

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=94
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._tenants_node_(payload=payload, HTTPmethod='POST')

# # 	def _tenants_tenantID_node_(self, tenant_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("tenants/" + tenant_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def modify_tenant(self, tenant_id, payload={}):
# # 		"""Modify an existing tenant

# # 		:param tenant_id: The ID of the tenant to modify
# # 		:type tenant_id: String

# # 		:param payload: Details the new state of the tenant
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=94
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._tenants_tenantID_node_(tenant_id, payload=payload, HTTPmethod='PUT')

# # 	def get_tenant(self, tenant_id):
# # 		"""Get a single tenant

# # 		:param tenant_id: The ID of the tenant to get
# # 		:type tenant_id: String

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=94
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._tenants_tenantID_node_(tenant_id)

# # 	def _tenantGroups_node_(self,  parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("tenantGroups", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_tenant_groups(self, parameters={}):
# # 		"""Retrieve tenant groups in the system.

# # 		:param parameters: Details filters for the query
# # 		:type parameters: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=94
# # 		.. seealso:: https://www.acano.com/publications/2015/09/Acano-Solution-Multi-tenancy-Considerations1.pdf#page=6
# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._tenantGroups_node_(parameters={})

# # 	def create_tenant_group(self, payload={}):
# # 		"""Create a tenant group.

# # 		:param payload: Details the initial state of the tenant
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=95
# # 		.. seealso:: https://www.acano.com/publications/2015/09/Acano-Solution-Multi-tenancy-Considerations1.pdf#page=6
# # 		.. note:: v1.8 upward
# # 		"""

# # 		return self._tenantGroups_node_(payload=payload, HTTPmethod='POST')

# # 	def _tenantGroups_tenantGroupID_node_(self, tenant_group_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("tenantGroups/" + tenant_group_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def modify_tenant_group(self, tenant_group_id, payload={}):
# # 		"""Modify an existing tenant group

# # 		:param tenant_group_id: The ID of the tenant group to modify
# # 		:type tenant_group_id: String

# # 		:param payload: Details the new state of the tenant group
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=94
# # 		.. seealso:: https://www.acano.com/publications/2015/09/Acano-Solution-Multi-tenancy-Considerations1.pdf#page=6

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._tenantGroups_tenantGroupID_node_(tenant_group_id, payload=payload, HTTPmethod='PUT')

# # 	def get_tenant_group(self, tenant_group_id):
# # 		"""Retrieve a single existing tenant group

# # 		:param tenant_group_id: The ID of the tenant group to get
# # 		:type tenant_group_id: String

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=94
# # 		.. seealso:: https://www.acano.com/publications/2015/09/Acano-Solution-Multi-tenancy-Considerations1.pdf#page=6

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._tenantGroups_tenantGroupID_node_(tenant_group_id, HTTPmethod='GET')

# # 	def create_access_query(self, payload={}):
# # 		"""The accessQuery method finds details of how a given URI or call ID (for example, one that could
# # 			be associated with a coSpace) might be reached. One use is an external system discovering
# # 			that a coSpace with URI "sales.meeting" would be reached via the SIP URI
# # 			"sales.meeting@example.com".

# # 		:param payload: Details the query
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=96

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._send_request(payload=payload, HTTPmethod='POST')

# # 	def _coSpaces_coSpaceID_accessMethods_node_(self, coSpace_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("coSpaces/" + coSpace_id + "/accessMethods", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_coSpace_access_methods(self, coSpace_id, parameters={}):
# # 		"""Retrieve the access methods for a coSpace. Access methods define URI / passcode / callID combinations that can be used to access
# # a coSpace

# # 		:param coSpace_id: The ID of the coSpace for which to retrieve access methods
# # 		:type coSpace_id: String

# # 		:param parameters: Details filters for the query
# # 		:type parameters: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=32

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._coSpaces_coSpaceID_accessMethods_node_(coSpace_id, parameters=parameters)

# # 	def create_coSpace_access_method(self, coSpace_id, payload={}):
# # 		"""Create a new access method for a coSpace. Access methods define URI / passcode / callID combinations that can be used to access
# # a coSpace

# # 		:param coSpace_id: The ID of the coSpace for which to add an access method
# # 		:type coSpace_id: String

# # 		:param payload: Details the initial state of the access method
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=32

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._coSpaces_coSpaceID_accessMethods_node_(coSpace_id, payload=payload, HTTPmethod='POST')

# # 	def _coSpaces_coSpaceID_accessmethods_accessMethodID_node_(self, coSpace_id, access_method_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("coSpaces/" + coSpace_id + "/accessMethods/" + access_method_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def modify_coSpace_access_method(self, coSpace_id, access_method_id, payload={}):
# # 		"""Modify an existing access method for a coSpace. Access methods define URI / passcode / callID combinations that can be used to access
# # a coSpace

# # 		:param coSpace_id: The ID of the coSpace in which to modify an access method
# # 		:type coSpace_id: String

# # 		:param access_method_id: The ID of the access method to modify.
# # 		:type access_method_id: String		

# # 		:param payload: Details the new state of the access method
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=33

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._coSpaces_coSpaceID_accessmethods_accessMethodID_node_(coSpace_id, access_method_id, payload=payload, HTTPmethod='PUT')

# # 	def get_coSpace_access_method(self, coSpace_id, access_method_id):
# # 		"""Retrieve a single access method for a coSpace. Access methods define URI / passcode / callID combinations that can be used to access
# # a coSpace

# # 		:param coSpace_id: The ID of the coSpace in which to get an access method
# # 		:type coSpace_id: String

# # 		:param access_method_id: The ID of the access method to get.
# # 		:type access_method_id: String		

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=33

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._coSpaces_coSpaceID_accessmethods_accessMethodID_node_(self, coSpace_id, access_method_id, HTTPmethod='GET')

# # 	#Generates bad request. Not sure why...

# # 	def _create_coSpace_diagnostics_(self, coSpace_id):
# # 		return self._send_request("coSpaces/" + coSpace_id + "/diagnostics", HTTPmethod='POST')

# # 	def _outboundDialPlanRules_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("outboundDialPlanRules", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_outbound_dial_plan_rules(self, parameters={}):
# # 		"""Retrieve outbound dial plan rules. 

# # 		:param parameters: Details filters for the query
# # 		:type parameters: Dict	

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=35

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._outboundDialPlanRules_node_(parameters=parameters)

# # 	def create_outbound_dial_plan_rule(self, payload={}):
# # 		"""Create a new outbound dial plan rule.

# # 		:param payload: Details the initial state of the dial plan rule.
# # 		:type payload: Dict	

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=35

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._outboundDialPlanRules_node_(payload={}, HTTPmethod='POST')

# # 	def _outboundDialPlanRules_outboundDialPlanRuleID_node_(self, outbound_dial_plan_rule_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("outboundDialPlanRules/" + outbound_dial_plan_rule_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def modify_outbound_dial_plan_rule(self, outbound_dial_plan_rule_id, payload={}):
# # 		"""Create a new outbound dial plan rule.
        
# # 		:param outbound_dial_plan_rule_id: The ID of the dial plan rule to modify
# # 		:type outbound_dial_plan_rule_id: String

# # 		:param payload: Details the new state of the dial plan rule.
# # 		:type payload: Dict	

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=35

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._outboundDialPlanRules_outboundDialPlanRuleID_node_(outbound_dial_plan_rule_id, payload=payload, HTTPmethod='PUT')

# # 	def get_outbound_dial_plan_rule(self, outbound_dial_plan_rule_id):
# # 		"""Retrieve a single outbound dial plan rule
        
# # 		:param outbound_dial_plan_rule_id: The ID of the dial plan rule to retrieve
# # 		:type outbound_dial_plan_rule_id: String

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=35

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._outboundDialPlanRules_outboundDialPlanRuleID_node_(outbound_dial_plan_rule_id)

# # 	def _inboundDialPlanRules_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("inboundDialPlanRules", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_inbound_dial_plan_rules(self, parameters={}):
# # 		"""Retrieve inbound dial plan rules. 

# # 		:param parameters: Details filters for the query
# # 		:type parameters: Dict	

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=37

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._inboundDialPlanRules_node_(parameters=parameters)

# # 	def create_inbound_dial_plan_rule(self, payload={}):
# # 		"""Create a new inbound dial plan rule.

# # 		:param payload: Details the initial state of the dial plan rule.
# # 		:type payload: Dict	

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=37

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._inboundDialPlanRules_node_(payload={}, HTTPmethod='POST')

# # 	def _inboundDialPlanRules_inboundDialPlanRuleID_node_(self, inbound_dial_plan_rule_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("inboundDialPlanRules/" + inbound_dial_plan_rule_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def modify_inbound_dial_plan_rule(self, inbound_dial_plan_rule_id, payload={}):
# # 		"""Create a new inbound dial plan rule.
        
# # 		:param inbound_dial_plan_rule_id: The ID of the dial plan rule to modify
# # 		:type inbound_dial_plan_rule_id: String

# # 		:param payload: Details the new state of the dial plan rule.
# # 		:type payload: Dict	

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=35

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._inboundDialPlanRules_inboundDialPlanRuleID_node_(inbound_dial_plan_rule_id, payload=payload, HTTPmethod='PUT')

# # 	def get_inbound_dial_plan_rule(self, inbound_dial_plan_rule_id, parameters={}):
# # 		"""Retrieve a single inbound dial plan rule. 
        
# # 		:param inbound_dial_plan_rule_id: The ID of the dial plan rule to retrieve
# # 		:type inbound_dial_plan_rule_id: String

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=37

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._inboundDialPlanRules_inboundDialPlanRuleID_node_(inbound_dial_plan_rule_id, parameters=parameters)

# # 	def _forwardingDialPlanRules_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("forwardingDialPlanRules", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_forwarding_dial_plan_rules(self, parameters={}):
# # 		"""Retrieve the forwarding dial plan rules. 
        
# # 		:param parameters: Details filters for the query
# # 		:type parameters: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=38
# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=39

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._forwardingDialPlanRules_node_(parameters)

# # 	def create_forwarding_dial_plan_rule(self, payload={}):
# # 		"""Create a new forwarding dial plan rule. 
        
# # 		:param payload: Details the initial state of the rule
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=38
# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=39

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._forwardingDialPlanRules_node_(payload=payload, HTTPmethod='POST')

# # 	def _forwardingDialPlanRules_forwardingDialPlanRuleID_node_(self, forwarding_dial_plan_rule_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("forwardingDialPlanRules/" + forwarding_dial_plan_rule_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def modify_forwarding_dial_plan_rule(self, forwarding_dial_plan_rule_id, payload={}):
# # 		"""Modify an existing forwarding dial plan rule. 
        
# # 		:param forwarding_dial_plan_rule_id: The ID of the rule to modify
# # 		:type forwarding_dial_plan_rule_id: Dict

# # 		:param payload: Details the new state of the rule
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=38
# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=39

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._forwardingDialPlanRules_forwardingDialPlanRuleID_node_(forwarding_dial_plan_rule_id, payload=payload, HTTPmethod='PUT')

# # 	def get_forwarding_dial_plan_rule(self, forwarding_dial_plan_rule_id):
# # 		"""Retrieve a single forwarding dial plan rule. 
        
# # 		:param forwarding_dial_plan_rule_id: The ID of the rule to modify
# # 		:type forwarding_dial_plan_rule_id: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=38
# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=40

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._forwardingDialPlanRules_forwardingDialPlanRuleID_node_(forwarding_dial_plan_rule_id)

# # 	def _calls_node(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("calls", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_calls(self, parameters={}):
# # 		"""Retrieve information on active calls

# # 		:param parameters: Details filters for the query
# # 		:type parameters: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=41

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._calls_node(parameters=parameters)

# # 	def create_call(self, payload={}):
# # 		"""Create a new call

# # 		:param payload: Details of the call
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=41

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._calls_node(payload=payload, HTTPmethod='POST')

# # 	def _calls_callID_node(self, call_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("calls/" + call_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_call(self, call_id):
# # 		"""Retrieve information on a single active call

# # 		:param call_id: The ID of the call for which to retrieve information
# # 		:type call_id: String

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=42

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._calls_callID_node(call_id)

# # 	def delete_call(self, call_id):
# # 		"""Cancel an in-progress call

# # 		:param call_id: The ID of the call
# # 		:type call_id: String

# # 		"""
# # 		return self._calls_callID_node(call_id, HTTPmethod="delete".upper())

# # 	def _callProfiles_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("callProfiles", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_call_profiles(self, parameters={}):
# # 		"""Retrieve information on call profiles

# # 		:param parameters: Details filters for the query
# # 		:type parameters: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=97
# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=42

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._callProfiles_node_(parameters=parameters)

# # 	def create_call_profile(self, payload={}):
# # 		"""Create a new call profile

# # 		:param payload: Details the initial state of the call profile
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=97
# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=43

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._callProfiles_node_(payload=payload, HTTPmethod='POST')

# # 	def _callProfiles_callProfileID_node(self, call_profile_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("callProfiles/" + call_profile_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def modify_call_profile(self, call_profile_id, payload={}):
# # 		"""Modify an existing call profile

# # 		:param call_profile_id: The ID of the call profile to modify
# # 		:type call_profile_id: String

# # 		:param payload: Details the new state of the call profile
# # 		:type payload: Dict		

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=97
# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=43

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._callProfiles_callProfileID_node(call_profile_id, payload=payload, HTTPmethod='PUT')

# # 	def get_call_profile(self, call_profile_id):
# # 		"""Retrieve information on a single call profile

# # 		:param call_profile_id: The ID of the call profile to modify
# # 		:type call_profile_id: String

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=97
# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=43

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._callProfiles_callProfileID_node(call_profile_id)

# # 	def _callLegs_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("callLegs", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_call_legs(self, parameters={}):
# # 		"""Retrieve information on call legs

# # 		:param parameters: Details filter for the query
# # 		:type parameters: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=43

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._callLegs_node_(parameters=parameters)

# # 	def create_call_leg(self, call_id, payload={}):
# # 		"""Create a new call leg

# # 		:param call_id: The ID of the call for which to create the call leg
# # 		:type call_id: String

# # 		:param payload: Details the initial state of the call leg
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=45

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._send_request("calls/" + call_id + "/callLegs", payload=payload, HTTPmethod='POST')

# # 	def _callLegs_callLegID_node_(self, call_leg_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("callLegs/" + call_leg_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def modify_call_leg(self, call_leg_id, payload={}):
# # 		"""Modify an existing call leg

# # 		:param call_leg_id: The ID of the call leg to modify
# # 		:type call_leg_id: String

# # 		:param payload: Details the new state of the call leg
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=45

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._callLegs_callLegID_node_(call_leg_id, payload=payload, HTTPmethod='PUT')

# # 	def get_call_leg(self, call_leg_id):
# # 		"""Retrieve information on a single call leg.

# # 		:param call_leg_id: The ID of the call leg to get
# # 		:type call_leg_id: String

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=47

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._callLegs_callLegID_node_(call_leg_id)

# # 	def _callLegProfiles_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("callLegProfiles", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_call_leg_profiles(self, parameters={}):
# # 		"""Retrieve information on call leg profiles

# # 		:param parameters: Details filters for the query
# # 		:type parameters: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=48

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._callLegProfiles_node_(parameters=parameters)

# # 	def create_call_leg_profile(self, payload={}):
# # 		"""Create a new call leg profile

# # 		:param payload: Details the initial state of the call leg profile
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=49

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._callLegProfiles_node_(payload=payload, HTTPmethod='POST')

# # 	def _callLegProfiles_callLegProfileID_node_(self, call_leg_profile_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("callLegProfiles/" + call_leg_profile_id, parameters={}, payload={}, HTTPmethod=HTTPmethod)

# # 	def modify_call_leg_profile(self, call_leg_profile_id, payload={}):
# # 		"""Modify an existing call leg profile

# # 		:param call_leg_profile_id: The ID of the call leg profile to modify
# # 		:type call_leg_profile_id: String		

# # 		:param payload: Details the new state of the call leg profile
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=49

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._callLegProfiles_callLegProfileID_node_(call_leg_profile_id, payload=payload, HTTPmethod='PUT')

# # 	def get_call_leg_profile(self, call_leg_profile_id):
# # 		"""Retrieve information on a single call leg profile

# # 		:param call_leg_profile_id: The ID of the call leg profile to get
# # 		:type call_leg_profile_id: String		

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=51

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._callLegProfiles_callLegProfileID_node_(call_leg_profile_id)

# # 	def get_call_leg_profile_trace(self, call_leg_id, parameters={}):
# # 		"""Retrieve information on a call leg profile trace

# # 		:param call_leg_id: The ID of the call leg to get
# # 		:type call_leg_id: String

# # 		:param parameters: Details filters for the query
# # 		:type parameters: Dict		

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=52

# # 		.. note:: v1.8 upward
# # 		"""
# # 		return self._send_request("callLegs/" + call_leg_profile_id + "/callLegProfileTrace", parameters=parameters)

# # 	def _dialTransforms_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("dialTransforms", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_dial_transforms(self, parameters={}):
# # 		"""Retrieve information on transforms set up for outbound calls.

# # 		:param call_leg_id: The ID of the call leg to get
# # 		:type call_leg_id: String

# # 		:param parameters: Details filters for the query
# # 		:type parameters: Dict		

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=54
# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=55


# # 		.. note:: v1.6 upward
# # 		"""
# # 		return self._dialTransforms_node_(parameters=parameters)

# # 	def create_dial_transform(self, payload={}):
# # 		"""Create a new dial transform for outbound calls

# # 		:param payload: Details the initial state of the dial transform
# # 		:type payload: Dict		

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=54
# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=55


# # 		.. note:: v1.6 upward
# # 		"""
# # 		return self._dialTransforms_node_(payload=payload, HTTPmethod='POST')

# # 	def _dialTransforms_dialTransformID_node_(self, dial_transform_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("dialTransforms/" + dial_transform_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def modify_dial_transform(self, dial_transform_id, payload={}):
# # 		"""Modify an existing dial transform

# # 		:param dial_transform_id: The ID of the dial transform to modify
# # 		:type dial_transform_id: String			

# # 		:param payload: Details the initial state of the dial transform
# # 		:type payload: Dict		

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=54
# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=55


# # 		.. note:: v1.6 upward
# # 		"""
# # 		return self._dialTransforms_dialTransformID_node_(dial_transform_id, payload=payload, HTTPmethod='PUT')

# # 	def get_dial_transform(self, dial_transform_id):
# # 		"""Retrieve information on a single dial transform

# # 		:param dial_transform_id: The ID of the dial transform to get
# # 		:type dial_transform_id: String				

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=54
# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=56


# # 		.. note:: v1.6 upward
# # 		"""
# # 		return self._dialTransforms_dialTransformID_node_(dial_transform_id)

# # 	def _callBrandingProfiles_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("callBrandingProfiles", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_call_branding_profiles(self, parameters={}):
# # 		"""Retrieve information on call branding profiles

# # 		:param parameters: Details filters for the query
# # 		:type parameters: Dict				

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=57

# # 		.. note:: v1.6 upward
# # 		"""
# # 		return self._callBrandingProfiles_node_(parameters=parameters)

# # 	def create_call_branding_profile(self, payload={}):
# # 		"""Create a call branding profile

# # 		:param payload: Details the initial state of the call branding profile.
# # 		:type payload: Dict				

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=57
        
# # 		.. note:: v1.6 upward
# # 		"""
# # 		return self._callBrandingProfiles_node_(payload=payload, HTTPmethod='POST')

# # 	def _callBrandingProfiles_callBrandingProfileID_node(self, call_branding_profile_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("callBrandingProfiles/" + call_branding_profile_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def modify_call_branding_profile(self, call_branding_profile_id, payload={}):
# # 		"""Modify an existing call branding profile

# # 		:param call_branding_profile_id: The ID of the call branding profile to modify
# # 		:type call_branding_profile_id: String		

# # 		:param payload: Details the new state of the call branding profile.
# # 		:type payload: Dict				

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=57
        
# # 		.. note:: v1.6 upward
# # 		"""
# # 		return self._callBrandingProfiles_callBrandingProfileID_node(call_branding_profile_id, payload=payload, HTTPmethod='PUT')

# # 	def get_call_branding_profile(self, call_branding_profile_id):
# # 		"""Retrieve information on a single call branding profile

# # 		:param call_branding_profile_id: The ID of the call branding profile to get
# # 		:type call_branding_profile_id: String					

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=58
        
# # 		.. note:: v1.6 upward
# # 		"""
# # 		return self._callBrandingProfiles_callBrandingProfileID_node(call_branding_profile_id)

# # 	def _dtmfProfiles_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("dtmfProfiles", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_dtmf_profiles(self, parameters={}):
# # 		"""Create a new DTMF profile	

# # 		:param parameters: Details filters for the query
# # 		:type parameters: Dict				

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=58
# # 		.. seealso:: https://en.wikipedia.org/wiki/Dual-tone_multi-frequency_signaling
        
# # 		.. note:: v1.6 upward
# # 		"""
# # 		return self._dtmfProfiles_node_(parameters=parameters)

# # 	def create_dtmf_profile(self, payload={}):
# # 		"""Create a DTMF profile	

# # 		:param payload: Details the initial state of the DTMF profile
# # 		:type payload: Dict				

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=59
# # 		.. seealso:: https://en.wikipedia.org/wiki/Dual-tone_multi-frequency_signaling
        
# # 		.. note:: v1.6 upward
# # 		"""
# # 		return self._dtmfProfiles_node_(payload=payload, HTTPmethod='POST')

# # 	def _dtmfProfiles_dtmfProfileID_node_(self, dtmf_profile_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("dtmfProfiles/" + dtmf_profile_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def modify_dtmf_profile(self, dtmf_profile_id, payload={}):
# # 		"""Modify a DTMF profile	

# # 		:param dtmf_profile_id: The ID of the DTMF profile to modify
# # 		:type dtmf_profile_id: String

# # 		:param payload: Details the new state of the DTMF profile
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=59
# # 		.. seealso:: https://en.wikipedia.org/wiki/Dual-tone_multi-frequency_signaling
        
# # 		.. note:: v1.6 upward
# # 		"""
# # 		return self._dtmfProfiles_dtmfProfileID_node_("dtmfProfiles/" + dtmf_profile_id, payload=payload, HTTPmethod='PUT')

# # 	def get_dtmf_profile(self, dtmf_profile_id):
# # 		"""Retrieve information on a single DTMF profile

# # 		:param dtmf_profile_id: The ID of the DTMF profile to get
# # 		:type dtmf_profile_id: String

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=59
# # 		.. seealso:: https://en.wikipedia.org/wiki/Dual-tone_multi-frequency_signaling
        
# # 		.. note:: v1.6 upward
# # 		"""
# # 		return self._dtmfProfiles_dtmfProfileID_node_(dtmf_profile_id)

# # 	def _ivrs_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("ivrs", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_ivrs(self, parameters={}):
# # 		"""Retrieve information on IVRs

# # 		:param parameters: Details filters for the query
# # 		:type parameters: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=59
# # 		.. seealso:: https://en.wikipedia.org/wiki/Interactive_voice_response
        
# # 		"""
# # 		return self._ivrs_node_(parameters=parameters)

# # 	def create_ivr(self, payload={}):
# # 		"""Create a new IVR

# # 		:param payload: Details the initial state of the IVR
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=60
# # 		.. seealso:: https://en.wikipedia.org/wiki/Interactive_voice_response
        
# # 		"""
# # 		return self._ivrs_node_(payload=payload, HTTPmethod='POST')

# # 	def _ivrs_ivrID_node(self, ivr_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("ivrs/" + ivr_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def modify_ivr(self, ivr_id, payload={}):
# # 		"""Modify an existing IVR

# # 		:param ivr_id: The ID of the IVR to modify
# # 		:type ivr_id: String		

# # 		:param payload: Details the new state of the IVR
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=60
# # 		.. seealso:: https://en.wikipedia.org/wiki/Interactive_voice_response
        
# # 		"""
# # 		return self._ivrs_ivrID_node(ivr_id, payload=payload, HTTPmethod='PUT')

# # 	def get_ivr(self, ivr_id):
# # 		"""Retrieve information on a single IVR

# # 		:param ivr_id: The ID of the IVR to get
# # 		:type ivr_id: String		

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=60
# # 		.. seealso:: https://en.wikipedia.org/wiki/Interactive_voice_response
        
# # 		"""
# # 		return self._ivrs_ivrID_node(ivr_id)

# # 	def _ivrBrandingProfiles_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("ivrBrandingProfiles", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_ivr_branding_profiles(self, parameters={}):
# # 		"""Retrieve information IVR branding profiles

# # 		:param parameters: Details filters for the query
# # 		:type parameters: Dict		

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=61	
# # 		"""
# # 		return self._ivrBrandingProfiles_node_(parameters={})

# # 	def create_ivr_branding_profile(self, payload={}):
# # 		"""Create a new IVR branding profile

# # 		:param payload: Details the initial state of the profile
# # 		:type payload: Dict		

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=61	
# # 		"""
# # 		return self._ivrBrandingProfiles_node_(payload=payload, HTTPmethod='POST')

# # 	def _ivrBrandingProfiles_ivrBrandingProfileID_node_(self, ivr_branding_profile_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("ivrBrandingProfiles/" + ivr_branding_profile_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def modify_ivr_branding_profile(self, ivr_branding_profile_id, payload={}):
# # 		"""Modify an existing IVR branding profile

# # 		:param ivr_branding_profile_id: The ID of the IVR branding profile to modify
# # 		:type ivr_branding_profile_id: String	

# # 		:param payload: Details the new state of the profile
# # 		:type payload: Dict		

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=61	
# # 		"""
# # 		return self._ivrBrandingProfiles_ivrBrandingProfileID_node_(ivr_branding_profile_id, payload=payload, HTTPmethod='PUT')

# # 	def get_ivr_branding_profile(self, ivr_branding_profile_id):
# # 		"""Retrieve information on a single IVR branding profile

# # 		:param ivr_branding_profile_id: The ID of the IVR branding profile to get
# # 		:type ivr_branding_profile_id: String	

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=61	
# # 		"""
# # 		return self._ivrBrandingProfiles_ivrBrandingProfileID_node_(ivr_branding_profile_id)

# # 	def _participants_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("participants", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_participants(self, parameters={}):
# # 		"""Get information on participants

# # 		:param parameters: Details filters for the query
# # 		:type parameters: Dict	

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=61
# # 		"""
# # 		return self._participants_node_(parameters=parameters)

# # 	def _participants_participantID_node_(self, participant_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("participants/" + participant_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_participant(self, participant_id):
# # 		"""Get information on a participant

# # 		:param participant_id: The ID of the participant to get
# # 		:type participant_id: String		

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=62
# # 		"""
# # 		return self._participants_participantID_node_(participant_id)

# # 	def get_participant_call_legs(self, participant_id):
# # 		"""Get information on a participant's call legs

# # 		:param participant_id: The ID of the participant for which to get call legs
# # 		:type participant_id: String		

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=63
# # 		"""
# # 		return self._send_request("participant/" + participant_id + "callLegs", HTTPmethod='GET')

# # 	def _users_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("users", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_users(self, parameters={}):
# # 		"""Get information on users

# # 		:param parameters: Details filters for the query
# # 		:type parameters: Dict		

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=65
# # 		"""
# # 		return self._users_node_(parameters=parameters)

# # 	def _users_userID_node_(self, user_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("users/" + user_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_user(self, user_id):
# # 		"""Get information on a single user

# # 		:param user_id: The ID of the user
# # 		:type user_id: String		

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=65
# # 		"""
# # 		return self._users_userID_node_(user_id)

# # 	def _users_userID_usercoSpaces_node_(self, user_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("users/" + user_id + "/usercoSpaces", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_user_coSpaces(self, user_id):
# # 		"""Get information on the coSpaces with which a user is currently associated

# # 		:param user_id: The ID of the user
# # 		:type user_id: String		

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=65
# # 		"""
# # 		return self._users_userID_usercoSpaces_node_(user_id)

# # 	def _recorders_node_(self, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("recorders", parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def get_recorders(self, parameters={}):
# # 		"""Get information on meeting recorders

# # 		:param parameters: Details filters for the query
# # 		:type parameters: Dict		

# # 		.. seealso:: https://www.acano.com/publications/2016/06/Solution-API-Reference-R1_9.pdf#page=105

# # 		.. note:: v1.9 upward
# # 		"""
# # 		return self._recorders_node_(parameters=parameters)

# # 	def create_recorder(self, payload={}):
# # 		"""Create a meeting recorder

# # 		:param payload: Details the initial state of the recorder
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=106

# # 		.. note:: v1.9 upward
# # 		"""
# # 		return self._recorders_node_(payload=payload, HTTPmethod='POST')

# # 	def _recorders_recorderid_node(self, recorder_id, parameters={}, payload={}, HTTPmethod='GET'):
# # 		return self._send_request("recorders/" + recorder_id, parameters=parameters, payload=payload, HTTPmethod=HTTPmethod)

# # 	def modify_recorder(self, recorder_id, payload={}):
# # 		"""Modify an existing meeting recorder

# # 		:param recorder_id: The ID of the recorder to modify
# # 		:type recorder_id: String

# # 		:param payload: Details the new state of the recorder
# # 		:type payload: Dict

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=106

# # 		.. note:: v1.9 upward
# # 		"""
# # 		return self._recorders_recorderid_node(recorder_id, payload=payload, HTTPmethod='PUT')

# # 	def get_recorder(self, recorder_id):
# # 		"""Get information on a single recorder

# # 		:param recorder_id: The ID of the recorder to get
# # 		:type recorder_id: String

# # 		.. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=106

# # 		.. note:: v1.9 upward
# # 		"""
# # 		return self._recorders_recorderid_node(recorder_id)
