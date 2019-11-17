from requests import get, post, put, delete, request, packages
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException
import xmltodict
import json
import urllib.parse
import urllib3
import xml.etree.ElementTree as ET
from .axltoolkit import CUCMAxlToolkit, IMPAxlToolkit, PawsToolkit

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

default_cucm = {
   'host': '10.0.131.41',
   'port': 8443,
   'username': 'admin',
   'password': 'c1sco123'
}

pawsclient = PawsToolkit(username=default_cucm['username'], password=default_cucm['password'], server_ip=default_cucm['host'],
                         service="VersionService", tls_verify=False, timeout=30)

def cucm_get_version(host, username, password, port):
    paws_response = pawsclient.get_active_version()
    # try:
    result = { 'success': True, 'response': {'version': paws_response['version']} }
    return result

def cucm_find_phone(host, username, password, port, location, parameters={}, body=None, request_method='GET'):
    pass

def cucm_list_phones(host, username, password, port, location, parameters={}, body=None, request_method='GET'):
    pass

def cucm_add_phone(host, username, password, port, location, parameters={}, body=None, request_method='GET'):
    pass

def cucm_edit_phone(host, username, password, port, location, parameters={}, body=None, request_method='GET'):
    pass

def cucm_delete_phone(host, username, password, port, location, parameters={}, body=None, request_method='GET'):
    pass