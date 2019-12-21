from requests import get, post, put, delete, packages,request
from requests.exceptions import RequestException, HTTPError
from requests.auth import HTTPBasicAuth


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

    def __init__(self, host, username=None, password=None, base_url=None, port=443):

        # set the host, port, and base_url of the object
        self.host = host
        self.port = str(port)
        self.base_url = base_url


    def _send_request(self, api_method, parameters={}, payload=None, headers={}, HTTPmethod='GET'):

        # Set the URL, in a format such as https//host:port/api/v1/api_method
        url = "https://{}:{}{}/{}".format(self.host, self.port, self.base_url, api_method)

        try:
            # Send the request and handle any exception that may occur
            resp = request(HTTPmethod, url, data=payload, params=parameters,
                           headers=headers, verify=False, timeout=2)
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
