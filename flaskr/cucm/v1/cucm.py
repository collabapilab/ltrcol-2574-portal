import requests
import re
import functools
import os
from zeep.xsd.valueobjects import CompoundValue
from lxml import etree
from collections import OrderedDict
from flaskr.cucm.v1.axltoolkit import CUCMAxlToolkit, PawsToolkit, UcmRisPortToolkit, UcmServiceabilityToolkit, UcmPerfMonToolkit


def serialize_object(obj, target_cls=OrderedDict):
    """
    Serialize zeep objects to native python data structures.

    This helper function is used inplace of zeep.helpers.serialize_object in order to handle the etree._Element types

    :Parameters:
        - obj (any) - Object to be serialized
        - target_cls (collection) - Type of object to serialize to. Defaults to OrderedDict

    :Returns:
        - (obj) - A Python Native Data Structured Object (str, list, dict)

    **Doctest**::

    """

    if isinstance(obj, list):
        return [serialize_object(sub, target_cls) for sub in obj]

    if isinstance(obj, etree._Element):
        def recursive_dict(element):
            return element.tag[element.tag.find('}') + 1:], dict(map(recursive_dict, element)) or element.text
        return recursive_dict(obj)

    if isinstance(obj, (dict, CompoundValue)):
        result = target_cls()
        for key in obj:
            result[key] = serialize_object(obj[key], target_cls)
        return result

    return obj


class AXL:
    """
    The CUCM AXL class

    Use this class to connect and make AXL API Calls to CUCM

    :param host: The Hostname / IP Address of the server
    :param username: The username of an account with access to the API.
    :param password: The password for your user account
    :param port: (optiona) The server port for API access (default: 443)
    :type host: String
    :type username: String
    :type password: String
    :type port: Integer
    :returns: return an AXL object
    :rtype: AXL
    """

    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.axlclient = None           # This is the AXL Client Object
        self.axl_tls_verify = False     # TLS Verify on AXL HTTPS connections
        self.axl_version = "10.0"       # This is the default AXL version we will use
        self.axl_timeout = 30           # Default Timeout in Seconds for AXL Queries
        self.axl_logging = False        # This controls the SOAP Logging

    class Decorators(object):
        @staticmethod
        def axl_setup(func):
            @functools.wraps(func)
            def axl_setup_check(self, *args, **kwargs):
                if not self.axlclient:
                    self._axl_setup()
                value = func(self, *args, **kwargs)
                return value
            return axl_setup_check

        @staticmethod
        def axl_result_check(func):
            @functools.wraps(func)
            def axl_result_check_wrapper(self, *args, **kwargs):
                value = func(self, *args, **kwargs)
                if value is None:
                    if self.axlclient.last_exception:
                        raise Exception(str(self.axlclient.last_exception))
                return serialize_object(value)
            return axl_result_check_wrapper

    def _axl_setup(self):
        """
        Tests and establishes AXL connection to a given VOS device. Initializes self.axlclient if successful

        If AXL Services are not running or if we are not authorized we fail

        """
        axl_test_url = "https://" + self.host + "/axl"
        r = requests.get(axl_test_url,
                         auth=(self.username, self.password),
                         timeout=self.axl_timeout,
                         verify=False)
        if r.status_code == 404:
            raise Exception("AXL Services Not Running: " + str(r.status_code) + " - " + r.reason)
        if r.status_code == 401:
            raise Exception("AXL Authentication error " + str(r.status_code) + " - " + r.reason)
        if r.status_code == 200:
            self._axl_set_schema()
        else:
            raise Exception("AXL Connectivity Exception:" + str(r.status_code) + " - " + r.reason)

    def _axl_set_schema(self):
        schema_folder_path = os.path.dirname(os.path.realpath(__file__)) + "/axltoolkit/"
        self.axlclient = CUCMAxlToolkit(username=self.username, password=self.password,
                                        server_ip=self.host, version=self.axl_version,
                                        tls_verify=self.axl_tls_verify, timeout=self.axl_timeout,
                                        logging_enabled=self.axl_logging, schema_folder_path=schema_folder_path
                                        )
        ccm_version = self.axlclient.get_ccm_version()
        if ccm_version:
            axl_version = re.findall(r'^\d+\.\d+', ccm_version)[0]
            self.axlclient = CUCMAxlToolkit(username=self.username, password=self.password,
                                            server_ip=self.host, version=axl_version,
                                            tls_verify=self.axl_tls_verify, timeout=self.axl_timeout,
                                            logging_enabled=self.axl_logging, schema_folder_path=schema_folder_path)
        else:
            if self.axlclient.last_exception:
                raise Exception("Exception with get_ccm_version --- " + str(self.axlclient.last_exception))

    @Decorators.axl_result_check
    @Decorators.axl_setup
    def add_phone(self, phone_data=None):
        axl_result = self.axlclient.add_phone(phone_data=phone_data)
        return axl_result

    @Decorators.axl_result_check
    @Decorators.axl_setup
    def get_phone(self, name=None):
        axl_result = self.axlclient.get_phone(name)
        return axl_result

    @Decorators.axl_result_check
    @Decorators.axl_setup
    def delete_phone(self, name=None):
        axl_result = self.axlclient.remove_phone(name)
        return axl_result

    @Decorators.axl_result_check
    @Decorators.axl_setup
    def apply_phone(self, name=None):
        axl_result = self.axlclient.apply_phone(name)
        return axl_result

    @Decorators.axl_result_check
    @Decorators.axl_setup
    def list_phone(self, search_criteria_data=None, returned_tags=None):
        axl_result = self.axlclient.list_phone(search_criteria_data, returned_tags)
        if axl_result['return'] is None:
            raise Exception("List Phone did not return any Results given the search criteria")
        return axl_result

    @Decorators.axl_result_check
    @Decorators.axl_setup
    def update_phone(self, phone_data=None):
        axl_result = self.axlclient.update_phone(phone_data=phone_data)
        return axl_result

    @Decorators.axl_result_check
    @Decorators.axl_setup
    def get_user(self, userid=None):
        axl_result = self.axlclient.get_user(userid=userid)
        return axl_result

    @Decorators.axl_result_check
    @Decorators.axl_setup
    def update_user(self, user_data=None):
        axl_result = self.axlclient.update_user(user_data=user_data)
        return axl_result


class PAWS:
    """
    The CUCM PAWS class

    Use this class to connect and make PAWS API Calls to CUCM

    https://developer.cisco.com/site/paws/documents/api-reference/

    :param host: The Hostname / IP Address of the server
    :param username: The username of an account with access to the API.
    :param password: The password for your user account
    :param port: (optiona) The server port for API access (default: 443)
    :type host: String
    :type username: String
    :type password: String
    :type port: Integer
    :returns: return an PAWS object
    :rtype: PAWS
    """

    def __init__(self, host, username, password, service):
        self.host = host
        self.username = username
        self.password = password
        self.service = service
        self.pawsclient = None        # This is the PAWS Client Object
        self.paws_tls_verify = False  # TLS Verify on PAWS HTTPS connections
        self.paws_timeout = 30        # Default Timeout in Seconds for PAWS Queries
        self.paws_logging = False     # This controls the SOAP Logging

    class Decorators(object):
        @staticmethod
        def paws_setup(func):
            @functools.wraps(func)
            def paws_setup_check(self, *args, **kwargs):
                if not self.pawsclient:
                    self._paws_setup()
                value = func(self, *args, **kwargs)
                return value
            return paws_setup_check

        @staticmethod
        def paws_result_check(func):
            @functools.wraps(func)
            def paws_result_check_wrapper(self, *args, **kwargs):
                value = func(self, *args, **kwargs)
                if value is None:
                    if self.pawsclient.last_exception:
                        raise Exception(str(self.pawsclient.last_exception))
                return serialize_object(value)
            return paws_result_check_wrapper

    def _paws_setup(self):
        """
        Tests and establishes PAWS connection to a given VOS device. Initializes self.pawsclient if successful

        If PAWS Services are not running or if we are not authorized we fail

        """
        paws_test_url = "https://" + self.host + "/platform-services/services/listServices"
        r = requests.get(paws_test_url,
                         auth=(self.username, self.password),
                         timeout=self.paws_timeout,
                         verify=False)
        if r.status_code == 404:
            raise Exception("PAWS Services Not Running: " + str(r.status_code) + " - " + r.reason)
        if r.status_code == 401:
            raise Exception("PAWS Authentication error " + str(r.status_code) + " - " + r.reason)
        if r.status_code == 200:
            self.pawsclient = PawsToolkit(username=self.username, password=self.password,
                                          server_ip=self.host, service=self.service,
                                          tls_verify=self.paws_tls_verify, timeout=self.paws_timeout)
        else:
            raise Exception("PAWS Connectivity Exception:" + str(r.status_code) + " - " + r.reason)

    @Decorators.paws_result_check
    @Decorators.paws_setup
    def get_version(self, Version='Active'):
        if (Version == 'Active'):
            return self.pawsclient.get_active_version()
        elif (Version == 'Inactive'):
            return self.pawsclient.get_inactive_version()
        else:
            raise Exception("get_version only accepts 'Active' or 'Inactive'")


class SXML:
    """
    The CUCM Serviceability XML API

    Use this class to connect and make Serviceability XML API Calls to CUCM

    https://developer.cisco.com/docs/sxml/

    :param host: The Hostname / IP Address of the server
    :param username: The username of an account with access to the API.
    :param password: The password for your user account
    :param port: (optiona) The server port for API access (default: 443)
    :type host: String
    :type username: String
    :type password: String
    :type port: Integer
    :returns: return an SXML object
    :rtype: SXML
    """

    def __init__(self, host, username, password, service):
        self.host = host
        self.username = username
        self.password = password
        self.service = service
        self.sxmlclient = None        # This is the PAWS Client Object
        self.sxml_tls_verify = False  # TLS Verify on PAWS HTTPS connections
        self.sxml_timeout = 30        # Default Timeout in Seconds for PAWS Queries
        self.sxml_logging = False     # This controls the SOAP Logging
        self.service_map = {
            "realtimeservice2": {
                "service_test_url": "/realtimeservice2/services/listServices",
                "toolkit": UcmRisPortToolkit
            },
            "controlcenterservice2": {
                "service_test_url": "/controlcenterservice2/services/listServices",
                "toolkit": UcmServiceabilityToolkit
            },
            "CDRonDemandService2": {
                "service_test_url": "/CDRonDemandService2/services/listServices",
                "toolkit": ""
            },
            "logcollectionservice2": {
                "service_test_url": "/logcollectionservice2/services/listServices",
                "toolkit": ""
            },
            "logcollectionservice": {
                "service_test_url": "/logcollectionservice/services",
                "toolkit": ""
            },
            "perfmonservice2": {
                "service_test_url": "/perfmonservice2/services/listServices",
                "toolkit": UcmPerfMonToolkit
            }
        }

    class Decorators(object):
        @staticmethod
        def sxml_setup(service=None):
            def decorator(func):
                @functools.wraps(func)
                def sxml_setup_check(self, *args, **kwargs):
                    if not isinstance(self.sxmlclient, self.service_map[service]['toolkit']):
                        self._sxml_setup(service=service)
                    value = func(self, *args, **kwargs)
                    return value
                return sxml_setup_check
            return decorator

        @staticmethod
        def sxml_result_check(func):
            @functools.wraps(func)
            def sxml_result_check_wrapper(self, *args, **kwargs):
                value = func(self, *args, **kwargs)
                if value is None:
                    if self.sxmlclient.last_exception:
                        raise Exception(str(self.sxmlclient.last_exception))
                return serialize_object(value)
            return sxml_result_check_wrapper

    def _sxml_setup(self, service=None):
        """
        Tests and establishes UC Manager Serviceability (SXML) Service connection to a given VOS device. Initializes self.sxmlclient if successful

        If given UC Manager Serviceability (SXML) Service is not running or if we are not authorized we fail

        """
        sxml_test_url = "https://" + self.host + self.service_map[service]['service_test_url']
        r = requests.get(sxml_test_url,
                         auth=(self.username, self.password),
                         timeout=self.sxml_timeout,
                         verify=False)
        if r.status_code == 404:
            raise Exception("SXML Services Not Running: " + str(r.status_code) + " - " + r.reason)
        if r.status_code == 401:
            raise Exception("SXML Authentication error " + str(r.status_code) + " - " + r.reason)
        if r.status_code == 200:
            self.sxmlclient = self.service_map[service]['toolkit'](
                    username=self.username, password=self.password, server_ip=self.host, tls_verify=self.sxml_tls_verify, timeout=self.sxml_timeout)
        else:
            raise Exception("SXML Connectivity Exception:" + str(r.status_code) + " - " + r.reason)

    @Decorators.sxml_result_check
    @Decorators.sxml_setup(service="realtimeservice2")
    def ris_query(self, search_criteria=None):
        return self.sxmlclient.get_service().selectCmDevice(StateInfo='', CmSelectionCriteria=search_criteria)

    @Decorators.sxml_result_check
    @Decorators.sxml_setup(service="controlcenterservice2")
    def ccs_get_service_status(self, service_list=None):
        # We must send at least a blank ServiceStatus so init a blank list before sending it to soapGetServiceStatus
        if service_list is None or len(service_list) == 0:
            service_list = [""]
        return self.sxmlclient.get_service().soapGetServiceStatus(ServiceStatus=service_list)

    @Decorators.sxml_result_check
    @Decorators.sxml_setup(service="perfmonservice2")
    def perfmon_query(self, host=None, perfmon_object=None):
        if host is None:
            host = self.host
        return self.sxmlclient.perfmonCollectCounterData(host, perfmon_object)
