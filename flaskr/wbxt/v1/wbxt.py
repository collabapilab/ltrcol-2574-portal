import json
from flaskr.rest.v1.rest import REST

# Retrieve access token from:
# https://developer.webex.com/docs/api/getting-started/accounts-and-authentication
wbxt_access_token = 'MWJiY2U5YmItNDE3Mi00ZTllLTkzYzgtZDdlYmNlODgxODA5OTEyYTZiMmEtM2Vm_PF84_consumer'


class WBXT(REST):
    '''
    The WBXT Server class

    Use this class to connect and make API calls to WebEx Teams.

    :param access_token: The token to authenticate with in Webex Teams.
    :type access_token: String
    :returns: return an WBXT object
    :rtype: WBXT
    '''

    def __init__(self, access_token=wbxt_access_token):
        '''
        Initialize the WBXT class as a child of the REST class.
        Define the WBXT-specific headers, host, and API base_url
        '''
        # Define the header structure for Webex Teams
        headers = {
            'Authorization': "Bearer " + access_token,
            'Content-Type': 'application/json;charset=utf-8'
        }

        # Create a super class, where the CMS class inherits from the REST class.
        super().__init__(host='api.ciscospark.com', base_url='/v1', headers=headers)

    def _wbxt_request(self, api_method, parameters={}, payload=None, http_method='GET'):
        '''
        Send a request to Webex Teams using the given parameters, payload, and method. Check results for
        HTTP-response errors, then parse the Webex Teams response and return its value.

        :param api_method:  The API method, such as "messages" that will be used with the existing base_url to form a
                            complete url, such as "/v1/messages"
        :param parameters:  A dictionary of parameters to be sent, such as {'filter': 'sales'}, which would become
                            "?filter=sales" as part of the URL.
        :param payload:     The payload to be sent, typically with a POST or PUT
        :param http_method: The request verb. Webex Teams only supports 'GET', 'PUT', 'POST', and 'DELETE'
        :type method: String
        :type parameters: Dict
        :type payload: String
        :type http_method: String
        :returns: return a response dictionary with the following keys:
           'success'  :rtype:Bool:   Whether the response received from the server is deemed a success
           'message'  :rtype:String: Contains error information, usually from the service
           'response' :rtype:Dict:   The parsed response, converted from the raw response.
        :rtype: Dict
        '''
        resp = self._send_request(api_method, parameters=parameters,
                                  payload=json.dumps(payload), http_method=http_method)

        if resp['success']:
            # Check for non-2XX response code
            resp = self._check_response(resp)
            resp = self._wbxt_parse_response(resp)

        return resp

    def _wbxt_parse_response(self, raw_resp):
        '''
        Return a parsed dictionary with the response from the raw response from _wbxt_request.

        : param raw_resp: Dictionary with minimally the following key:
           'response': type: requests.models.Response: The raw response from the requests library.
        : rtype Dict

        : returns: return a dictionary with the following keys:
           'success': rtype: Bool:  Whether the response received from the server is deemed a success
           'message': rtype: String: Contains error information, either from the server or from the CMS, if available
           'response': rtype: Dict: The parsed response, converted from the XML of the raw response.
        : rtype: Dict
        '''
        result = {'success': False, 'message': '', 'response': ''}

        try:
            result = raw_resp['success']
            # parse response
            parsed_response = json.loads(raw_resp['response'].content.decode("utf-8"))
            result['results'] = json.loads(json.dumps(parsed_response))

        except json.decoder.JSONDecodeError:
            # Could not decode as JSON; try to decode as a binary string
            result['message'] = raw_resp['response'].content.decode()

        return result

    def get_rooms(self, parameters={}):
        '''
        Get Webex Teams Rooms (Spaces)

        :param parameters: Dictionary of parameters, such as
            teamId :type String: List rooms associated with a team, by ID.
            type   :type String: List rooms by type.  :Values: direct, group.
            sortBy :type String: Sort results.  :Values: id, lastactivity, created
            max    :type Int:    Maximum number of rooms in the response (default=100)

        :type parameters: Dict

        Reference: https://developer.webex.com/docs/api/v1/rooms/list-rooms
        '''
        return self._wbxt_request("rooms", parameters=parameters)

    def create_message(self, payload=None):
        '''
        Post a message to a Webex Teams Room (Space)

        :param payload: Payload containing the message.  E.g.
          {"roomId": "Y2lzY29zcGFyazovL3VzL1JPT00vMmQ1ODU1YTAtMTNkZi0xMWVhLWEzZjYtYjFmODVhNjU5MWMz",
           "text": "Test message"}
        :type payload: Dict

        Reference:  https://developer.webex.com/docs/api/v1/messages/create-a-message
        '''
        return self._wbxt_request("messages", payload=payload, http_method="POST")
