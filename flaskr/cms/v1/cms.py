from requests import get, post, put, delete, packages,request
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.exceptions import RequestException
import xmltodict
from flask import jsonify
from flask import render_template
import base64
import json
import urllib.parse

packages.urllib3.disable_warnings(InsecureRequestWarning)

default_cms = {
   'host': 'cms1a.pod31.col.lab',
   'port': 8443,
   'username': 'admin',
   'password': 'c1sco123'
}


def cms_send_request(host, username, password, port, location, parameters={}, body=None, request_method='GET'):

    url = "https://" + host + ":" + str(port) + str(location)
    if len(parameters) > 0:
        url = url + "?" + urllib.parse.urlencode(parameters)
    auth=HTTPBasicAuth(username, password)

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }
    
    if body:
        body = urllib.parse.urlencode(body)

    if request_method.lower() in ['get', 'put', 'post', 'delete']:
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
                # result = {'success': False, 'message': resp.reason}
        
        except RequestException as e:
            result = {'success': False, 'message': str(e)}
                        
    else:
        result = jsonify({'success': False, 'message': 'Invalid verb ' + request_method})

    return result

def cms_parse_response(resp):
    # response content converted to an ordered dictionary type
    if len(resp.content) == 0:
        return
    resp_odict = xmltodict.parse(resp.content)
    try:
        rootName = list(resp_odict.keys())[0]
        root = resp_odict[rootName]
        if(root["@total"] == "1"):
            li = list()
            childName = list(root.keys())[1]

            li.append(root[childName].copy())

            root[childName] = li
            resp_odict[rootName] = root

            return json.loads(json.dumps(resp_odict))

        elif(len(resp_odict) == 0):
            return {}

            #pp.pprint(root)
            #We need to make it a list
    except KeyError:
        pass 
    # convert from ordered dict to plain dict
    resp_dict = json.loads(json.dumps(resp_odict))
    return resp_dict
