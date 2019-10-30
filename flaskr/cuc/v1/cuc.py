from requests import get, post, put, delete, packages,request
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import xmltodict
from flask import render_template
import base64
import json
import urllib.parse

packages.urllib3.disable_warnings(InsecureRequestWarning)


def cuc_get_version_api(host, username, password, port, location, parameters={}, body=None, request_method='GET'):
    pass

def cuc_list_mailboxes_api(host, username, password, port, location, parameters={}, body=None, request_method='GET'):
    pass

def cuc_find_mailbox_api(host, username, password, port, location, parameters={}, body=None, request_method='GET'):
    pass

def cuc_add_mailbox_api(host, username, password, port, location, parameters={}, body=None, request_method='GET'):
    pass

def cuc_edit_mailbox_api(host, username, password, port, location, parameters={}, body=None, request_method='GET'):
    pass

def cuc_delete_mailbox_api(host, username, password, port, location, parameters={}, body=None, request_method='GET'):
    pass

