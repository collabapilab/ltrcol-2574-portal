from requests import get, post, put, delete, request, packages
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException
import xmltodict
import json
import urllib.parse
import urllib3
import xml.etree.ElementTree as ET

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

default_cms = {
   'host': 'cms1a.pod31.col.lab',
   'port': 8443,
   'username': 'admin',
   'password': 'c1sco123'
}

cms_error_codes = {
    "accessMethodDoesNotExist": "You tried to modify or remove an accessMethod using an ID that did not correspond to a valid access method",
    "callBrandingProfileDoesNotExist": "You tried to modify or remove a call branding profile using an ID that did not correspond to a valid call branding profile",
    "callBridgeDoesNotExist": "You tried to modify or remove a configured clustered Call Bridge using an ID that did not correspond to a valid clustered Call Bridge",
    "callDoesNotExist": "You tried to perform a method on a call object using an ID that did not correspond to a currently active call",
    "callRecordingCannotBeModified": "You tried to start/stop recording a call that cannot be modified. Present from R1.9",
    "callLegCannotBeDeleted": "You tried to delete a call leg that can't be deleted. Present from R1.8",
    "callLegDoesNotExist": "You tried to perform a method on a call leg object using an ID that did not correspond to a currently active call leg",
    "callLegProfileDoesNotExist": "You tried to modify or remove a callLegProfile using an ID that did not correspond to a valid call leg profile",
    "callProfileDoesNotExist": "You tried to modify or remove a callProfile using an ID that is not valid",
    "cdrReceiverDoesNotExist": "You tried to modify or remove a CDR receiver using an ID that did not correspond to a valid CDR receiver. Present from R1.8"
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


def cms_send_request(host, username, password, port, base_url, id=None, parameters={}, body=None, request_method='GET'):

    # Check if a PUT or DELETE method does not have a required ID
    if request_method.upper() in ['PUT', 'DELETE'] and not id:
        return {'success': False,
                'message': 'ID was not supplied supplied for {} request.'.format(request_method.upper())}

    # Set the URL to be called
    url = "https://{}:{}{}".format(host, port,  base_url)

    # Append the ID, if present
    if id is not None:
        url = "{}/{}".format(url, id)

    # Set the search/sort parameters
    if len(parameters) > 0:
        url = "{}?{}".format(url,  urllib.parse.urlencode(parameters))

    # Set the required header information and authentication parameters
    auth = HTTPBasicAuth(username, password)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Encode the body, if present
    if body:
        body = urllib.parse.urlencode(body)

    # Verify if the supplied request method (GET, PUT, POST, or DELETE) is valid
    if request_method.upper() in ['GET', 'PUT', 'POST', 'DELETE']:
        try:
            # Send the request and handle any exception that may occur
            response = request(request_method, url, auth=auth,
                               data=body, headers=headers, verify=False, timeout=2)

            # Raise HTTPError error for non-2XX responses
            response.raise_for_status()

            # Check for expected response and set the result accordingly
            if response.status_code == 200:
                result = {'success': True,
                          'response': cms_parse_response(response)}

                # When creating an object, CMS returns it in the location portion of the header.
                # If that field is present, we will store it in the 'id' portion of the result
                try:
                    result['id'] = response.headers._store['location'][1][len(
                        location)+1:]
                except Exception e:
                    pass

            else:
                # seed result with the default response
                result = {'success': False, 'message': json.loads(
                    json.dumps(xmltodict.parse(response.content)))}
                try:
                    root = ET.fromstring(response.content)
                    error_tag = root[0].tag
                    try:
                        result['message'] = error_tag + ': ' + cms_error_codes[error_tag]
                    except KeyError:
                        # We couldn't map that error code, so just return the tag
                        result['message'] = error_tag
                except IndexError:
                    # We couldn't find the root element item
                    pass
                except ET.ParseError:
                    # We couldn't parse the XML
                    result['message'] = 'Invalid XML received from CMS'

        except RequestException as e:
            result = {'success': False, 'message': str(e)}

    else:
        result = {'success': False,
                  'message': 'Invalid request method: {}'.format(request_method)}

    return result


def cms_parse_response(response):
    """
    Parses the response contents of the body.  This would be present after a GET operation.

    Use this method to query for the CMS system status.
    """

    # If response contains any content in the body, convert to an ordered dictionary type
    if len(response.content) == 0:
        try:
            return response.headers._store['location'][1][len(response.request.path_url)+1:]
        except KeyError:
            return json.loads(json.dumps({}))

    # Convert the XML to an ordered dictionary (a regular dictionary, that maintains a consisten order of
    # elements, similar to a list)
    resp_odict = xmltodict.parse(response.content)

    # Always return a list of dictionaries instead of only when there's multiple XML elements
    try:
        # Get the root key from the dictionary (e.g. 'coSpaces')
        rootName = list(resp_odict.keys())[0]

        # check if there is only one element, meaning xmltodict would not have created a list
        if(resp_odict[rootName]["@total"] == "1"):
            # Get the child key nested under the root (e.g. 'coSpace')
            childName = list(resp_odict[rootName].keys())[1]
            # Force the child element to be a list
            resp_odict = xmltodict.parse(
                response.content, force_list={childName: True})

        # No elements, so just return a blank dictionary
        elif (len(resp_odict) == 0):
            return json.loads(json.dumps({}))

    # Maybe the @total key didn't exist; we'll just return the result
    except KeyError:
        pass 

    # convert from ordered dict to plain dict
    resp_dict = json.loads(json.dumps(resp_odict))
    return resp_dict
