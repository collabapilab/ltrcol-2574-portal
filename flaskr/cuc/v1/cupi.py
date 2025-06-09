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

    def __init__(self, host, username, password, port=443, tls_verify=False):
        '''
        Initialize the CUPI class as a child of the REST class. Define the CUPI-specific headers, and API base_url
        '''
        # Define the header structure for CUPI
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        # Create a super class, where the CUPI class inherits from the REST class.  This will allow us to
        # add CUPI-specific items.  Reference:  https://realpython.com/python-super/
        super().__init__(host, username, password, base_url='/vmrest',
                         headers=headers, port=port, tls_verify=tls_verify)

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
        resp = self._send_request(api_method, parameters=parameters,
                                  payload=json.dumps(payload), http_method=http_method)

        if resp['success']:
            resp = self._check_response(resp)
            resp = self._cupi_parse_response(resp)
        return resp

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
        if len(raw_resp['response'].content) > 0:
            try:
                # Could not decode as JSON; convert the binary response to a string type
                response_string = raw_resp['response'].content.decode('utf-8')

                # Attempt to convert the response string into a dict using json.loads
                parsed_response = json.loads(response_string)

                # Convert Response payload ("content") from byte type into string-, the to dict using json.loads
                # parsed_response = json.loads(raw_resp['response'].content.decode("utf-8"))
                try:
                    # From most responses, @total key will indicate how many items were found. If @total=1,
                    # the data included under child key will be a dict; if @total>1, then a list of dicts.
                    # We would like to always return a list of dicts, even if there's only one item in the list.
                    if(str(parsed_response["@total"]) == "1"):
                        # Find the child key nested under the root (e.g. 'Users'), ignoring '@total' key
                        rootobj = [
                            key for key in parsed_response.keys() if key not in '@total'][0]
                        # Force the child element to be a list
                        parsed_response[rootobj] = [parsed_response[rootobj]]

                # The @total key does not exist; just return the result
                except KeyError:
                    # There was likely an error that we can supply in the message
                    try:
                        result['message'] = parsed_response['errors']['message']
                    except KeyError:
                        pass
                # Replace the response value with our parsed_response
                result['response'] = parsed_response

            # Could not decode response string into a dict using json.loads
            except json.decoder.JSONDecodeError:
                # This may be a normal response, as for a valid POST/PUT. Or it could be an error web
                # page from Unity. If it's the latter, look for an Exception tag to give us more information.
                regex = r"<b>\s*Exception:\s*</b>\s*<pre>\s*(.*?)\s+</pre>"
                exception_match = re.search(regex, response_string)
                if exception_match:
                    result['message'] = exception_match[1]
                else:
                    result['message'] = response_string

        return result
