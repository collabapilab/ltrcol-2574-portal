from lxml import etree
from zeep import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport
from zeep.plugins import HistoryPlugin
from requests import Session
from requests.auth import HTTPBasicAuth
import urllib3
import logging.config
import logging
import os
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AXLHistoryPlugin(HistoryPlugin):
    """
        Extends Zeep HistoryPlugin for easy xml extraction
    """

    @staticmethod
    def _parse_envelope(envelope):
        return etree.tostring(envelope, encoding="unicode", pretty_print=True)

    @property
    def last_received_xml(self):
        last_tx = self._buffer[-1]
        if last_tx:
            return self._parse_envelope(last_tx['received']['envelope'])

    @property
    def last_sent_xml(self):
        last_tx = self._buffer[-1]
        if last_tx:
            return self._parse_envelope(last_tx['sent']['envelope'])


class AxlToolkit:
    """
    The AxlToolkit Common AXL SOAP API class
    This Parent class enables us to connect and make SOAP API calls to CUCM & IM&P utilizing Zeep Python Package as the SOAP Client

    :param username: The username used for Basic HTTP Authentication
    :param password: The password used for Basic HTTP Authentication
    :param server_ip: The Hostname / IP Address of the server
    :param version: (optional) The major version of CUCM / IM&P Cluster (default: 12.5)
    :param tls_verify: (optional) Certificate validation check for HTTPs connection (default: True)
    :param timeout: (optional) Zeep Client Transport Response Timeout in seconds (default: 10)
    :param logging_enabled: (optional) Zeep SOAP message Logging (default: False)
    :param schema_folder_path: (optional) Sub Directory Location for AXL schema versions (default: None)
    :type username: str
    :type password: str
    :type server_ip: str
    :type version: str
    :type tls_verify: bool
    :type timeout: int
    :type logging_enabled: bool
    :type schema_folder_path: str
    :returns: return an AxlToolkit object
    :rtype: AxlToolkit
    """

    def __init__(self, username, password, server_ip, version='12.5', tls_verify=True, timeout=10,
                 logging_enabled=False, schema_folder_path=None):
        """

        Constructor - Create new instance

        """

        self.session = Session()
        self.session.auth = HTTPBasicAuth(username, password)
        self.session.verify = tls_verify
        self.history = AXLHistoryPlugin(maxlen=1)
        self.wsdl = None
        self.last_exception = None

        filedir = os.path.dirname(__file__)
        if schema_folder_path is not None:
            filedir = schema_folder_path

        self.cache = SqliteCache(path='/tmp/sqlite_axl_{0}.db'.format(server_ip), timeout=60)

        if version == '1.0':
            self.wsdl = os.path.join(filedir, 'schema/1.0/AXLAPI.wsdl')  
        elif version == '12.5':
            self.wsdl = os.path.join(filedir, 'schema/12.5/AXLAPI.wsdl')
        elif version == '12.0':
            self.wsdl = os.path.join(filedir, 'schema/12.0/AXLAPI.wsdl')
        elif version == '11.5':
            self.wsdl = os.path.join(filedir, 'schema/11.5/AXLAPI.wsdl')
        elif version == '11.0':
            self.wsdl = os.path.join(filedir, 'schema/11.0/AXLAPI.wsdl')
        elif version == '10.5':
            self.wsdl = os.path.join(filedir, 'schema/10.5/AXLAPI.wsdl')
        elif version == '10.0':
            self.wsdl = os.path.join(filedir, 'schema/10.0/AXLAPI.wsdl')
        else:
            self.wsdl = os.path.join(filedir, 'schema/12.5/AXLAPI.wsdl')

        self.client = Client(wsdl=self.wsdl, plugins=[self.history],
                             transport=Transport(timeout=timeout, operation_timeout=timeout,
                             cache=self.cache, session=self.session))
        # Update the Default SOAP API Binding Address Location with server_ip for all API Service Endpoints
        # Default: (https://CCMSERVERNAME:8443/axl/)
        self.service = self.client.create_service("{http://www.cisco.com/AXLAPIService/}AXLAPIBinding",
                                                  "https://{0}:8443/axl/".format(server_ip))

        if logging_enabled:
            self._enable_logging()

    @staticmethod
    def _enable_logging():
        """
        Enables Logging of SOAP Request and Response Payloads to /tmp/axltoolkit.log

        Use http://xmlprettyprint.com/ to help with SOAP XML payloads

        Its a staticmethod in order to allow other classes in this file to utilize it directly
        """
        logging.config.dictConfig({
            'version': 1,
            'formatters': {
                'verbose': {
                    'format': '%(asctime)s | %(name)s: %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'verbose',
                },
                'debug_file_handler': {
                    'level': 'DEBUG',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'verbose',
                    'filename': '/tmp/axltoolkit.log',
                    "maxBytes": 10485760,
                    "backupCount": 20,
                    "encoding": "utf8"
                }
            },
            'loggers': {
                'zeep.transports': {
                    'level': 'DEBUG',
                    'propagate': True,
                    'handlers': ['console', 'debug_file_handler'],
                },
            }
        })
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    def get_service(self):
        return self.service

    def last_request_debug(self):
        return {
            'request': self.history.last_sent,
            'response': self.history.last_received
        }

    def run_sql_query(self, query):
        """

        Thin AXL (SQL Queries / Updates)

        """

        result = {'num_rows': 0,
                  'query': query}

        try:
            if any(re.findall(r'<|>|&lt;|&gt;', query)):
                if not re.search(r'^<!\[CDATA\[', query):
                    query = f"<![CDATA[{query}]]>"
            sql_result = self.service.executeSQLQuery(sql=query)
        except Exception as fault:
            sql_result = None
            self.last_exception = fault
            return None

        num_rows = 0
        result_rows = []

        if sql_result is not None:
            if sql_result['return'] is not None:
                for row in sql_result['return']['row']:
                    result_rows.append({})
                    for column in row:
                        result_rows[num_rows][column.tag] = column.text
                    num_rows += 1

        result['num_rows'] = num_rows
        if num_rows > 0:
            result['rows'] = result_rows

        return result

    def run_sql_update(self, query):
        """

        Thin AXL (SQL Queries / Updates)

        """

        result = {'rows_updated': 0,
                  'query': query}

        try:
            if any(re.findall(r'<|>|&lt;|&gt;', query)):
                if not re.search(r'^<!\[CDATA\[', query):
                    query = f"<![CDATA[{query}]]>"
            sql_result = self.service.executeSQLUpdate(sql=query)
        except Exception as fault:
            sql_result = None
            self.last_exception = fault
            return None

        if sql_result is not None:
            if sql_result['return'] is not None:
                result['rows_updated'] = sql_result['return']['rowsUpdated']

        return result


class CUCMAxlToolkit(AxlToolkit):
    """
    The CUCMAxlToolkit based on parent class AxlToolkit
    This class enables us to connect and make unique CUCM AXL API requests

    :param username: The username used for Basic HTTP Authentication
    :param password: The password used for Basic HTTP Authentication
    :param server_ip: The Hostname / IP Address of the server
    :param version: (optional) The major version of CUCM / IM&P Cluster (default: 12.5)
    :param tls_verify: (optional) Certificate validation check for HTTPs connection (default: True)
    :param timeout: (optional) Zeep Client Transport Response Timeout in seconds (default: 10)
    :param logging_enabled: (optional) Zeep SOAP message Logging (default: False)
    :param schema_folder_path: (optional) Sub Directory Location for AXL schema versions (default: None)
    :type username: str
    :type password: str
    :type server_ip: str
    :type version: str
    :type tls_verify: bool
    :type timeout: int
    :type logging_enabled: bool
    :type schema_folder_path: str
    :returns: return an CUCMAxlToolkit object
    :rtype: CUCMAxlToolkit
    """

    def __init__(self, username, password, server_ip, version='12.5', tls_verify=True, timeout=10,
                 logging_enabled=False, schema_folder_path=None):
        schema_folder_path += "CUCM/"

        # Create a super class, where the CUCMAxlToolkit class inherits from the AxlToolkit class.
        # This enables us to extend the parent class AxlToolkit with CUCM AXL API specic methods
        # Reference:  https://realpython.com/python-super/
        super().__init__(username, password, server_ip, version=version, tls_verify=tls_verify, timeout=timeout,
                         logging_enabled=logging_enabled, schema_folder_path=schema_folder_path)
    """
    UCM Group
    """
    def get_ucm_group(self, name):
        try:
            result = self.service.getCallManagerGroup(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def update_ucm_group_members(self, name, members):

        member_data = []
        member_count = 0

        for member in members:
            member_count += 1
            member_data.append({'priority': member_count, 'callManagerName': member})

        try:
            result = self.service.updateCallManagerGroup(name=name, members={'member': member_data})
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def add_ucm_group(self, name, members):

        member_data = []
        member_count = 0

        for member in members:
            member_count += 1
            member_data.append({'priority': member_count, 'callManagerName': member})

        try:
            result = self.service.addCallManagerGroup(callManagerGroup={
                                                      'name': name, 'members': {'member': member_data}})
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def remove_ucm_group(self, name):
        try:
            result = self.service.removeCallManagerGroup(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    """

    Users

    """

    def get_user(self, userid):
        try:
            result = self.service.getUser(userid=userid)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def list_user(self, search_Criteria_data, returned_tags=None):

        if returned_tags is None:
            returned_tags = {
                "firstName": "",
                "middleName": "",
                "lastName": "",
                "emMaxLoginTime": "",
                "userid": "",
                "mailid": "",
                "department": "",
                "manager": "",
                "userLocale": "",
                "primaryExtension": "",
                "associatedPc": "",
                "enableCti": "",
                "subscribeCallingSearchSpaceName": "",
                "enableMobility": "",
                "enableMobileVoiceAccess": "",
                "maxDeskPickupWaitTime": "",
                "remoteDestinationLimit": "",
                "status": "",
                "enableEmcc": "",
                "patternPrecedence": "",
                "numericUserId": "",
                "mlppPassword": "",
                "homeCluster": "",
                "imAndPresenceEnable": "",
                "serviceProfile": "",
                "directoryUri": "",
                "telephoneNumber": "",
                "title": "",
                "mobileNumber": "",
                "homeNumber": "",
                "pagerNumber": "",
                "calendarPresence": "",
                "userIdentity": ""
            }

        try:
            result = self.service.listUser(searchCriteria=search_Criteria_data, returnedTags=returned_tags)
        except Exception as fault:
            # users = None
            self.last_exception = fault
        return result

    def update_user(self, user_data):

        try:
            result = self.service.updateUser(**user_data)
        except Exception as fault:
            result = None
            self.last_exception = fault
        return result

    def sql_get_device_pkid(self, device):

        sql_query = "select pkid from device where name = '{0}'".format(device)

        result = self.run_sql_query(sql_query)

        if result['num_rows'] > 0:
            pkid = result['rows'][0]['pkid']
        else:
            pkid = None

        return pkid

    def sql_get_user_group_pkid(self, group_name):

        sql_query = "select pkid from dirgroup where name = '{0}'".format(group_name)

        result = self.run_sql_query(sql_query)

        if result['num_rows'] > 0:
            pkid = result['rows'][0]['pkid']
        else:
            pkid = None

        return pkid

    def sql_get_enduser_pkid(self, userid):

        sql_query = "select pkid from enduser where userid = '{0}'".format(userid)

        result = self.run_sql_query(sql_query)

        if result['num_rows'] > 0:
            pkid = result['rows'][0]['pkid']
        else:
            pkid = None

        return pkid

    def sql_associate_user_to_group(self, userid, group_name):

        user_group_pkid = self.sql_get_user_group_pkid(group_name)
        enduser_pkid = self.sql_get_enduser_pkid(userid)

        if user_group_pkid is not None and enduser_pkid is not None:
            query = "insert into enduserdirgroupmap (fkenduser, fkdirgroup) values " \
                    "('{0}', '{1}')".format(enduser_pkid, user_group_pkid)

            sql_result = self.run_sql_update(query)

            if sql_result['rows_updated'] > 0:
                result = True
            else:
                result = False

            return result

    def sql_remove_user_from_group(self, userid, group_name):
        pass

    """

    Lines

    """

    def get_line(self, dn, partition):
        try:
            result = self.service.getLine(pattern=dn, routePartitionName=partition)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def add_line(self, line_data):
        try:
            result = self.service.addLine(line=line_data)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def update_line(self, line_data):
        try:
            result = self.service.updateLine(**line_data)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def apply_line(self, dn, partition=None):
        try:
            result = self.service.applyLine(pattern=dn, routePartitionName=partition)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def add_ldap_filter(self, name, filter_name):

        filter_data = {
            'name': name,
            'filter': filter_name
        }

        try:
            result = self.service.addLdapFilter(filter_data)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def get_ldap_filter(self, name):
        """
        LDAP Filter
        """
        try:
            result = self.service.getLdapFilter(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def list_ldap_filter(self, search_Criteria_data, returned_tags):

        try:
            result = self.service.listLdapFilter(searchCriteria=search_Criteria_data,
                                                 returnedTags=returned_tags)
            self.last_exception = None
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def remove_ldap_filter(self, name):
        try:
            result = self.service.removeLdapFilter(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault
        return result

    """

    LDAP Directory

    """

    def add_ldap_directory(self, ldap_dir_data):

        try:
            result = self.service.addLdapDirectory(ldapDirectory=ldap_dir_data)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def get_ldap_directory(self, name):
        try:
            result = self.service.getLdapDirectory(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def list_ldap_directory(self, search_Criteria_data, returned_tags):

        try:
            result = self.service.listLdapDirectory(searchCriteria=search_Criteria_data,
                                                    returnedTags=returned_tags)
            self.last_exception = None
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def remove_ldap_directory(self, name):
        try:
            result = self.service.removeLdapDirectory(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def start_ldap_sync(self, ldap_name=None):
        query = "update directorypluginconfig set syncnow = '1'"
        if ldap_name is not None:
            query += "  where name = '{0}'".format(ldap_name)

        sql_result = self.run_sql_update(query)

        if sql_result['rows_updated'] > 0:
            result = True
        else:
            result = False

        return result

    def get_ldap_system(self):
        """
        LDAP System
        """
        try:
            result = self.service.getLdapSystem()
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def update_ldap_system(self, sync_enabled, ldap_server, user_id_attribute):

        try:
            result = self.service.updateLdapSystem(syncEnabled=sync_enabled,
                                                   ldapServer=ldap_server,
                                                   userIdAttribute=user_id_attribute)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def get_ldap_authentication(self):
        """
        LDAP Authentication
        """
        try:
            result = self.service.getLdapAuthentication()
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def update_ldap_authentication(self, enabled, dn, password, search_base, servers, port, ssl):

        server_data = []

        for server in servers:
            server_data.append({'hostName': server,
                                'ldapPortNumber': port,
                                'sslEnabled': ssl})

        try:
            result = self.service.updateLdapAuthentication(authenticateEndUsers=enabled,
                                                           distinguishedName=dn,
                                                           ldapPassword=password,
                                                           userSearchBase=search_base,
                                                           servers={'server': server_data})
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def get_phone(self, name):
        """
        Phone
        """
        try:
            result = self.service.getPhone(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def add_phone(self, phone_data, line_data=None):
        if line_data is not None:
            phone_data['lines'] = {'line': line_data}

        try:
            result = self.service.addPhone(phone=phone_data)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def remove_phone(self, name):
        try:
            result = self.service.removePhone(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def apply_phone(self, name):
        try:
            result = self.service.applyPhone(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def update_phone(self, phone_data, line_data=None):

        if line_data is not None:
            phone_data['lines'] = {'line': line_data}

        try:
            result = self.service.updatePhone(**phone_data)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def list_phone(self, search_Criteria_data, returned_tags=None):
        if returned_tags is None:
            returned_tags = {
                'AllowPresentationSharingUsingBfcp': '',
                'aarNeighborhoodName': '',
                'allowCtiControlFlag': '',
                'allowMraMode': '',
                'allowiXApplicableMedia': '',
                'alwaysUsePrimeLine': '',
                'alwaysUsePrimeLineForVoiceMessage': '',
                'authenticationMode': '',
                'authenticationString': '',
                'authenticationUrl': '',
                'automatedAlternateRoutingCssName': '',
                'blockIncomingCallsWhenRoaming': '',
                'builtInBridgeStatus': '',
                'callInfoPrivacyStatus': '',
                'callingSearchSpaceName': '',
                'certificateOperation': '',
                'certificateStatus': '',
                'cgpnTransformationCssName': '',
                'class': '',
                'commonDeviceConfigName': '',
                'commonPhoneConfigName': '',
                'confidentialAccess': '',
                'currentConfig': '',
                'currentProfileName': '',
                'defaultProfileName': '',
                'description': '',
                'deviceMobilityMode': '',
                'devicePoolName': '',
                'deviceTrustMode': '',
                'dialRulesName': '',
                'digestUser': '',
                'directoryUrl': '',
                'dndOption': '',
                'dndRingSetting': '',
                'dndStatus': '',
                'earlyOfferSupportForVoiceCall': '',
                'ecKeySize': '',
                'enableActivationID': '',
                'enableCallRoutingToRdWhenNoneIsActive': '',
                'enableExtensionMobility': '',
                'featureControlPolicy': '',
                'geoLocationFilterName': '',
                'geoLocationName': '',
                'hlogStatus': '',
                'homeNetworkId': '',
                'hotlineDevice': '',
                'idleTimeout': '',
                'idleUrl': '',
                'ignorePresentationIndicators': '',
                'informationUrl': '',
                'isActive': '',
                'isDualMode': '',
                'isProtected': '',
                'joinAcrossLines': '',
                'keyOrder': '',
                'keySize': '',
                'loadInformation': '',
                'locationName': '',
                'loginDuration': '',
                'loginTime': '',
                'loginUserId': '',
                'mediaResourceListName': '',
                'messagesUrl': '',
                'mlppIndicationStatus': '',
                'mobilityUserIdName': '',
                'model': '',
                'mraServiceDomain': '',
                'mtpPreferedCodec': '',
                'mtpRequired': '',
                'name': '',
                'networkHoldMohAudioSourceId': '',
                'networkLocale': '',
                'networkLocation': '',
                'numberOfButtons': '',
                'outboundCallRollover': '',
                'ownerUserName': '',
                'packetCaptureDuration': '',
                'packetCaptureMode': '',
                'phoneServiceDisplay': '',
                'phoneSuite': '',
                'phoneTemplateName': '',
                'preemption': '',
                'presenceGroupName': '',
                'primaryPhoneName': '',
                'product': '',
                'protocol': '',
                'protocolSide': '',
                'proxyServerUrl': '',
                'remoteDevice': '',
                'requireDtmfReception': '',
                'requireOffPremiseLocation': '',
                'requireThirdPartyRegistration': '',
                'rerouteCallingSearchSpaceName': '',
                'retryVideoCallAsAudio': '',
                'rfc2833Disabled': '',
                'ringSettingBusyBlfAudibleAlert': '',
                'ringSettingIdleBlfAudibleAlert': '',
                'roamingDevicePoolName': '',
                'secureAuthenticationUrl': '',
                'secureDirectoryUrl': '',
                'secureIdleUrl': '',
                'secureInformationUrl': '',
                'secureMessageUrl': '',
                'secureServicesUrl': '',
                'securityProfileName': '',
                'sendGeoLocation': '',
                'servicesUrl': '',
                'singleButtonBarge': '',
                'sipProfileName': '',
                'softkeyTemplateName': '',
                'sshUserId': '',
                'subscribeCallingSearchSpaceName': '',
                'traceFlag': '',
                'unattendedPort': '',
                'upgradeFinishTime': '',
                'useDevicePoolCgpnTransformCss': '',
                'useTrustedRelayPoint': '',
                'userHoldMohAudioSourceId': '',
                'userLocale': ''
            }
        elif isinstance(returned_tags, list):
            returned_tags = dict.fromkeys(returned_tags, '')

        try:
            result = self.service.listPhone(searchCriteria=search_Criteria_data, returnedTags=returned_tags)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    """

    Partitions

    """

    def add_partition(self, name, description):

        partition_data = {'name': name,
                          'description': description}

        try:
            result = self.service.addRoutePartition(routePartition=partition_data)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def add_partitions(self, partition_list):
        """
        Accepts a list of partitions, either as a list of strings with Partition names, or a list of dictionaries
        containing the name and description for each partition.
        """

        result = []

        for partition in partition_list:

            if not isinstance(partition, dict):
                partition = {"name": partition, "description": ""}

            try:
                result.append(self.service.addRoutePartition(routePartition=partition))
            except Exception as fault:
                result.append({'fault': fault})
                self.last_exception = fault

        return result

    def get_partition(self, name, returned_tags=None):

        try:
            if returned_tags is not None:
                result = self.service.getRoutePartition(name=name, returnedTags=returned_tags)
            else:
                result = self.service.getRoutePartition(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def remove_partition(self, name):

        try:
            result = self.service.removeRoutePartition(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    """

    Calling Search Space

    """

    def add_css(self, name, description, partition_list):

        css_data = {'name': name,
                    'description': description,
                    'members':
                        {'member': []}
                    }

        css_index = 1
        for partition in partition_list:
            partition_data = {'routePartitionName': partition,
                              'index': css_index}
            css_data['members']['member'].append(partition_data)
            css_index += 1

        try:
            result = self.service.addCss(css=css_data)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def get_css(self, name):

        try:
            result = self.service.getCss(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def remove_css(self, name):

        try:
            result = self.service.removeCss(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def update_css(self, css_name, description, partition_list):

        members = {'member': []}

        css_index = 1

        for partition in partition_list:
            partition_data = {'routePartitionName': partition,
                              'index': css_index}
            members['member'].append(partition_data)
            css_index += 1

        try:
            result = self.service.updateCss(name=css_name, description=description, members=members)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    """

    Route Group

    """

    def add_route_group(self, name, distribution_algorithm, device_list):

        rg_data = {
            'name': name,
            'distributionAlgorithm': distribution_algorithm,
            'members': {
                'member': []
            }
        }

        rg_index = 1
        for device in device_list:
            rg_data['members']['member'].append({
                'deviceSelectionOrder': rg_index,
                'deviceName': device,
                'port': 0
            })
            rg_index += 1

        try:
            result = self.service.addRouteGroup(routeGroup=rg_data)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def get_route_group(self, name):

        try:
            result = self.service.getRouteGroup(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def remove_route_group(self, name):

        try:
            result = self.service.removeRouteGroup(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def update_route_group(self, name):
        pass

    def add_route_list(self, name, description, cm_group, enabled, roan, members, ddi=None):
        """

        Route List

        """
        rl_data = {
            'name': name,
            'description': description,
            'callManagerGroupName': cm_group,
            'routeListEnabled': enabled,
            'runOnEveryNode': roan,
            'members': {
                'member': []
            }
        }

        rg_index = 1
        for member in members:
            rl_data['members']['member'].append({
                'selectionOrder': rg_index,
                'routeGroupName': member,
                'digitDiscardInstructionName': ddi
            })
            rg_index += 1

        try:
            result = self.service.addRouteList(routeList=rl_data)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def get_route_list(self, name):

        try:
            result = self.service.getRouteList(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def remove_route_list(self, name):

        try:
            result = self.service.removeRouteList(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def add_route_pattern(self, pattern, partition, route_list, network_location, outside_dialtone):
        """

        Route Pattern

        """

        rp_data = {
            'pattern': pattern,
            'routePartitionName': partition,
            'destination': {
                'routeListName': route_list
            },
            'blockEnable': False,
            'networkLocation': network_location,
            'provideOutsideDialtone': outside_dialtone
        }

        try:
            result = self.service.addRoutePattern(routePattern=rp_data)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def get_route_pattern(self, pattern, partition):

        try:
            result = self.service.getRoutePattern(pattern=pattern, routePartitionName=partition)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def remove_route_pattern(self, pattern, partition):

        try:
            result = self.service.removeRoutePattern(pattern=pattern, routePartitionName=partition)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def update_route_pattern(self, name):
        pass

    """

    Route Pattern

    """

    def add_translation_pattern(self, pattern, partition, route_list, network_location, outside_dialtone):

        rp_data = {
            'pattern': pattern,
            'routePartitionName': partition,
            'blockEnable': False,
            'networkLocation': network_location,
            'provideOutsideDialtone': outside_dialtone
        }

        try:
            result = self.service.addRoutePattern(routePattern=rp_data)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def get_translation_pattern(self, pattern, partition):

        try:
            result = self.service.getRoutePattern(pattern=pattern, routePartitionName=partition)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def remove_translation_pattern(self, pattern, partition):

        try:
            result = self.service.removeRoutePattern(pattern=pattern, routePartitionName=partition)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def update_translation_pattern(self, name):
        pass

    """

    SIP Route Pattern

    """

    def add_sip_route_pattern(self, pattern, partition, route_list):

        rp_data = {
            'pattern': pattern,
            'routePartitionName': partition,
            'sipTrunkName': route_list,
            'usage': 'Domain Routing',
        }

        try:
            result = self.service.addSipRoutePattern(sipRoutePattern=rp_data)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def get_sip_route_pattern(self, pattern, partition):

        try:
            result = self.service.getRoutePattern(pattern=pattern, routePartitionName=partition)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def remove_sip_route_pattern(self, pattern, partition):

        try:
            result = self.service.removeRoutePattern(pattern=pattern, routePartitionName=partition)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def update_sip_route_pattern(self, name):
        pass

    """

    Conference Bridge

    """

    def add_cfb(self, cfb_data):

        try:
            result = self.service.addConferenceBridge(conferenceBridge=cfb_data)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def add_cfb_cms(self, name, description, cfb_prefix, sip_trunk,
                    security_icon_control, override_dest, addresses,
                    username, password, port):
        cms_data = {
            'name': name,
            'description': description,
            'product': 'Cisco Meeting Server',
            'conferenceBridgePrefix': cfb_prefix,
            'sipTrunkName': sip_trunk,
            'allowCFBControlOfCallSecurityIcon': security_icon_control,
            'overrideSIPTrunkAddress': override_dest,
            'addresses': {
                'address': addresses
            },
            'userName': username,
            'password': password,
            'httpPort': port
        }

        result = self.add_cfb(cms_data)

        return result

    def get_cfb(self, name):

        try:
            result = self.service.getConferenceBridge(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def remove_cfb(self, name):
        pass

    def update_cfb(self, css_name, description, partition_list):
        pass

    """

    Media Resource Group

    """

    def get_mrg(self, name):

        try:
            result = self.service.getMediaResourceGroup(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    """

    Media Resource Group List

    """

    def get_mrgl(self, name):

        try:
            result = self.service.getMediaResourceList(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    """

    Device Pool

    """

    def get_device_pool(self, name):

        try:
            result = self.service.getDevicePool(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    """

    Device Security Profile

    """

    def get_phone_security_profile(self, name):

        try:
            result = self.service.getPhoneSecurityProfile(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def add_phone_security_profile(self, phone_type, protocol, name, description, device_security_mode,
                                   authentication_mode, key_size, key_order, ec_key_size, tftp_encrypted_config,
                                   nonce_validity_time, transport_type, sip_phone_port, enable_digest_auth):

        security_profile = {'phoneType': phone_type,
                            'protocol': protocol,
                            'name': name,
                            'description': description,
                            'deviceSecurityMode': device_security_mode,
                            'authenticationMode': authentication_mode,
                            'keySize': key_size,
                            'keyOrder': key_order,
                            'ecKeySize': ec_key_size,
                            'tftpEncryptedConfig': tftp_encrypted_config,
                            'nonceValidityTime': nonce_validity_time,
                            'transportType': transport_type,
                            'sipPhonePort': sip_phone_port,
                            'enableDigestAuthentication': enable_digest_auth,
                            }

        try:
            result = self.service.addPhoneSecurityProfile(phoneSecurityProfile=security_profile)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    """

    SIP Trunk Security Profile

    """

    def get_sip_trunk_security_profile(self, name):

        try:
            result = self.service.getSipTrunkSecurityProfile(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def add_sip_trunk_security_profile(self, name, description, security_mode, incoming_transport, outgoing_transport,
                                       digest_auth, nonce_policy_time, x509_subject_name, incoming_port,
                                       app_level_auth, accept_presence_subscription, accept_ood_refer,
                                       accept_unsolicited_notify, allow_replaces, transmit_security_status,
                                       sip_v150_outbound_offer_filter, allow_charging_header):

        security_profile = {
            'name': name,
            'description': description,
            'securityMode': security_mode,
            'incomingTransport': incoming_transport,
            'outgoingTransport': outgoing_transport,
            'digestAuthentication': digest_auth,
            'noncePolicyTime': nonce_policy_time,
            'x509SubjectName': x509_subject_name,
            'incomingPort': incoming_port,
            'applLevelAuthentication': app_level_auth,
            'acceptPresenceSubscription': accept_presence_subscription,
            'acceptOutOfDialogRefer': accept_ood_refer,
            'acceptUnsolicitedNotification': accept_unsolicited_notify,
            'allowReplaceHeader': allow_replaces,
            'transmitSecurityStatus': transmit_security_status,
            'sipV150OutboundSdpOfferFiltering': sip_v150_outbound_offer_filter,
            'allowChargingHeader': allow_charging_header,
        }

        try:
            result = self.service.addSipTrunkSecurityProfile(sipTrunkSecurityProfile=security_profile)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def remove_sip_trunk_security_profile(self, name):

        try:
            result = self.service.removeSipTrunkSecurityProfile(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def get_sip_profile(self, name):
        """
        SIP Profile
        """
        try:
            result = self.service.getSipProfile(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def add_sip_profile(self, profile_data):

        try:
            result = self.service.addSipProfile(sipProfile=profile_data)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def update_sip_profile(self, profile_data):

        try:
            result = self.service.updateSipProfile(**profile_data)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def get_sip_trunk(self, name):
        """
        SIP Trunk
        """
        try:
            result = self.service.getSipTrunk(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def remove_sip_trunk(self, name):

        try:
            result = self.service.removeSipTrunk(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def add_sip_trunk(self, trunk_data):

        try:
            result = self.service.addSipTrunk(sipTrunk=trunk_data)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def update_sip_trunk(self, trunk_data):

        try:
            result = self.service.updateSipTrunk(**trunk_data)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    """

    Reset / Restart Devices

    """

    def do_reset_restart_device(self, device, is_hard_reset, is_mgcp):
        reset_data = {
            'deviceName': device,
            'isHardReset': is_hard_reset,
            'isMGCP': is_mgcp
        }

        try:
            result = self.service.doDeviceReset(**reset_data)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def reset_device(self, device):
        result = self.do_reset_restart_device(device, True, False)

        return result

    def restart_device(self, device):
        result = self.do_reset_restart_device(device, False, False)

        return result

    def reset_mgcp(self, device):
        result = self.do_reset_restart_device(device, True, True)

        return result

    def restart_mgcp(self, device):
        result = self.do_reset_restart_device(device, False, True)

        return result

    """

    Service Parameters

    """

    def sql_update_service_parameter(self, name, value):

        query = "update processconfig set paramvalue = '{0}' where paramname = '{1}'".format(value, name)

        sql_result = self.run_sql_update(query)

        if sql_result['rows_updated'] > 0:
            result = True
        else:
            result = False

        return result

    def sql_get_service_parameter(self, name):

        query = "select * from processconfig where paramname = '{0}'".format(name)

        sql_result = self.run_sql_query(query)

        if sql_result['num_rows'] > 0:
            result = sql_result['rows']
        else:
            result = None

        return result

    """

    Device Association

    """

    def sql_associate_device_to_user(self, device, userid, association_type='1'):

        device_pkid = self.sql_get_device_pkid(device)
        enduser_pkid = self.sql_get_enduser_pkid(userid)

        if device_pkid is not None and enduser_pkid is not None:

            query = "insert into enduserdevicemap (fkenduser, fkdevice, defaultprofile, tkuserassociation) " \
                    "values ('{0}','{1}','f','{2}')".format(enduser_pkid, device_pkid, association_type)

            sql_result = self.run_sql_update(query)

            if sql_result['rows_updated'] > 0:
                result = True
            else:
                result = False

            return result

    """

    Remote Destinations

    """

    def get_remote_destination(self, destination):
        try:
            result = self.service.getRemoteDestination(destination=destination)
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def check_connectivity(self):
        pass

    """

    Get CCM Version

    """

    def get_ccm_version(self):
        try:
            result = self.service.getCCMVersion()
        except Exception as fault:
            result = None
            self.last_exception = fault
        if result:
            return result['return']['componentVersion']['version']
        else:
            return None

    """

    UC Service

    """

    def add_uc_service(self, uc_service_data):

        try:
            result = self.service.addUcService(ucService=uc_service_data)
            self.last_exception = None
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def get_uc_service(self, name):

        try:
            result = self.service.getUcService(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault
        return result

    def list_uc_service(self, search_Criteria_data, returned_tags):

        try:
            result = self.service.listUcService(searchCriteria=search_Criteria_data,
                                                returnedTags=returned_tags)
            self.last_exception = None
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def remove_uc_service(self, name):
        try:
            result = self.service.removeUcService(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault
        return result

    def add_service_profile(self, service_profile_data):
        """
        Add UC Service Profile
        """

        try:
            result = self.service.addServiceProfile(serviceProfile=service_profile_data)
        except Exception as fault:
            result = None
            self.last_exception = fault
        return result

    def get_service_profile(self, name):

        try:
            result = self.service.getServiceProfile(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault
        return result

    def list_service_profile(self, search_Criteria_data, returned_tags):

        try:
            result = self.service.listServiceProfile(searchCriteria=search_Criteria_data,
                                                     returnedTags=returned_tags)
            self.last_exception = None
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def remove_service_profile(self, name):
        try:
            result = self.service.removeServiceProfile(name=name)
        except Exception as fault:
            result = None
            self.last_exception = fault
        return result

    """

       Add Application User

    """

    def add_app_user(self, app_user_data):

        try:
            result = self.service.addAppUser(appUser=app_user_data)
            self.last_exception = None
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    """

    Remove Application User

    """

    def remove_app_user(self, sequence):

        try:
            result = self.service.removeAppUser(**sequence)
            self.last_exception = None
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def update_presence_redundancy_group(self, presence_redundancy_group_data):
        """
        update Presence Redundancy Group
        """
        try:
            result = self.service.updatePresenceRedundancyGroup(**presence_redundancy_group_data)
            self.last_exception = None
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def list_presence_redundancy_group(self, search_Criteria_data, returned_tags):
        """
        list Presence Redundancy Group
        """

        try:
            result = self.service.listPresenceRedundancyGroup(searchCriteria=search_Criteria_data,
                                                              returnedTags=returned_tags)
            self.last_exception = None
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result

    def update_Service_Parameter(self, service_parameter_data):
        """
        update Service Parameter/Enterprise Parameter
        """
        try:
            result = self.service.updateServiceParameter(**service_parameter_data)
            self.last_exception = None
        except Exception as fault:
            result = None
            self.last_exception = fault

        return result


class IMPAxlToolkit(AxlToolkit):
    """
    The IMPAxlToolkit based on parent class AxlToolkit
    This class enables us to connect and make unique IM&P AXL API requests

    :param username: The username used for Basic HTTP Authentication
    :param password: The password used for Basic HTTP Authentication
    :param server_ip: The Hostname / IP Address of the server
    :param version: (optional) The major version of CUCM / IM&P Cluster (default: 12.5)
    :param tls_verify: (optional) Certificate validation check for HTTPs connection (default: True)
    :param timeout: (optional) Zeep Client Transport Response Timeout in seconds (default: 10)
    :param logging_enabled: (optional) Zeep SOAP message Logging (default: False)
    :param schema_folder_path: (optional) Sub Directory Location for AXL schema versions (default: None)
    :type username: str
    :type password: str
    :type server_ip: str
    :type version: str
    :type tls_verify: bool
    :type timeout: int
    :type logging_enabled: bool
    :type schema_folder_path: str
    :returns: return an IMPAxlToolkit object
    :rtype: IMPAxlToolkit
    """

    def __init__(self, username, password, server_ip, version='11.5', tls_verify=True, timeout=10,
                 logging_enabled=False, schema_folder_path=None):
        schema_folder_path += "IMP/"

        # Create a super class, where the CUCMAxlToolkit class inherits from the AxlToolkit class.
        # This enables us to extend the parent class AxlToolkit with CUCM AXL API specic methods
        # Reference:  https://realpython.com/python-super/
        super().__init__(username, password, server_ip, version=version, tls_verify=tls_verify, timeout=timeout,
                         logging_enabled=logging_enabled, schema_folder_path=schema_folder_path)

    def get_cup_version(self):
        """
        Get CUP Version
        """
        try:
            result = self.service.getCUPVersion()
        except Exception as fault:
            result = None
            self.last_exception = fault
        if result:
            return result['return']['version']
        else:
            return None


class UcmServiceabilityToolkit:
    """
    The UcmServiceabilityToolkit SOAP API class
    This class enables us to connect and make Control Center Services API calls utilizing Zeep Python Package as the SOAP Client

    :param username: The username used for Basic HTTP Authentication
    :param password: The password used for Basic HTTP Authentication
    :param server_ip: The Hostname / IP Address of the server
    :param tls_verify: (optional) Certificate validation check for HTTPs connection (default: True)
    :param timeout: (optional) Zeep Client Transport Response Timeout in seconds (default: 10)
    :param logging_enabled: (optional) Zeep SOAP message Logging (default: False)
    :type username: str
    :type password: str
    :type server_ip: str
    :type tls_verify: bool
    :type timeout: int
    :type logging_enabled: bool
    :returns: return an UcmServiceabilityToolkit object
    :rtype: UcmServiceabilityToolkit
    """

    def __init__(self, username, password, server_ip, tls_verify=True, timeout=10, logging_enabled=False):
        """
        Constructor - Create new instance
        """

        self.session = Session()
        self.session.auth = HTTPBasicAuth(username, password)
        self.session.verify = tls_verify
        self.history = AXLHistoryPlugin(maxlen=1)
        self.wsdl = 'https://{0}:8443/controlcenterservice2/services/ControlCenterServices?wsdl'.format(server_ip)
        self.last_exception = None

        self.cache = SqliteCache(path='/tmp/sqlite_serviceability_{0}.db'.format(server_ip), timeout=60)

        self.client = Client(wsdl=self.wsdl, plugins=[self.history], transport=Transport(timeout=timeout,
                                                                                         operation_timeout=timeout,
                                                                                         cache=self.cache,
                                                                                         session=self.session))

        # Update the Default SOAP API Binding Address Location with server_ip for all API Service Endpoints
        # Default: (https://localhost:8443/controlcenterservice2/services/ControlCenterServices)
        control_svc_ip = "https://{0}:8443/controlcenterservice2/services/ControlCenterServices".format(server_ip)
        self.service = self.client.create_service("{http://schemas.cisco.com/ast/soap}ControlCenterServicesBinding",
                                                  control_svc_ip)

        if logging_enabled:
            AxlToolkit._enable_logging()

    def get_service(self):
        return self.service


class UcmRisPortToolkit:
    """
    The UcmRisPortToolkit SOAP API class
    This class enables us to connect and make RisPort70 API calls utilizing Zeep Python Package as the SOAP Client

    :param username: The username used for Basic HTTP Authentication
    :param password: The password used for Basic HTTP Authentication
    :param server_ip: The Hostname / IP Address of the server
    :param tls_verify: (optional) Certificate validation check for HTTPs connection (default: True)
    :param timeout: (optional) Zeep Client Transport Response Timeout in seconds (default: 10)
    :param logging_enabled: (optional) Zeep SOAP message Logging (default: False)
    :type username: str
    :type password: str
    :type server_ip: str
    :type tls_verify: bool
    :type timeout: int
    :type logging_enabled: bool
    :returns: return an UcmRisPortToolkit object
    :rtype: UcmRisPortToolkit
    """

    def __init__(self, username, password, server_ip, tls_verify=True, timeout=30, logging_enabled=False):
        """
        Constructor - Create new instance
        """

        self.session = Session()
        self.session.auth = HTTPBasicAuth(username, password)
        self.session.verify = tls_verify
        self.history = AXLHistoryPlugin(maxlen=1)
        self.wsdl = 'https://{0}:8443/realtimeservice2/services/RISService70?wsdl'.format(server_ip)
        self.last_exception = None

        self.cache = SqliteCache(path='/tmp/sqlite_risport_{0}.db'.format(server_ip), timeout=60)

        self.client = Client(wsdl=self.wsdl, plugins=[self.history], transport=Transport(timeout=timeout,
                                                                                         operation_timeout=timeout,
                                                                                         cache=self.cache,
                                                                                         session=self.session))

        # Update the Default SOAP API Binding Address Location with server_ip for all API Service Endpoints
        # Default: (https://localhost:8443/realtimeservice2/services/RISService70)
        self.service = self.client.create_service("{http://schemas.cisco.com/ast/soap}RisBinding",
                                                  "https://{0}:8443/realtimeservice2/services/RISService70".format(server_ip))

        if logging_enabled:
            AxlToolkit._enable_logging()

    def get_service(self):
        return self.service


class UcmPerfMonToolkit:
    """
    The UcmPerfMonToolkit SOAP API class
    This class enables us to connect and make PerfMon API calls utilizing Zeep Python Package as the SOAP Client

    :param username: The username used for Basic HTTP Authentication
    :param password: The password used for Basic HTTP Authentication
    :param server_ip: The Hostname / IP Address of the server
    :param tls_verify: (optional) Certificate validation check for HTTPs connection (default: True)
    :param timeout: (optional) Zeep Client Transport Response Timeout in seconds (default: 10)
    :param logging_enabled: (optional) Zeep SOAP message Logging (default: False)
    :type username: str
    :type password: str
    :type server_ip: str
    :type tls_verify: bool
    :type timeout: int
    :type logging_enabled: bool
    :returns: return an UcmPerfMonToolkit object
    :rtype: UcmPerfMonToolkit
    """

    def __init__(self, username, password, server_ip, tls_verify=True, timeout=30, logging_enabled=False):
        """
        Constructor - Create new instance
        """

        self.session = Session()
        self.session.auth = HTTPBasicAuth(username, password)
        self.session.verify = tls_verify
        self.history = AXLHistoryPlugin(maxlen=1)
        self.wsdl = 'https://{0}:8443/perfmonservice2/services/PerfmonService?wsdl'.format(server_ip)
        self.last_exception = None

        self.cache = SqliteCache(path='/tmp/sqlite_perfmon_{0}.db'.format(server_ip), timeout=60)

        self.client = Client(wsdl=self.wsdl, plugins=[self.history], transport=Transport(timeout=timeout,
                                                                                         operation_timeout=timeout,
                                                                                         cache=self.cache,
                                                                                         session=self.session))

        # Update the Default SOAP API Binding Address Location with server_ip for all API Service Endpoints
        # Default: (https://localhost:8443/perfmonservice2/services/PerfmonService)
        self.service = self.client.create_service("{http://schemas.cisco.com/ast/soap}PerfmonBinding",
                                                  "https://{0}:8443/perfmonservice2/services/PerfmonService".format(server_ip))

        if logging_enabled:
            AxlToolkit._enable_logging()

    def get_service(self):
        return self.service

    def perfmon_open_session(self):
        session_handle = self.service.perfmonOpenSession()
        return session_handle

    def perfmon_close_session(self, session_handle):
        return self.service.perfmonCloseSession(SessionHandle=session_handle)

    def perfmon_add_counter(self, session_handle, counters):
        """
        :param session_handle: A session Handle returned from perfmonOpenSession()
        :param counters: An array of counters or a single string for a single counter
        :return: True for Success and False for Failure
        """

        if isinstance(counters, list):
            counter_data = [
                {
                    'Counter': []
                }
            ]

            for counter in counters:
                new_counter = {
                    'Name': counter
                }
                counter_data[0]['Counter'].append(new_counter)

        elif counters is not None:
            counter_data = [
                {
                    'Counter': [
                        {
                            'Name': counters
                        }
                    ]
                }
            ]

        try:
            self.service.perfmonAddCounter(SessionHandle=session_handle, ArrayOfCounter=counter_data)
            result = True
        except Exception:
            result = False

        return result

    def perfmon_collect_session_data(self, session_handle):
        return self.service.perfmonCollectSessionData(SessionHandle=session_handle)

    def perfmon_collect_counter_data(self, host, perfmon_object):
        return self.service.perfmonCollectCounterData(Host=host, Object=perfmon_object)


class UcmLogCollectionToolkit:
    """
    The UcmLogCollectionToolkit SOAP API class
    This class enables us to connect and make Log Collection API calls utilizing Zeep Python Package as the SOAP Client

    :param username: The username used for Basic HTTP Authentication
    :param password: The password used for Basic HTTP Authentication
    :param server_ip: The Hostname / IP Address of the server
    :param tls_verify: (optional) Certificate validation check for HTTPs connection (default: True)
    :param timeout: (optional) Zeep Client Transport Response Timeout in seconds (default: 10)
    :param logging_enabled: (optional) Zeep SOAP message Logging (default: False)
    :type username: str
    :type password: str
    :type server_ip: str
    :type tls_verify: bool
    :type timeout: int
    :type logging_enabled: bool
    :returns: return an UcmLogCollectionToolkit object
    :rtype: UcmLogCollectionToolkit
    """

    def __init__(self, username, password, server_ip, tls_verify=True, timeout=30, logging_enabled=False):
        """
        Constructor - Create new instance
        """

        self.session = Session()
        self.session.auth = HTTPBasicAuth(username, password)
        self.session.verify = tls_verify
        self.history = AXLHistoryPlugin(maxlen=1)
        self.wsdl = 'https://{0}:8443/logcollectionservice2/services/LogCollectionPortTypeService?wsdl'.format(server_ip)
        self.last_exception = None

        self.cache = SqliteCache(path='/tmp/sqlite_logcollection.db', timeout=60)

        self.client = Client(wsdl=self.wsdl, plugins=[self.history], transport=Transport(timeout=timeout,
                                                                                         operation_timeout=timeout,
                                                                                         cache=self.cache,
                                                                                         session=self.session))

        # Update the Default SOAP API Binding Address Location with server_ip for all API Service Endpoints
        # Default: (https://localhost:8443/logcollectionservice2/services/LogCollectionPortTypeService)
        self.service = self.client.create_service("{http://schemas.cisco.com/ast/soap}LogCollectionPortSoapBinding",
                                                  "https://{0}:8443/logcollectionservice2/services/LogCollectionPortTypeService".format(server_ip))

        if logging_enabled:
            AxlToolkit._enable_logging()

    def get_service(self):
        return self.service


class UcmDimeGetFileToolkit:
    """
    The UcmDimeGetFileToolkit SOAP API class
    This class enables us to connect and make DimeGetFileService API calls utilizing Zeep Python Package as the SOAP Client

    :param username: The username used for Basic HTTP Authentication
    :param password: The password used for Basic HTTP Authentication
    :param server_ip: The Hostname / IP Address of the server
    :param tls_verify: (optional) Certificate validation check for HTTPs connection (default: True)
    :param timeout: (optional) Zeep Client Transport Response Timeout in seconds (default: 10)
    :param logging_enabled: (optional) Zeep SOAP message Logging (default: False)
    :type username: str
    :type password: str
    :type server_ip: str
    :type tls_verify: bool
    :type timeout: int
    :type logging_enabled: bool
    :returns: return an UcmDimeGetFileToolkit object
    :rtype: UcmDimeGetFileToolkit
    """

    def __init__(self, username, password, server_ip, tls_verify=True, timeout=30, logging_enabled=False):
        """
        Constructor - Create new instance
        """

        self.session = Session()
        self.session.auth = HTTPBasicAuth(username, password)
        self.session.verify = tls_verify
        self.history = AXLHistoryPlugin(maxlen=1)
        self.wsdl = 'https://{0}:8443/logcollectionservice/services/DimeGetFileService?wsdl'.format(server_ip)
        self.last_exception = None

        self.cache = SqliteCache(path='/tmp/sqlite_logcollectiondime.db', timeout=60)

        self.client = Client(wsdl=self.wsdl, plugins=[self.history], transport=Transport(timeout=timeout,
                                                                                         operation_timeout=timeout,
                                                                                         cache=self.cache,
                                                                                         session=self.session))

        self.service = self.client.service

        if logging_enabled:
            AxlToolkit._enable_logging()

    def get_service(self):
        return self.service


class PawsToolkit:
    """
    The PawsToolkit SOAP API class
    This class enables us to connect and make PAWS API calls utilizing Zeep Python Package as the SOAP Client

    :param username: The username used for Basic HTTP Authentication
    :param password: The password used for Basic HTTP Authentication
    :param server_ip: The Hostname / IP Address of the server
    :param service: The PAWS API service name
    :param tls_verify: (optional) Certificate validation check for HTTPs connection (default: True)
    :param timeout: (optional) Zeep Client Transport Response Timeout in seconds (default: 10)
    :param logging_enabled: (optional) Zeep SOAP message Logging (default: False)
    :type username: str
    :type password: str
    :type server_ip: str
    :type service: str
    :type tls_verify: bool
    :type timeout: int
    :type logging_enabled: bool
    :returns: return an PawsToolkit object
    :rtype: PawsToolkit
    """

    def __init__(self, username, password, server_ip, service, tls_verify=True, timeout=30, logging_enabled=False):
        """
        Constructor - Create new instance
        """

        self.session = Session()
        self.session.auth = HTTPBasicAuth(username, password)
        self.session.verify = tls_verify
        self.history = AXLHistoryPlugin(maxlen=1)
        self.wsdl = None
        self.binding = None
        self.endpoint = None
        self.last_exception = None

        self.cache = SqliteCache(path='/tmp/sqlite_paws_{0}.db'.format(server_ip), timeout=60)

        dir = os.path.dirname(__file__)

        if service == 'HardwareInformation':
            self.wsdl = os.path.join(dir, 'paws/hardware_information_service.wsdl')
            self.binding = "{http://services.api.platform.vos.cisco.com}HardwareInformationServiceSoap11Binding"
            self.endpoint = "https://{0}:8443/platform-services/services/HardwareInformationService.HardwareInformationServiceHttpsSoap11Endpoint/".format(server_ip)  # nopep8
        elif service == 'OptionsService':
            self.wsdl = 'https://{0}:8443/platform-services/services/OptionsService?wsdl'.format(server_ip)
            self.binding = "{http://services.api.platform.vos.cisco.com}OptionsServiceSoap12Binding"
            self.endpoint = "https://{0}:8443/platform-services/services/OptionsService.OptionsServiceHttpsSoap12Endpoint/".format(server_ip)  # nopep8
        elif service == 'ProductService':
            self.wsdl = 'https://{0}:8443/platform-services/services/ProductService?wsdl'.format(server_ip)
            self.binding = "{http://services.api.platform.vos.cisco.com}ProductServiceSoap12Binding"
            self.endpoint = "https://{0}:8443/platform-services/services/ProductService.ProductServiceHttpsSoap12Endpoint/".format(server_ip)  # nopep8
        elif service == 'VersionService':
            self.wsdl = 'https://{0}:8443/platform-services/services/VersionService?wsdl'.format(server_ip)
            self.binding = "{http://services.api.platform.vos.cisco.com}VersionServiceSoap12Binding"
            self.endpoint = "https://{0}:8443/platform-services/services/VersionService.VersionServiceHttpsSoap12Endpoint/".format(server_ip)  # nopep8
        elif service == 'ClusterNodesService':
            self.wsdl = 'https://{0}:8443/platform-services/services/ClusterNodesService?wsdl'.format(server_ip)
            self.binding = "{http://services.api.platform.vos.cisco.com}ClusterNodesServiceSoap12Binding"
            self.endpoint = "https://{0}:8443/platform-services/services/ClusterNodesService.ClusterNodesServiceHttpsSoap12Endpoint/".format(server_ip)  # nopep8

        self.client = Client(wsdl=self.wsdl, plugins=[self.history], transport=Transport(timeout=timeout,
                                                                                         operation_timeout=timeout,
                                                                                         cache=self.cache,
                                                                                         session=self.session))

        self.service = self.client.create_service(self.binding, self.endpoint)

        if logging_enabled:
            AxlToolkit._enable_logging()

    def get_service(self):
        return self.service

    def get_cluster_replication(self):
        cluster_replication = self.service.isNodeReplicationOK()
        return cluster_replication

    def get_active_options(self):
        active_options = self.service.getActiveOptions()
        return active_options

    def get_active_version(self):
        active_version = self.service.getActiveVersion()
        return active_version

    def get_inactive_version(self):
        inactive_version = self.service.getInactiveVersion()
        return inactive_version

    def get_installed_products(self):
        installed_prod = self.service.getInstalledProducts()
        return installed_prod

    def get_hardware_information(self):
        hw_info = self.service.getHardwareInformation()
        return hw_info
