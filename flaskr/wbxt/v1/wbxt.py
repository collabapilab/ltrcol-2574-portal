import json
from flaskr.rest.v1.rest import REST

# Retrieve access token from:
# https://developer.webex.com/docs/api/getting-started/accounts-and-authentication
wbxt_access_token = 'ZDg2NDU1MDUtOWY0Mi00YmM5LTgxNGItOGY5NzE4YWQyZGNjNDRhZTFlOGUtOGUw_PF84_d28d283c-6ebb-4988-88bd-1272ee4dbff8'

class WBXT(REST):
    """The WBXT Server class

    Use this class to connect and make API calls to WebEx Teams.


    """

    def __init__(self):
        headers = {
            'Authorization': "Bearer " + wbxt_access_token,
            'Content-Type': 'application/json;charset=utf-8'
        }
        super().__init__(host='api.ciscospark.com', base_url='/v1', headers = headers)


    def _wbxt_parse_response(self, resp):
        result = self._check_response(resp)
        try:
            # parse response
            response = json.loads(resp['response'].content.decode("utf-8"))
            result['results'] = json.loads(json.dumps(response))

        except json.decoder.JSONDecodeError:
            # Could not decode as JSON; try to decode as a binary string
            result['message'] = resp['response'].content.decode()

        return result

    def _wbxt_request(self, api_method, parameters={}, payload=None, HTTPmethod='GET'):
        resp = self._send_request(api_method, parameters=parameters,
                                  payload=json.dumps(payload), HTTPmethod=HTTPmethod)
        
        if resp['success']:
            resp = self._wbxt_parse_response(resp)
        return resp

    def get_rooms(self):
        return self._wbxt_request("rooms")

    def create_message(self, payload=None):
        return self._wbxt_request("messages", payload=payload, HTTPmethod="POST")
