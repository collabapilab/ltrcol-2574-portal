import json
import xmltodict
import xml.parsers.expat
from flaskr.rest.v1.rest import REST
from base64 import b64encode


class CMS(REST):
    '''
    The CMS Server class

    Use this class to connect and make API calls to an most Cisco Meeting Server devices.

    :param host: The Hostname / IP Address of the server
    :param username: The username of an account with access to the API.
    :param password: The password for your user account
    :param port: (optional) The server port for API access (default: 443)
    :type host: String
    :type username: String
    :type password: String
    :type port: Integer
    :returns: return an CMS object
    :rtype: CMS
    '''

    def __init__(self, host, username, password, port=443, tls_verify=False):
        '''
        Initialize the CMS class as a child of the REST class. Define the CMS-specific headers, and API base_url
        '''
        # Define the header structure for CMS. CMS returns text/xml and except for the layoutTemplates,
        # requires Content-Type to be x-www-form-urlencoded
        headers = {
            'Accept': 'text/xml',
            'Content-Type': 'x-www-form-urlencoded'
        }

        # Create a super class, where the CMS class inherits from the REST class.
        super().__init__(host, username, password, base_url='/api/v1',
                         headers=headers, port=port, tls_verify=tls_verify)

        # CMS documents its error codes in its API documentation. We have simply converted it to a dict
        self.error_codes = {
            "accessMethodDoesNotExist": "You tried to modify or remove an accessMethod using an ID that did not correspond to a valid access method",
            "callBrandingProfileDoesNotExist": "You tried to modify or remove a call branding profile using an ID that did not correspond to a valid call branding profile",
            "callBridgeDoesNotExist": "You tried to modify or remove a configured clustered Call Bridge using an ID that did not correspond to a valid clustered Call Bridge",
            "callDoesNotExist": "You tried to perform a method on a call object using an ID that did not correspond to a currently active call",
            "callRecordingCannotBeModified": "You tried to start/stop recording a call that cannot be modified. Present from R1.9",
            "callLegCannotBeDeleted": "You tried to delete a call leg that can't be deleted. Present from R1.8",
            "callLegDoesNotExist": "You tried to perform a method on a call leg object using an ID that did not correspond to a currently active call leg",
            "callLegProfileDoesNotExist": "You tried to modify or remove a callLegProfile using an ID that did not correspond to a valid call leg profile",
            "callProfileDoesNotExist": "You tried to modify or remove a callProfile using an ID that is not valid",
            "cdrReceiverDoesNotExist": "You tried to modify or remove a CDR receiver using an ID that did not correspond to a valid CDR receiver. Present from R1.8",
            "coSpaceDoesNotExist": "You tried to modify or remove a coSpace using an ID that did not correspond to a valid coSpace on the system",
            "coSpaceUserDoesNotExist": "You tried to modify or remove a coSpace user using an ID that did not correspond to a valid coSpace user",
            "databaseNotReady": "You tried a method (e.g. initiation of an LDAP sync method) before the database was ready",
            "directorySearchLocationDoesNotExist": " You tried to reference, modify or remove a directory search location using an ID that did not correspond to a valid directory search location. Present from R1.8",
            "dtmfProfileDoesNotExist": " You tried to reference, modify or remove a DTMF profile using an ID that did not correspond to a valid DTMF profile",
            "duplicateCallBridgeName": "You tried to create or modify a clustered Call Bridge to use a name that would clash with an existing configured clustered Call Bridge",
            "duplicateCoSpaceId": "You tried to create or modify a coSpace call ID to use a call ID that clashed with one used by another coSpace",
            "duplicateCoSpaceUri": " You tried to create or modify a coSpace to use a URI that clashed with one that corresponds to another coSpace. (Two coSpaces can't share the same URI, because the Meeting Server must be able to uniquely resolve an incoming call to a coSpace URI)",
            "duplicateCoSpaceSecret": " You tried to modify a coSpace, or create or modify a coSpace access method, using a secret that clashed with one that is already used by that coSpace or one of its access methods",
            "forwardingDialPlanRuleDoesNotExist": "You tried to modify or remove an forwarding dial plan rule using an ID that did not correspond to a valid forwarding dial plan rule",
            "inboundDialPlanRuleDoesNotExist": "You tried to modify or remove an inbound dial plan rule using an ID that did not correspond to a valid inbound dial plan rule",
            "inboundDialPlanRuleUriConflict": " You tried to make modifications to an inbound dial plan rule which would have caused a URI conflict. For example, this can happen if you try to add a rule which matches multiple tenants and more than one tenant has a coSpace with the same URI",
            "invalidOperation": " You tried an operation which isn't supported; for example, you attempted to POST to /api/v1/system/profiles or issue a DELETE for a configured user generated from an LDAP sync",
            "invalidVersion": "You attempted an operation with an invalid API version. Present from R1.8",
            "ivrBrandingProfileDoesNotExist": "You tried to modify or remove an IVR branding profile object using an ID that did not correspond to a valid IVR branding profile on the system",
            "ivrDoesNotExist": "You tried to modify or remove an IVR object using an ID that did not correspond to a valid IVR on the system",
            "ivrUriConflict": "You tried to make modifications to an IVR object which would have caused a URI conflict",
            "ldapMappingDoesNotExist": "You tried to modify or remove an LDAP mapping using an ID that did not correspond to a valid LDAP mapping",
            "ldapServerDoesNotExist": "You tried to modify or remove an LDAP server using an ID that did not correspond to a valid LDAP server",
            "ldapSourceDoesNotExist": "You tried to modify or remove an LDAP source using an ID that did not correspond to a valid LDAP source",
            "ldapSyncCannotBeCancelled": "You tried to cancel an LDAP synchronization that has either started or completed – only LDAP synchronization methods that have not started yet can be cancelled",
            "ldapSyncDoesNotExist": "You tried to query or cancel an LDAP synchronization with an ID that did not correspond to a valid LDAP synchronization",
            "messageDoesNotExist": "You tried to remove a coSpace message using an ID that did not correspond to a valid coSpace message",
            "outboundDialPlanRuleDoesNotExist": "You tried to modify or remove an outbound dial plan rule using an ID that did not correspond to a valid outbound dial plan rule",
            "parameterError": "One or more parameters in a request were found to be invalid. Supporting parameter and error values give more detail about the failure",
            "participantLimitReached": "You tried to add a new participant beyond the maximum number allowed for the call",
            "recorderDoesNotExist": "You tried to modify or remove a recorder using an ID that did not correspond to a valid recorder. Present from R1.9",
            "tenantDoesNotExist": "You tried to modify or remove a tenant using an ID that did not correspond to a valid tenant",
            "tenantGroupCoSpaceIdConflict": "Your request to remove or use a tenant group would have resulted in a coSpace ID conflict. Present from R1.8",
            "tenantGroupDoesNotExist": " You tried to modify, remove or use a tenant group that does not exist. Present from R1.8",
            "tenantParticipantLimitReached": "You tried to add a new participant beyond the maximum number allowed for the owning tenant",
            "tooManyCdrReceivers": "You tried to add a new CDR receiver when the maximum number were already present. R1.8 supports up to 2 CDR receivers",
            "tooManyLdapSyncs": "A method to create a new LDAP synchronization method failed. Try again later",
            "66unrecognisedObject": " There are elements in the URI you are accessing that are not recognized; e.g, you specified the wrong object ID in the URI",
            "userDoesNotExist": "You tried to modify or remove a user using an ID that did not correspond to a valid user",
            "userProfileDoesNotExist": "You tried to modify a user profile using an ID that did not correspond to a valid user profile"
        }

    def _cms_request(self, api_method, parameters={}, payload=None, http_method='GET'):
        '''
        Send a request to a CMS server using the given parameters, payload, and method. Check results for
        HTTP-response errors, then parse the CMS response and return its value.

        :param api_method:  The API method, such as "coSpaces" that will be used with the existing base_url to form a
                            complete url, such as "/api/v1/coSpaces"
        :param parameters:  A dictionary of parameters to be sent, such as {'filter': 'sales'}
        :param payload:     The payload to be sent, typically with a POST or PUT
        :param http_method: The request verb. CMS only supports 'GET', 'PUT', 'POST', and 'DELETE'
        :type method: String
        :type parameters: Dict
        :type payload: String
        :type http_method: String
        :returns: return a response dictionary with the following keys:
           'success'  :rtype:Bool:   Whether the response received from the server is deemed a success
           'message'  :rtype:String: Contains error information, either from the server or from the CMS, if available
           'response' :rtype:Dict:   The parsed response, converted from the XML of the raw response.
        :rtype: Dict
        '''
        resp = self._send_request(api_method, parameters=parameters,
                                  payload=payload, http_method=http_method)
        if resp['success']:
            resp = self._check_response(resp)
            resp = self._cms_parse_response(resp)
        return resp

    def _cms_parse_response(self, raw_resp):
        '''
        Return a parsed dictionary with the response from the raw response from _cms_request.

        This function takes a raw response from _cms_request and attempts to convert the response key
        to a dict type (from its original Response type).  Within this response, based on the @total
        key, the contents may either be a list of dictionaries or just a dictionary (if @total=1).
        For ease of processing later on, we will always return a list of dictionaries.

        :param raw_resp: Dictionary with minimally the following key:
           'response' :rtype:requests.models.Response: The raw response from the requests library.
        :rtype Dict

        :returns: return a dictionary with the following keys:
           'success'  :rtype:Bool:  Whether the response received from the server is deemed a success
           'message'  :rtype:String: Contains error information, either from the server or from the CMS, if available
           'response' :rtype:Dict: The parsed response, converted from the XML of the raw response.
        :rtype: Dict
        '''
        result = {'success': raw_resp['success'],
                  'message': raw_resp['message'], 'response': ''}

        try:
            # Convert the binary encoded XML to a OrderedDict using xmltodict.parse
            parsed_response = xmltodict.parse(
                raw_resp['response'].content.decode("utf-8"))

            # Get the root key from the dictionary (e.g. 'coSpaces')
            rootobj = list(parsed_response.keys())[0]

            # Check if we had returned a 200-299 response code
            if result['success']:
                # In cases where there is exactly one user/object/etc, the child object
                # will contain a dict, instead of having a list of dicts for each child
                try:
                    childobj = list(parsed_response[rootobj].keys())[1]

                    if isinstance(parsed_response[rootobj][childobj], dict):
                        parsed_response = xmltodict.parse(
                            raw_resp['response'].content, force_list={childobj: True})
                except IndexError:
                    pass
                # Replace the response value with our parsed_response, converting the OrderedDict to dict
                result['response'] = json.loads(json.dumps(parsed_response))

            else:
                # Error codes for CMS. These are returned with a 400 response code with a rootobj=failureDetails
                if rootobj == 'failureDetails':
                    error_tag = list(parsed_response[rootobj].keys())[0]
                    try:
                        # Map a known CMS error code
                        result['message'] = '{}: {}.  URL={}'.format(error_tag,
                                                                     self.error_codes[error_tag],
                                                                     raw_resp['response'].request.url)
                    except KeyError:
                        # We couldn't map that error tag to a known code, so just return the tag
                        result['message'] = error_tag
                else:
                    # Unknown root object
                    result['message'] = 'Unknown root object: {}'.format(
                        rootobj)
                    result['response'] = json.loads(
                        json.dumps(parsed_response))

        # No XML found in the response. check the Location header and return it, if present
        except xml.parsers.expat.ExpatError:
            try:
                # Return the string from the location header, if present
                location = raw_resp['response'].headers['location'].split("/")[len(
                    raw_resp['response'].headers['location'].split("/"))-1]
                result['response'] = location
            except:
                pass
        except Exception as e:
            result['message'] = 'Failed to decode response content: \
                                {}.  URL={}'.format(e, raw_resp['response'].request.url)

        return result
