import json
from flaskr.rest.v1.rest import REST
from base64 import b64encode


class CUPI(REST):
    """The CUPI Server class

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

    """

    def __init__(self, host, username, password, port=443):
        # Define the header structure for CUPI
        headers = {
            'Authorization': "Basic " + b64encode(str.encode(username + ":" + password)).decode("utf-8"),
            'Accept': 'application/json',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json'
        }

        # Create a super class, where the CUPI class inherits from the REST class.  This will allow us to
        # add CUPI-specific items.
        # Reference:  https://realpython.com/python-super/
        super().__init__(host, base_url='/vmrest', headers=headers, port=port)

    def _cupi_request(self, api_method, parameters={}, payload=None, http_method='GET'):
        # Create a line of URL paramters from the dictionary, however only convert the spaces to %20
        # parameters = "&".join("{}={}".format(*i) for i in parameters.items()).replace(' ', '%20')
        # json.loads(json.dumps(xml... in order to convert from OrderedDict to dict
        resp = self._send_request(api_method, parameters=parameters,
                                  payload=json.dumps(payload), http_method=http_method)

        if resp['success']:
            # Check for non-2XX response code
            resp = self._check_response(resp)
            # if resp['success']:
            #     # We have a valid response in the 2XX range, parse this response
            resp = self._cupi_parse_response(resp)
        return resp

    def _cupi_parse_response(self, raw_resp):
        '''
        This function takes a raw response from _cupi_request and attempts to convert the response key
        to a dict type (from its original Response type).  Within this response, based on the @total
        key, the contents may either be a list of dictionaries or just a dictionary (if @total=1).
        For ease of processing later on, we will always return a list of dictionaries.

        When requested, CUPI will respond with JSON payload.  However in some cases, such as importing
        a user, the payload may just be a binary string, since it is only returning the object's ID.
        '''
        result = {}
        try:
            result['success'] = raw_resp['success']
            # Attempt to parse the response into JSON format from the Response type from the requests
            # module to a dictionary
            parsed_response = json.loads(raw_resp['response'].content.decode("utf-8"))
            try:
                # check if there is only one element, meaning xmltodict would not have created a list
                if(str(parsed_response["@total"]) == "1"):
                    # Get the child key nested under the root (e.g. 'Users')
                    rootobj = [key for key in parsed_response.keys() if key not in '@total'][0]
                    # Force the child element to be a list
                    parsed_response[rootobj] = [parsed_response[rootobj]]

            # If the @total key didn't exist, just return the result
            except KeyError:
                pass
            # Replace the response value with our parsed_response
            result['response'] = parsed_response

        except json.decoder.JSONDecodeError:
            # Could not decode as JSON;  raw response  was likely a binary string; convert it to regular string type.
            result['message'] = raw_resp['response'].content.decode()

        return result

    def get_users(self, parameters={}):
        """Get a list of users on the Unity Connection system.

        See also:
        https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/connection/REST-API/CUPI_API/b_CUPI-API/b_CUPI-API_chapter_011101.html#reference_E4DD44846143441C8FB01478AB71476B
        """
        return self._cupi_request("users", parameters=parameters)

    def get_ldapusers(self, parameters={}):
        """Get a list of users on the Unity Connection system.

        See also:
        https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/connection/REST-API/CUPI_API/b_CUPI-API/b_CUPI-API_chapter_011101.html#reference_E4DD44846143441C8FB01478AB71476B
        """
        return self._cupi_request("import/users/ldap", parameters=parameters)

    def import_ldapuser(self, parameters={}, payload=None):
        """Get a list of users on the Unity Connection system.

        See also:
        https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/connection/REST-API/CUPI_API/b_CUPI-API/b_CUPI-API_chapter_011101.html#reference_E4DD44846143441C8FB01478AB71476B
        """
        return self._cupi_request("import/users/ldap", parameters=parameters, payload=payload, http_method='POST')

    def get_user(self, id):
        """Get a voicemail user from the Unity Connection system by user id.

        See also:
        https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/connection/REST-API/CUPI_API/b_CUPI-API/b_CUPI-API_chapter_011101.html#reference_E4DD44846143441C8FB01478AB71476B
        """
        return self._cupi_request("users/" + str(id))

    def update_user(self, id, payload=None):
        """Modify a user on the Unity Connection system.

        See also:
        https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/connection/REST-API/CUPI_API/b_CUPI-API/b_CUPI-API_chapter_011101.html#reference_E4DD44846143441C8FB01478AB71476B
        """
        return self._cupi_request("users/" + str(id), payload=payload, http_method='PUT')

    def delete_user(self, id):
        """Delete a user from the Unity Connection system.

        See also:
        https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/connection/REST-API/CUPI_API/b_CUPI-API/b_CUPI-API_chapter_011101.html#reference_E4DD44846143441C8FB01478AB71476B
        """
        return self._cupi_request("users/" + str(id), http_method='DELETE')

    def update_pin(self, id, payload=None):
        """Modify a user on the Unity Connection system.

        Payload example:
        {
            "Credentials":"14235834"
        }

        See also:
        https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/connection/REST-API/CUPI_API/b_CUPI-API/b_CUPI-API_chapter_011110.html#reference_B32245DBC67A42228AA514C41D708368
        """

        return self._cupi_request('users/' + str(id) + '/credential/pin', payload=payload, http_method='PUT')
