import json
import xmltodict
import xml.parsers.expat
from flaskr.rest.v1.rest import REST
from base64 import b64encode


class UDS(REST):
    '''
    The UDS Server class

    Use this class to connect and make API calls to an most Cisco Meeting Server devices.

    :param host: The Hostname / IP Address of the server
    :param username: The username of an account with access to the API.
    :param password: The password for your user account
    :param port: (optional) The server port for API access (default: 443)
    :type host: String
    :type username: String
    :type password: String
    :type port: Integer
    :returns: return an UDS object
    :rtype: UDS
    '''

    def __init__(self, host, username=None, password=None, port=8443):
        '''
        Initialize the UDS class as a child of the REST class. Define the UDS-specific headers, and API base_url
        '''
        # Define the header structure for UDS. 
        headers = {
            'Accept': 'application/xml'
        }

        # Create a super class, where the UDS class inherits from the REST class.
        super().__init__(host, username, password, base_url='/cucm-uds', headers=headers, port=port)


    def _uds_request(self, api_method, parameters={}, payload=None, http_method='GET'):
        '''
        Send a request to a UDS server using the given parameters, payload, and method. Check results for
        HTTP-response errors, then parse the UDS response and return its value.

        :param api_method:  The API method, such as "users" that will be used with the existing base_url to form a
                            complete url, such as "/cucm-uds/users"
        :param parameters:  A dictionary of parameters to be sent
        :param payload:     The payload to be sent, typically with a POST or PUT
        :param http_method: The request verb. UDS only supports 'GET', 'PUT', 'POST', and 'DELETE'
        :type method: String
        :type parameters: Dict
        :type payload: String
        :type http_method: String
        :returns: return a response dictionary with the following keys:
           'success'  :rtype:Bool:   Whether the response received from the server is deemed a success
           'message'  :rtype:String: Contains error information, either from the server or from UDS, if available
           'response' :rtype:Dict:   The parsed response, converted from the XML of the raw response.
        :rtype: Dict
        '''

        resp = self._send_request(api_method, parameters=parameters, 
                                  payload=payload, http_method=http_method)
        if resp['success']:
            resp = self._check_response(resp)
            resp = self._uds_parse_response(resp)
        return resp

    def _uds_parse_response(self, raw_resp):
        '''
        Return a parsed dictionary with the response from the raw response from _uds_request.

        This function takes a raw response from _uds_request and attempts to convert the response key
        to a dict type (from its original Response type).  Within this response, based on the @total
        key, the contents may either be a list of dictionaries or just a dictionary (if @total=1).
        For ease of processing later on, we will always return a list of dictionaries.

        :param raw_resp: Dictionary with minimally the following key:
           'response' :rtype:requests.models.Response: The raw response from the requests library.
        :rtype Dict

        :returns: return a dictionary with the following keys:
           'success'  :rtype:Bool:  Whether the response received from the server is deemed a success
           'message'  :rtype:String: Contains error information, either from the server or from the UDS, if available
           'response' :rtype:Dict: The parsed response, converted from the XML of the raw response.
        :rtype: Dict
        '''
        result = {'success': raw_resp['success'], 'message': raw_resp['message'], 'response': ''}
        
        try:
            # Convert the binary encoded XML to a OrderedDict using xmltodict.parse
            parsed_response = xmltodict.parse(raw_resp['response'].content.decode("utf-8"))
            
            # Get the root key from the dictionary (e.g. 'coSpaces')
            rootobj = list(parsed_response.keys())[0]

            # Check if we had returned a 200-299 response code
            if result['success']:
                try:
                    # check if there is only one element, @totalCount will be 1.  in that case, xmltodict
                    # would not have created a list of dicts
                    if(parsed_response[rootobj]["@totalCount"] == "1"):
                        # Get the child key nested under the root (e.g. 'user')
                        childobj = [key for key in parsed_response[rootobj].keys() if key[0] not in '@'][0]

                        # Force the child element to be a list
                        parsed_response = xmltodict.parse(
                            raw_resp['response'].content, force_list={childobj: True})

                # The @totalCount key does not exist; just return the result
                except KeyError:
                    pass
                
                # Replace the response value with our parsed_response, converting the OrderedDict to dict
                result['response'] = json.loads(json.dumps(parsed_response))

            else:
                result['response'] = json.loads(json.dumps(parsed_response))

        except Exception as e:
            result['message'] = 'Failed to decode response content: \
                                {}.  URL={}'.format(e, raw_resp['response'].request.url)

        return result

    def get_user(self, userid=None):
        '''
        Retrieve user via UDS.

        :returns: Dictionary with the following key/value pairs:
            - success (bool): Whether or not an error was encountered
            - message (string): Detailed message about the message sent/received
            - num_found (int): number of users found (should be 1 or 0)
            - response (dict): the user object dictionary, if found.
        '''
        params = {'username': userid}
        user = self._uds_request("users", parameters=params)

        user['num_found'] = 0
        if user['success']:
            try:
                # For a specific user search, @totalCount will be 1 or generate a KeyError
                user['num_found'] = int(user['response']['users']['@totalCount'])
                # Assign the response to just that single user's information
                user['response'] = user['response']['users']['user'][0]

            except KeyError:
                pass
        return user
