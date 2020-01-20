import json
import re
from base64 import b64encode
from flaskr.rest.v1.rest import REST


class CUPI(REST):
    '''
    The CUPI Server class

    Use this class to connect and make API calls using the Cisco Unity Provisioning Interface.

    :param host: The Hostname / IP Address of the server
    :param username: The username of an account with access to the API.
    :param password: The password for your user account
    :param port: (optiona) The server port for API access (default: 443)
    :type host: String
    :type username: String
    :type password: String
    :type port: Integer
    :returns: return an CUPI object
    :rtype: CUPI
    '''

    def __init__(self, host, username, password, port=443):
        '''
        Initialize the CUPI class as a child of the REST class. Define the CUPI-specific headers, and API base_url
        '''
        # Define the header structure for CUPI
        headers = {
        }

        # Create a super class, where the CUPI class inherits from the REST class.  This will allow us to
        # add CUPI-specific items.  Reference:  https://realpython.com/python-super/

    def _cupi_request(self, api_method, parameters={}, payload=None, http_method='GET'):
        '''
        Send a request to a CUC server using the given parameters, payload, and method. Check results for
        HTTP-response errors, then parse the CUC response and return its value.

        :param api_method:  The API method, such as "users" that will be used with the existing base_url to form a
                            complete url, such as "/vmrest/users"
        :param parameters:  A dictionary of parameters to be sent, such as {'filter': 'sales'}
        :param payload:     The payload to be sent, typically with a POST or PUT
        :param http_method: The request verb. CUPI only supports 'GET', 'PUT', 'POST', and 'DELETE'
        :type method: String
        :type parameters: Dict
        :type payload: String
        :type http_method: String
        :returns: return a response dictionary with the following keys:
           'success'  :rtype:Bool:   Whether the response received from the server is deemed a success
           'message'  :rtype:String: Contains error information, usually from the server
           'response' :rtype:Dict:   The parsed response, converted from the raw response.
        :rtype: Dict
        '''
        pass

    def _cupi_parse_response(self, raw_resp):
        '''
        Return a parsed dictionary with the response from the raw response from _cupi_request.

        This function parses the a raw response from _cupi_request and returns:
          -  success indication
          -  message with any string payload returned  
          -  response payload in a dict

        :param raw_resp: Dictionary with minimally the following key:
           'response' :rtype:requests.models.Response: The raw response from the requests library.
        :rtype Dict

        :returns: return a dictionary with the following keys:
           'success' :rtype:Bool:  Whether the response received from the server is deemed a success
           'message' :rtype:String: Contains error information, either from the server or from the CMS, if available
           'response' :rtype:Dict: The parsed response, converted from the raw response.
        :rtype: Dict
        '''
        result = {'success': raw_resp['success'],
                  'message': raw_resp['message'], 'response': ''}
        # Check if the payload had any data to decode
