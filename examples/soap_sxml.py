"""
Sample python script demonstrating CUCM SXML with zeep library
"""
import pprint
import logging
from lxml import etree
import requests
import urllib3
import zeep

# Set up logging with a default level of INFO
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
# Create a logging instance
log = logging.getLogger(__name__)

# Create variables for your pod CUCM host and credentials
CUCM_ADDRESS = '10.0.131.41'
# CUCM_ADDRESS = 'cucm1a.pod31.col.lab'
CUCM_USERNAME = "admin"
CUCM_PASSWORD = "C1sco.123"

# Create variable for the CUCM 14 RISPORT WSDL File location
RISPORT_WSDL_FILE = "https://cucm1a.pod31.col.lab:8443/realtimeservice2/services/RISService70?wsdl"

# Create an instance of requests.Session that we will use with the zeep.Client
session = requests.Session()
# Disable SSL Certificate verification
session.verify = False
# Disable insecure requests warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Configure session authentication with basic auth method using CUCM credentials
session.auth = requests.auth.HTTPBasicAuth(CUCM_USERNAME, CUCM_PASSWORD)

# Create an instance of zeep HistoryPlugin in order to debug the sent and received SOAP Payloads
history = zeep.plugins.HistoryPlugin()

# Create an instance of the zeep.Client using the RISPORT_WSDL_FILE file
# and the session object as the transport and with the history plugin
client = zeep.Client(wsdl=RISPORT_WSDL_FILE, transport=zeep.Transport(session=session),
                     plugins=[history])

# Create the RisPort70 Service binding to your POD's CUCM RisPort70 service URL
# Defaults to https://localhost:8443/perfmonservice2/services/PerfmonService/
service = client.create_service('{http://schemas.cisco.com/ast/soap}RisBinding',
                                f'https://{CUCM_ADDRESS}:8443/realtimeservice2/services/RISService70/')

# pprint(service.listPhone.__doc__)
"""
('listPhone(searchCriteria: {name: xsd:string, description: xsd:string, '
 'protocol: xsd:string, callingSearchSpaceName: xsd:string, devicePoolName: '
 'xsd:string, securityProfileName: xsd:string}, returnedTags: ns0:LPhone, '
 'skip: xsd:unsignedLong, first: xsd:unsignedLong, sequence: xsd:unsignedLong) '
 '-> return: {phone: ns0:LPhone[]}, sequence: xsd:unsignedLong')
"""

# Create variables to pass as arguments to SelectCmDeviceExt RisPort70 API service method
cm_selection_criteria = {
    'MaxReturnedDevices': '1000',
    'DeviceClass': 'Any',
    'Model': '255',
    'Status': 'Any',
    'NodeName': '',
    'SelectBy': 'Description',
    'SelectItems': {
        'item': 'Cisco*'
    },
    'Protocol': 'Any',
    'DownloadStatus': 'Any'
}

# execute selectCMDevice RisPort70 method and pass the StateInfo and cm_selection_criteria as arguments
phone_query_response = service.selectCmDevice(StateInfo='', CmSelectionCriteria=cm_selection_criteria)

# log outbound soap payload sent to CUCM RISPORT API
log.info('*** Sent SOAP payload:\n %s', etree.tostring(history.last_sent["envelope"], encoding="unicode", pretty_print=True))
# log inbound soap payload received from CUCM RISPORT API
log.info('*** Received SOAP payload:\n %s', etree.tostring(history.last_received["envelope"], encoding="unicode", pretty_print=True))
# pretty print the parsed response by zeep library
log.info('*** Parsed payload:\n %s', pprint.pformat(phone_query_response))

# Create variable for the CUCM 14 PerfMon WSDL File location
PERFMON_WSDL_FILE = "https://cucm1a.pod1.col.lab:8443/perfmonservice2/services/PerfmonService?wsdl"

# Create a new instance of the zeep.Client using the PERFMON_WSDL_FILE
# and the session object as the transport and with the history plugin
client = zeep.Client(wsdl=PERFMON_WSDL_FILE, transport=zeep.Transport(session=session),
                     plugins=[history])

# Create the PerfMon Service binding to your POD's CUCM PerfMon service URL
# Defaults to https://localhost:8443/perfmonservice2/services/PerfmonService/
service = client.create_service('{http://schemas.cisco.com/ast/soap}PerfmonBinding',
                                f'https://{CUCM_ADDRESS}:8443/perfmonservice2/services/PerfmonService')

perfmon_query_response = service.perfmonCollectCounterData(Host="cucm1a.pod31.col.lab", Object="Cisco CallManager")

# log outbound soap payload sent to CUCM AXL API
log.info('*** Sent SOAP payload:\n %s', etree.tostring(history.last_sent["envelope"], encoding="unicode", pretty_print=True))
# log inbound soap payload received from CUCM AXL API
log.info('*** Received SOAP payload:\n %s', etree.tostring(history.last_received["envelope"], encoding="unicode", pretty_print=True))
# pretty print the parsed response by zeep library
log.info('*** Parsed payload:\n %s', pprint.pformat(perfmon_query_response))
