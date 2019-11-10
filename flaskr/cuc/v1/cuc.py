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

default_cuc = {
   'host': 'cuc1a.pod31.col.lab',
   'port': 443,
   'username': 'admin',
   'password': 'c1sco123'
}


def cuc_parse_params(params):
    if len(params) == 0:
        return ''

    # query = (column[is | startswith] value)
    # args: -> ?query=alias&is=operator;  ?filter=operator&match=exact  query=(alias%20is%20operator)
    # ?query=(dtmfaccessid%20startswith%2099999) <--> ?filter=2099999&match=exact
    # base_url = '/vmrest/users?query=(alias%20is%20operator)'

    # query=(alias startswith a)
    # sort=(column [asc | desc])
    # space = %20 ; 
    # ?filter=2099999&match=exact&sortorder=asc

    # ?column=dtmfaccessid&filter=99999&match=is
    # ?filter=operator

    try:
        filter = params['filter']
        if filter == '':
            return ''
    except KeyError:
        # No filter found.  Just encode whatever dictionary was sent
        url_param = urllib.parse.urlencode(params)
        if url_param:
            url_param = '?' + url_param
        return url_param

    # column to search
    column = 'alias'
    # 'startswith' or is'
    match_method = 'startswith'
    # sort order 'asc' or 'desc'
    sortorder = 'asc'

    # result will be:  ?query=(<column> <matchmethod> <filter>)&sortorder=(<column>=<sortorder>)
    # (with spaces replaced with %20 ) for example:
    # ?filter=operat  would be converted to:  ?query=(alias%20startswith%20operat)&sortorder=(alias=asc)
    # 
    #  ?column=dtmfaccessid&filter=99999&match=is

    # ?filter=operator  - would find all users whose alias that start with operator (operator, operator1, etc)
    # ?filter=operator&match=is  - would find a user whose alias  is exactly 'operator'
    # ?filter=99999&column=dtmfaccessid&match=is  - would find the user with dtmfaccessid = 99999

    try:
        if params['match'] in ['is', 'startswith']:
            match_method = params['match']
    except KeyError:
        pass
    try:
        column = params['column']
    except KeyError:
        pass
    try:
        if params['sortorder'] in ['asc', 'desc']:
            sortorder = params['sortorder']
    except KeyError:
        pass

    url_param = '?query=({}%20{}%20{})&sort=({}%20{})'.format(
        column, match_method, filter, column, sortorder)

    return url_param


def cuc_send_request(host, username, password, port, base_url, id=None, parameters={}, body=None, request_method='GET'):

    if request_method.upper() in ['PUT', 'DELETE'] and not id:
        return {'success': False, 'message': 'ID was not supplied supplied for ' + str(request_method.upper() + ' request.')}
    url = "https://" + host + ":" + str(port) + base_url
    if id is not None:
        url = url + '/' + str(id)

    # if len(parameters) > 0:
    #     url = url + "?" + cuc_parse_params(parameters)
    url = url + cuc_parse_params(parameters)

    auth = HTTPBasicAuth(username, password)

    # DIFFERENT FROM CMS
    headers = {
        'Content-Type': 'application/json',
        'Connection': 'keep-alive'
    }

    if body:
        # body = urllib.parse.urlencode(body)
        body = json.dumps(body)

    if request_method.upper() in ['GET', 'PUT', 'POST', 'DELETE']:
        try:
            resp = request(request_method, url, auth=auth,
                           data=body, headers=headers, verify=False, timeout=2)
            if resp:
                if resp.status_code == 200:
                    result = {'success': True,
                              'response': cuc_parse_response(resp)}

                    try:
                        result['id'] = resp.headers._store['location'][1][len(
                            location)+1:]
                    except:
                        pass
                elif resp.status_code in [201, 204]:
                    result = {'success': True,
                              'response': resp.content.decode("utf-8")}
                else:
                    failure_msg = json.loads(
                        json.dumps(xmltodict.parse(resp.content)))
                    result = {'success': False, 'message': failure_msg}
            else:
                result = {'success': False, 'message': json.loads(
                    json.dumps(xmltodict.parse(resp.content)))}

        except RequestException as e:
            result = {'success': False, 'message': str(e)}

    else:
        result = {'success': False,
                  'message': 'Invalid verb ' + request_method}

    return result


def cuc_parse_response(resp):
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
            resp_odict = xmltodict.parse(
                resp.content, force_list={childName: True})

        # No elements, so just return a blank dictionary
        elif (len(resp_odict) == 0):
            return json.loads(json.dumps({}))

    # Maybe the @total key didn't exist; we'll just return the result
    except KeyError:
        pass

    # convert from ordered dict to plain dict
    resp_dict = json.loads(json.dumps(resp_odict))
    return resp_dict


def cuc_get_version(host, username, password, port, base_url, parameters={}, body=None, request_method='GET'):
    pass


def cuc_list_mailboxes(host, username, password, port, base_url, parameters={}, body=None, request_method='GET'):
    pass


def cuc_find_mailbox(host, username, password, port, base_url, parameters={}, body=None, request_method='GET'):
    pass


def cuc_add_mailbox(host, username, password, port, base_url, parameters={}, body=None, request_method='GET'):
    pass


def cuc_edit_mailbox(host, username, password, port, base_url, parameters={}, body=None, request_method='GET'):
    pass


def cuc_delete_mailbox(host, username, password, port, base_url, parameters={}, body=None, request_method='GET'):
    pass
