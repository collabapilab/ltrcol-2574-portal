from requests import get, post, put, delete, packages,request
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import xmltodict
from flask import render_template
import base64
import json
import urllib.parse

packages.urllib3.disable_warnings(InsecureRequestWarning)


def cucm_get_version_api(host, username, password, port, location, parameters={}, body=None, request_method='GET'):
    pass

def cucm_find_phone_api(host, username, password, port, location, parameters={}, body=None, request_method='GET'):
    pass

def cucm_list_phones_api(host, username, password, port, location, parameters={}, body=None, request_method='GET'):
    pass

def cucm_add_phone_api(host, username, password, port, location, parameters={}, body=None, request_method='GET'):
    pass

def cucm_edit_phone_api(host, username, password, port, location, parameters={}, body=None, request_method='GET'):
    pass

def cucm_delete_phone_api(host, username, password, port, location, parameters={}, body=None, request_method='GET'):
    pass

