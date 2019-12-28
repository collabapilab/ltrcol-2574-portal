from requests import get, post, put, delete, packages, request
from requests.exceptions import RequestException, HTTPError
from requests.auth import HTTPBasicAuth


class REST:
    """
    The REST Server class
    Use this class to connect and make API calls to an most REST-based devices.

    :param host: The Hostname / IP Address of the server
    :param port: (optional) The server port for API access (default: 443)
    :param base_url: (optional) The base URL, such as "/api/v1" for a given API
    :param headers: (optional) A dictionary of header key/value pairs
    :type host: String
    :type port: Integer
    :type base_url: String
    :type headers: Dict
    :returns: return an REST object
    :rtype: REST

    """

    def __init__(self, host, base_url=None, headers={}, port=443):
        """
        Initialize an object with the host, port, and base_url using the parameters passed in.
        """
        self.host = host
        self.port = str(port)
        self.base_url = base_url
        self.headers = headers

    def _send_request(self, api_method, parameters={}, payload=None, http_method='GET'):
        """
        Used to send a REST request using the desired http_method (GET, PUT, POST, DELETE) to the
        specified base_url + api_method.  Any specified parameters and payload, where applicable,
        will be included.

        :param api_method: The Hostname / IP Address of the server
        :param parameters: (optiona) The server port for API access (default: 443)
        :param payload: (optional) A body/payload to be included in the request.
        :param http_method: (optional) The type of method (GET, PUT, POST, DELETE)

        :type host: String
        :type port: Integer

        :returns: returns a dictionary indicating success with the raw response or
                  a message indicating the error encountered.

        :rtype: Dict with 'success' and either 'response' or 'message' exception occurred
        """

        # Set the URL using the parameters of the object and the api_method requested
        # in a format such as: https//host:port/api/v1/api_method


        # Send the request and handle RequestException that may occur
        pass

    def _check_response(self, raw_response):
        """
        Check the response status.  If it has a non-2XX value, then set the 'success' result
        to false and place the exception in the 'message'
        """
        pass
