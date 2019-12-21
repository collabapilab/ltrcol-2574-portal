import xmltodict
import json
import urllib.parse
import xml.etree.ElementTree as ET
from flaskr.rest.v1.rest import REST
from base64 import b64encode
import xml.parsers.expat


class CMS(REST):
    """The CMS Server class

    Use this class to connect and make API calls to an most REST-based devices.

    :param host: The Hostname / IP Address of the server
    :param username: The username of an account with access to the API.
    :param password: The password for your user account
    :param port: (optiona) The server port for API access (default: 443)
    :type host: String
    :type username: String
    :type password: String
    :type port: Integer
    :returns: return an CMS object
    :rtype: CMS

    """

    def __init__(self, host, username, password, port=443):
        super().__init__(host, username, password, base_url='/api/v1', port=port)
        self.headers = {
            'Authorization': "Basic " + b64encode(str.encode(username + ":" + password)).decode("utf-8"),
            'Accept': 'application/xml',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json'
        }

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
            "unrecognizedObject": " There are elements in the URI you are accessing that are not recognized; e.g, you tried to perform a GET on /api/v1/system/profile rather than (the correct) /api/v1/system/profiles",
            "userDoesNotExist": "You tried to modify or remove a user using an ID that did not correspond to a valid user",
            "userProfileDoesNotExist": "You tried to modify a user profile using an ID that did not correspond to a valid user profile"
        }


    def _cms_request(self, method, parameters={}, payload=None, HTTPmethod='GET'):
        # Change the parameters from dictionary to an encoded string
        parameters = urllib.parse.urlencode(parameters)
        resp = self._send_request(method, parameters=parameters,
                                  payload=payload, headers=self.headers, HTTPmethod=HTTPmethod)
        if resp['success']:
            resp = self._cms_parse_response(resp)
        return resp


    def _cms_parse_response(self, resp):

        result = self._check_non2XX_response(resp)

        try:
            if resp['response'].status_code in list(range(200, 300)):
                # parse response
                # json.loads(json.dumps(xml... in order to convert from OrderedDict to dict
                response = xmltodict.parse(resp['response'].content.decode("utf-8"))
                if len(response) == 0:
                    try:
                        result['location'] = response.headers._store['location']
                    except:
                        # No location header present
                        pass
                    result['message'] = json.loads(json.dumps(response))
                else:
                    try:
                        # Get the root key from the dictionary (e.g. 'coSpaces')
                        rootName = list(response.keys())[0]

                        # check if there is only one element, meaning xmltodict would not have created a list
                        if(response[rootName]["@total"] == "1"):
                            # Get the child key nested under the root (e.g. 'coSpace')
                            childName = list(response[rootName].keys())[1]
                            # Force the child element to be a list
                            response = xmltodict.parse(
                                resp['response'].content, force_list={childName: True})

                    # Maybe the @total key didn't exist; we'll just return the result
                    except KeyError:
                        pass
                    result['message'] = json.loads(json.dumps(response))
            else:
                # Error codes for CMS
                try:
                    root = ET.fromstring(resp['response'].content)
                    error_tag = root[0].tag
                    try:
                        result['success']: False
                        result['message'] = error_tag + \
                            ': ' + self.error_codes[error_tag]
                    except KeyError:
                        # We couldn't map that error code, so just return the tag
                        result['message'] = error_tag
                except IndexError:
                    # We couldn't find the root element item
                    pass
                except ET.ParseError:
                    # We couldn't parse the XML
                    result['success']: False
                    result['message'] = 'Invalid XML received from device'

        except xml.parsers.expat.ExpatError:
            try:
                result = resp['response'].headers['location'].split(
                    "/")[len(resp['response'].headers['location'].split("/"))-1]
            except:
                result = resp['response'].headers['Date']

        return result

    def get_system_status(self):
        """Get information on the current system status, e.g. software version, uptime etc.
        
        :Example:
            >>> print(a.get_system_status())

        .. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=68
        .. note:: v1.8 upward
        """
        # return self._send_request("system/status")
        return self._cms_request("system/status")

    def get_coSpaces(self, parameters={}):
        """Get the coSpaces within the Acano VM. These are returned in an arbitrary order.

        :param parameters: A dictionary of parameters, per the Acano API.
        :type parameters: Dict
        
        :Example:
            >>> print(a.get_coSpaces())

        :Example:

            >>> print(a.get_coSpaces(parameters = {
            >>> 'offset' : 5
            >>> }))

        .. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=25
        .. note:: v1.8 upward

        """
        return self._cms_request("coSpaces", parameters=parameters)

    def create_coSpace(self, payload={}):
        """Create a new coSpace

        :param payload: Details the initial state of the newly created coSpace
        :type payload: Dict
        
        :Example:
            >>> print(a.create_coSpace())

        :Example:

            >>>	print(a.create_coSpace(payload = {
            >>>	'name' : 'Emergency meeting'
            >>>	}))

        .. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=25
        .. note:: v1.8 upward

        """
        return self._cms_request("coSpaces", payload=payload, HTTPmethod='POST')

    def update_coSpace(self, id, payload):
        """Make changes to an existing coSpace, using the coSpace ID as the identifier.

        :param coSpace_id: The ID of the coSpace to modify. This can be returned from the get_coSpaces()["coSpaces"]["coSpace"][i]["@id"]
        :type coSpace_id: String

        :param payload: Details the new state of the identified coSpace
        :type payload: Dict
        
        :Example:
            >>>	print(a.modify_coSpace("3b8dfa05-f7b6-41f2-b14a-739a0d015b90", payload = {
            >>>	"name" : "Modified coSpace"
            >>>	}))

        .. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=25
        .. note:: v1.8 upward
        """
        return self._cms_request("coSpaces/" + id, payload=payload, HTTPmethod='PUT')

    def get_coSpace(self, id):
        """Get the details of a coSpace, using the coSpace ID as the identifier.

        :param coSpace_id: The ID of the coSpace to modify. This can be returned from the get_coSpaces()["coSpaces"]["coSpace"][i]["@id"]
        :type coSpace_id: String

        :param parameters: Filters for the query
        :type parameters: Dict
        
        :Example:
            >>> print(a.get_coSpace("3b8dfa05-f7b6-41f2-b14a-739a0d015b90"))

        .. seealso:: https://www.acano.com/publications/2015/09/Solution-API-Reference-R1_8.pdf#page=27
        .. note:: v1.8 upward
        """
        return self._cms_request(("coSpaces/" + id))

    def delete_coSpace(self, id):
        """Delete a coSpace, using the coSpace ID as the identifier.

        :param coSpace_id: The ID of the coSpace to delete. This can be returned from the get_coSpaces()["coSpaces"]["coSpace"][i]["@id"]
        :type coSpace_id: String
        
        :Example:
            >>> print(a.delete_coSpace("3b8dfa05-f7b6-41f2-b14a-739a0d015b90"))

        .. note:: This function is not explicitly described in the Acano API reference
        .. note:: v1.8 upward
        """
        return self._cms_request("coSpaces/" + id, HTTPmethod="DELETE")
