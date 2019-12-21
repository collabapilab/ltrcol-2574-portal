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
        # Create a super class, where the CUPI class inherits from the REST class.  This will allow us to 
        # add CUPI-specific items.
        # Reference:  https://realpython.com/python-super/
        super().__init__(host, username, password, base_url='/vmrest', port=port)

        self.headers = {
            'Authorization': "Basic " +  b64encode(str.encode(username + ":" + password)).decode("utf-8"),
            'Accept': 'application/json',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json'
        }

    def _cupi_request(self, api_method, parameters={}, payload=None, HTTPmethod='GET'):
        # Create a line of URL paramters from the dictionary, however only convert the spaces to %20
        # parameters = "&".join("{}={}".format(*i) for i in parameters.items()).replace(' ', '%20')
        resp = self._send_request(api_method, parameters=parameters, payload=json.dumps(
            payload), headers=self.headers, HTTPmethod=HTTPmethod)
        if resp['success']:
            resp = self._cupi_parse_response(resp)
        return resp

    def _cupi_parse_response(self, resp):
        '''
        When requested, CUPI will respond with JSON payload.  However in some cases, such as importing a user, the payload
        may just be a binary string, since it is only returning the object's ID.
        '''

        result = self._check_non2XX_response(resp)
        try:
            # parse response
            # json.loads(json.dumps(xml... in order to convert from OrderedDict to dict
            response = json.loads(resp['response'].content.decode("utf-8"))
            try:
                # check if there is only one element, meaning xmltodict would not have created a list
                if(str(response["@total"]) == "1"):
                    # Get the child key nested under the root (e.g. 'Users')
                    rootobj = [key for key in response.keys() if key not in '@total'][0]
                    # Force the child element to be a list
                    response[rootobj] = [response[rootobj]]

            # Maybe the @total key didn't exist; we'll just return the result
            except KeyError:
                pass
            result['results'] = json.loads(json.dumps(response))
                
        except json.decoder.JSONDecodeError:
            # Could not decode as JSON; that means the result was most likely a binary string
            result['message'] = resp['response'].content.decode()

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
        return self._cupi_request("import/users/ldap", parameters=parameters, payload=payload, HTTPmethod='POST')

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
        return self._cupi_request("users/" + str(id), payload=payload, HTTPmethod='PUT')

    def delete_user(self, id):
        """Delete a user from the Unity Connection system.

        See also:  
        https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/connection/REST-API/CUPI_API/b_CUPI-API/b_CUPI-API_chapter_011101.html#reference_E4DD44846143441C8FB01478AB71476B
        """
        return self._cupi_request("users/" + str(id), HTTPmethod='DELETE')

    def update_pin(self, id, payload=None):
        """Modify a user on the Unity Connection system.

        Payload example:
        {
            "Credentials":"14235834"
        }


        See also:  
        https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/connection/REST-API/CUPI_API/b_CUPI-API/b_CUPI-API_chapter_011110.html#reference_B32245DBC67A42228AA514C41D708368
        """

        return self._cupi_request('users/' + str(id) + '/credential/pin', payload=payload, HTTPmethod='PUT')
