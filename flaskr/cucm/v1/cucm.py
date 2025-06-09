import requests
import re
import functools
import os
from time import sleep
from zeep.xsd.valueobjects import CompoundValue
from lxml import etree
from collections import OrderedDict
from flaskr.cucm.v1.axltoolkit import CUCMAxlToolkit, PawsToolkit, UcmRisPortToolkit, UcmServiceabilityToolkit, UcmPerfMonToolkit


def serialize_object(obj, target_cls=OrderedDict):
    """
    Serialize zeep objects to native python data structures.

    This helper function is used in place of zeep.helpers.serialize_object in order to handle the etree._Element types

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

    Wrapper class further extends CUCMAXLToolkit class to provide automated setup, retry, fault detection
    when making AXL API Calls to CUCM

    https://developer.cisco.com/docs/axl/

    :param host: The Hostname / IP Address of the server
    :param username: The username with CUCM AXL API access
    :param password: The password for your user account
    :type host: String
    :type username: String
    :type password: String
    :returns: return an AXL object
    :rtype: AXL
    """

    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.axlclient = None                   # This is the AXL Client Object (CUCMAxlToolkit from axltoolkit)
        self.axl_tls_verify = False             # Certificate validation check for HTTPs connection
        self.axl_version = "1.0"                # This is the default AXL version to try to find current version
        self.axl_timeout = 30                   # Default Timeout in Seconds awaiting for Response
        self.axl_attempts = 0                   # AXL Request Attempt Count
        self.axl_max_retries = 3                # AXL Request Max Number of Retries when throttled
        self.axl_backoff_times = [1, 5, 10]     # AXL Retry Request Backoff Timers in seconds. Invoked if we get throttling response 503
        self.axl_logging = False                # This controls the SOAP Request Logging to /tmp/axltoolkit.log

    class Decorators(object):
        """
        Inner Class holding Decorator methods for the parent Class

        These Static decorator methods enables us to:
            - Dynamically setup API Sessions and cache Authentication Cookie named JSESSIONIDSSO for subsequent requests.
                This enables us to re-use the Authenticated Session
            - Handle SOAP API Result validation, retry with backoff when requests are throttled,
                and dynamically covert Zeep/Soap objects to native python objects (serialize)
        """
        @staticmethod
        def axl_setup(func):
            """
            Decorator method that checks if we already have a client session setup,
            if not initiates AXL._axl_setup(), and then executes the original decorated class method and returns
            its return value.
            """
            @functools.wraps(func)
            def axl_setup_check(self, *args, **kwargs):
                if not self.axlclient:
                    self._axl_setup()
                value = func(self, *args, **kwargs)
                return value
            return axl_setup_check

        @staticmethod
        def axl_result_check_with_retry(func):
            """
            Decorator method that checks the results returned from the original method and re-tries it if
            failure reason is due to AXL throttling (HTTP Status 503). Otherwise if the original decorated class method
            returned value is None, it raises an Exception relaying the last SOAP exception message.

            All successful responses will be dynamically converted from Zeep/Soap objects to native python objects
            via the local serialize_object method.
            """
            @functools.wraps(func)
            def axl_result_check_wrapper(self, *args, **kwargs):
                while self.axl_attempts <= self.axl_max_retries:
                    try:
                        value = func(self, *args, **kwargs)
                        if value is None:
                            if self.axlclient.last_exception:
                                if "HTTP Status 503" in str(self.axlclient.last_exception.detail):
                                    if self.axl_attempts >= self.axl_max_retries:
                                        raise Exception(f"Received 503 -- AXL Throttling hit {self.axl_max_retries} times")
                                    sleep(self.axl_backoff_times[self.axl_attempts])
                                    self.axl_attempts += 1
                                else:
                                    raise Exception(str(self.axlclient.last_exception))
                        else:
                            return serialize_object(value)
                    except Exception as e:
                        self.axl_attempts = 0
                        raise Exception(e)
            return axl_result_check_wrapper

    def _axl_setup(self):
        """
        Internal AXL Class method which Tests and establishes AXL connection to a given VOS device.

        Calls _axl_get_schema which initializes self.axlclient if AXL Services are up and if user is authenticated.

        If AXL Services are not running or if user is not authorized Raise Exception with appropriate error.

        """
        axl_test_url = "https://" + self.host + "/axl"
        r = requests.get(axl_test_url,
                         auth=(self.username, self.password),
                         timeout=self.axl_timeout,
                         verify=self.axl_tls_verify)
        if r.status_code == 404:
            raise Exception("AXL Services Not Running: " + str(r.status_code) + " - " + r.reason)
        if r.status_code == 401:
            raise Exception("AXL Authentication error " + str(r.status_code) + " - " + r.reason)
        if r.status_code == 200:
            self._axl_set_schema()
        else:
            raise Exception("AXL Connectivity Exception:" + str(r.status_code) + " - " + r.reason)

    def _axl_set_schema(self):
        """
        Internal AXL Class method which detects the CUCM version and instantiates the CUCMAxlToolkit with the
        appropriate WSDL file.

        First we use the Default AXL Version self.axl_version and run getCCMVersion AXL request.

        Strip the major version from the response. ie: 11.5 or 12.5

        Initialize the self.axlclient with the current CUCM version

        """
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

    @Decorators.axl_result_check_with_retry
    @Decorators.axl_setup
    def add_phone(self, phone_data=None):
        axl_result = self.axlclient.add_phone(phone_data=phone_data)
        return axl_result

    @Decorators.axl_result_check_with_retry
    @Decorators.axl_setup
    def get_phone(self, name=None):
        axl_result = self.axlclient.get_phone(name)
        return axl_result

    @Decorators.axl_result_check_with_retry
    @Decorators.axl_setup
    def delete_phone(self, name=None):
        axl_result = self.axlclient.remove_phone(name)
        return axl_result

    @Decorators.axl_result_check_with_retry
    @Decorators.axl_setup
    def apply_phone(self, name=None):
        axl_result = self.axlclient.apply_phone(name)
        return axl_result

    @Decorators.axl_result_check_with_retry
    @Decorators.axl_setup
    def list_phone(self, search_criteria_data=None, returned_tags=None):
        axl_result = self.axlclient.list_phone(search_criteria_data, returned_tags)
        if axl_result['return'] is None:
            raise Exception("List Phone did not return any Results given the search criteria")
        return axl_result

    @Decorators.axl_result_check_with_retry
    @Decorators.axl_setup
    def update_phone(self, phone_data=None):
        axl_result = self.axlclient.update_phone(phone_data=phone_data)
        return axl_result

    @Decorators.axl_result_check_with_retry
    @Decorators.axl_setup
    def update_line(self, line_data=None):
        axl_result = self.axlclient.update_line(line_data=line_data)
        return axl_result

    @Decorators.axl_result_check_with_retry
    @Decorators.axl_setup
    def apply_line(self, dn=None, partition=None):
        axl_result = self.axlclient.apply_line(dn=dn, partition=partition)
        return axl_result

    @Decorators.axl_result_check_with_retry
    @Decorators.axl_setup
    def get_user(self, userid=None):
        axl_result = self.axlclient.get_user(userid=userid)
        return axl_result

    @Decorators.axl_result_check_with_retry
    @Decorators.axl_setup
    def update_user(self, user_data=None):
        axl_result = self.axlclient.update_user(user_data=user_data)
        return axl_result


class PAWS:
    """
    The VOS Platform Administrative Web Services (PAWS) class

    Wrapper class further extends PawsToolkit class to provide automated setup, fault detection when making PAWS API Calls to CUCM

    https://developer.cisco.com/site/paws/documents/api-reference/

    :param host: The Hostname / IP Address of the server
    :param username: The username of an account with access to the API.
    :param password: The password for your user account
    :param service: The PAWS API Service Name
    :type host: String
    :type username: String
    :type password: String
    :type service: String
    :returns: return an PAWS object
    :rtype: PAWS
    """

    def __init__(self, host, username, password, service):
        self.host = host
        self.username = username
        self.password = password
        self.pawsclient = None        # This is the PAWS Client Object (PawsToolkit from axltoolkit)
        self.paws_tls_verify = False  # Certificate validation check for HTTPs connection
        self.paws_timeout = 30        # Default Timeout in Seconds awaiting for Response
        self.service = service        # This is the PAWS Service Name (ie: VersionService, ClusterNodesService)
        self.paws_logging = False     # This controls the SOAP Request Logging to /tmp/axltoolkit.log

    class Decorators(object):
        """
        Inner Class holding Decorator methods for the parent Class

        These Static decorator methods enables us to:
            - Dynamically setup API Sessions and cache Authentication Cookie named JSESSIONIDSSO for subsequent requests.
                This enables us to re-use the Authenticated Session
            - Handle SOAP API Result validation, and dynamically covert Zeep/Soap objects to native python objects (serialize)
        """
        @staticmethod
        def paws_setup(func):
            """
            Decorator method that checks if we already have a client session setup,
            if not initiates AXL._paws_setup(), and then executes the original decorated class method and returns
            its return value.
            """
            @functools.wraps(func)
            def paws_setup_check(self, *args, **kwargs):
                if not self.pawsclient:
                    self._paws_setup()
                value = func(self, *args, **kwargs)
                return value
            return paws_setup_check

        @staticmethod
        def paws_result_check(func):
            """
            Decorator method that checks the results returned from the original method, if the original decorated class method
            returned value is None, it raises an Exception relaying the last SOAP exception message.

            All successful responses will be dynamically converted from Zeep/Soap objects to native python objects
            via the local serialize_object method.
            """
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
        Internal PAWS Class method which Tests and establishes PAWS connection to a given VOS device.

        If PAWS Services are up and if user is authenticated initializes self.pawsclient with a new PawsToolkit
        for the chosen PAWS API Service (ie: VersionService, ClusterNodeServices)

        If PAWS Services are not running or if user is not authorized Raise Exception with appropriate error.

        """
        paws_test_url = "https://" + self.host + "/platform-services/services/listServices"
        r = requests.get(paws_test_url,
                         auth=(self.username, self.password),
                         timeout=self.paws_timeout,
                         verify=self.paws_tls_verify)
        if r.status_code == 404:
            raise Exception("PAWS Services Not Running: " + str(r.status_code) + " - " + r.reason)
        if r.status_code == 401:
            raise Exception("PAWS Authentication error " + str(r.status_code) + " - " + r.reason)
        if r.status_code == 200:
            self.pawsclient = PawsToolkit(username=self.username, password=self.password,
                                          server_ip=self.host, service=self.service,
                                          tls_verify=self.paws_tls_verify, timeout=self.paws_timeout,
                                          logging_enabled=self.paws_logging)
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

    Wrapper class further extends multiple serviceability API classes from axltoolkit module to provide automated
    setup, retry, fault detection when making SXML API Calls to CUCM

    https://developer.cisco.com/docs/sxml/

    :param host: The Hostname / IP Address of the server
    :param username: The username of an account with access to the API.
    :param password: The password for your user account
    :param service: The SXML API Service Name
    :type host: String
    :type username: String
    :type password: String
    :type service: String
    :returns: return an SXML object
    :rtype: SXML
    """

    def __init__(self, host, username, password, service):
        self.host = host
        self.username = username
        self.password = password
        self.sxmlclient = None        # This is the PAWS Client Object
        self.sxml_tls_verify = False  # TLS Verify on PAWS HTTPS connections
        self.sxml_timeout = 30        # Default Timeout in Seconds for PAWS Queries
        self.service = service        # This is the SXML Service Name (ie: UcmRisPortToolkit, UcmServiceabilityToolkit, UcmPerfMonToolkit)
        self.sxml_logging = False     # This controls the SOAP Logging
        self.service_map = {          # This maps Service Names to Service Test URLs and axltoolkit Classes
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
        """
        Inner Class holding Decorator methods for the parent Class

        These Static decorator methods enables us to:
            - Dynamically setup API Sessions depending on the SXML Service Type, cache Authentication
                Cookie named JSESSIONIDSSO for subsequent requests. This enables us to re-use the Authenticated Session
            - Handle SOAP API Result validation, and dynamically covert Zeep/Soap objects to native python objects (serialize)
        """
        @staticmethod
        def sxml_setup(service=None):
            """
            Decorator method that checks if we already have a client session setup and the right type/instance
            if not initiates SXML._sxml_setup() with the chosen SXML service, and then executes the original
            decorated class method and returns its return value.
            """
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
            """
            Decorator method that checks the results returned from the original method, if the original decorated class method
            returned value is None, it raises an Exception relaying the last SOAP exception message.

            All successful responses will be dynamically converted from Zeep/Soap objects to native python objects
            via the local serialize_object method.
            """
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
        Internal SXML Class method which Tests and establishes SXML connection to a given VOS device.

        If given SXML Service is up and if user is authenticated initializes self.sxmlclient with a mapped axltoolkit
        class for the chosen SXML API Service (ie: UcmRisPortToolkit, UcmServiceabilityToolkit, UcmPerfMonToolkit)

        If given SXML Service is not running or if user is not authorized Raise Exception with appropriate error.

        """
        sxml_test_url = "https://" + self.host + self.service_map[service]['service_test_url']
        r = requests.get(sxml_test_url,
                         auth=(self.username, self.password),
                         timeout=self.sxml_timeout,
                         verify=self.sxml_tls_verify)
        if r.status_code == 404:
            raise Exception("SXML Services Not Running: " + str(r.status_code) + " - " + r.reason)
        if r.status_code == 401:
            raise Exception("SXML Authentication error " + str(r.status_code) + " - " + r.reason)
        if r.status_code == 200:
            self.sxmlclient = self.service_map[service]['toolkit'](
                    username=self.username, password=self.password, server_ip=self.host, tls_verify=self.sxml_tls_verify,
                    timeout=self.sxml_timeout, logging_enabled=self.sxml_logging)
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
    def perfmon_query_class(self, host=None, perfmon_class_name=None):
        if host is None:
            host = self.host
        return self.sxmlclient.perfmon_collect_counter_data(host, perfmon_class_name)

    @Decorators.sxml_result_check
    @Decorators.sxml_setup(service="perfmonservice2")
    def perfmon_open_session(self):
        return self.sxmlclient.perfmon_open_session()

    @Decorators.sxml_result_check
    @Decorators.sxml_setup(service="perfmonservice2")
    def perfmon_close_session(self, session_handle=None):
        return self.sxmlclient.perfmon_close_session(session_handle)

    @Decorators.sxml_result_check
    @Decorators.sxml_setup(service="perfmonservice2")
    def perfmon_add_counter(self, session_handle=None, counters=None):
        return self.sxmlclient.perfmon_add_counter(session_handle, counters)

    @Decorators.sxml_result_check
    @Decorators.sxml_setup(service="perfmonservice2")
    def perfmon_collect_session_data(self, session_handle=None):
        return self.sxmlclient.perfmon_collect_session_data(session_handle)
