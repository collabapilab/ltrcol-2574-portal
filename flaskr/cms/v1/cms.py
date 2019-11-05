from requests import get, post, put, delete, request, packages
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException
import xmltodict
import json
import urllib.parse
import urllib3
# from flask import render_template
# import base64

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

default_cms = {
   'host': 'cms1a.pod31.col.lab',
   'port': 8443,
   'username': 'admin',
   'password': 'c1sco123'
}


def cms_send_request(host, username, password, port, base_url, id=None, parameters={}, body=None, request_method='GET'):

    if request_method.upper() in ['PUT', 'DELETE'] and not id:
        return {'success': False, 'message': 'ID was not supplied supplied for ' + str(request_method.upper() + ' request.')}
 
    url = "https://" + host + ":" + str(port) + base_url
    if id is not None:
        url = url + '/' + str(id)

    if len(parameters) > 0:
        url = url + "?" + urllib.parse.urlencode(parameters)

    auth=HTTPBasicAuth(username, password)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }
    
    if body:
        body = urllib.parse.urlencode(body)

    if request_method.upper() in ['GET', 'PUT', 'POST', 'DELETE']:
        try:
            resp = request(request_method, url, auth=auth, data=body, headers=headers, verify=False, timeout=2)
            if resp:
                if resp.status_code == 200:
                    result = {'success': True, 'response': cms_parse_response(resp)}

                    try:
                        result['id'] = resp.headers._store['location'][1][len(location)+1:]
                    except:
                        pass

                else:
                    failure_msg = json.loads(json.dumps(xmltodict.parse(resp.content)))
                    result = {'success': False, 'message': failure_msg}
            else:
                result = {'success': False, 'message': json.loads(json.dumps(xmltodict.parse(resp.content)))}
        
        except RequestException as e:
            result = {'success': False, 'message': str(e)}
                        
    else:
        result = {'success': False, 'message': 'Invalid verb ' + request_method}

    return result

def cms_parse_response(resp):
    """
    Parses the response contents of the body.  This would be present after a GET operation.

    Use this method to query for the CMS system status.
    """


    # response content converted to an ordered dictionary type
    if len(resp.content) == 0:
        try:
            return resp.headers._store['location'][1][len(resp.request.path_url)+1:]
        except KeyError:
            return json.loads(json.dumps({}))

    # Convert the XML to an ordered dictionary (a regular dictionary, that maintains a consisten order of 
    # elements, similar to a list)
    resp_odict = xmltodict.parse(resp.content)

    # One problem with xmltodict is that in 
    try:
        # Get the root key from the dictionary (e.g. 'coSpaces')
        rootName = list(resp_odict.keys())[0]

        # check if there is only one element, meaning xmltodict would not have created a list
        if(resp_odict[rootName]["@total"] == "1"):
            # Get the child key nested under the root (e.g. 'coSpace')
            childName = list(resp_odict[rootName].keys())[1]
            # Force the child element to be a list
            resp_odict = xmltodict.parse(resp.content, force_list={childName: True})

        # No elements, so just return a blank dictionary
        elif (len(resp_odict) == 0):
            return json.loads(json.dumps({}))

    # Maybe the @total key didn't exist; we'll just return the result
    except KeyError:
        pass 

    # convert from ordered dict to plain dict
    resp_dict = json.loads(json.dumps(resp_odict))
    return resp_dict
