"""
Sample python script demonstrating CUCM AXL with zeep library
"""
import pprint
import logging
from lxml import etree
import requests
import urllib3
# Import zeep library
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

# Create variable for the CUCM 14 AXL WSDL File location
AXL_WSDL_FILE = "flaskr/cucm/v1/axltoolkit/CUCM/schema/14.0/AXLAPI.wsdl"

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

# Create an instance of the zeep.Client using the axl_wsdl file
# and the session object as the transport and with the history plugin
client = zeep.Client(wsdl=AXL_WSDL_FILE, transport=zeep.Transport(session=session),
                     plugins=[history])

# Create the AXL Service binding to your POD's CUCM AXL service URL
# Defaults to https://ccmservername:8443/axl/
service = client.create_service('{http://www.cisco.com/AXLAPIService/}AXLAPIBinding',
                                f'https://{CUCM_ADDRESS}:8443/axl/')

# pprint(service.listPhone.__doc__)
"""
('listPhone(searchCriteria: {name: xsd:string, description: xsd:string, '
 'protocol: xsd:string, callingSearchSpaceName: xsd:string, devicePoolName: '
 'xsd:string, securityProfileName: xsd:string}, returnedTags: ns0:LPhone, '
 'skip: xsd:unsignedLong, first: xsd:unsignedLong, sequence: xsd:unsignedLong) '
 '-> return: {phone: ns0:LPhone[]}, sequence: xsd:unsignedLong')
"""

# Create variables to pass as arguments to listPhone AXL API service method
search_criteria = {
    'name': '%'
}

returned_tags = {
    'name': '%'
}

# execute listPhone AXL method and pass the searchCriteria and returnedTags as arguments
list_phone_response = service.listPhone(searchCriteria=search_criteria, returnedTags=returned_tags)

# log outbound soap payload sent to CUCM AXL API
log.info('\n %s', etree.tostring(history.last_sent["envelope"], encoding="unicode", pretty_print=True))
# log inbound soap payload received from CUCM AXL API
log.info('\n %s', etree.tostring(history.last_received["envelope"], encoding="unicode", pretty_print=True))
# pretty print the parsed response by zeep library
log.info('\n %s', pprint.pformat(list_phone_response))

# Create variable to pass as arguments to updatePhone AXL API service method
update_phone_data = {
    'name': 'CSFPOD31UCMUSER',
    'callingSearchSpaceName': 'Unrestricted_CSS'
}

# execute updatePhone AXL method and unpack the update_phone_data dictionary and pass it as keyword arguments
update_phone_response = service.updatePhone(**update_phone_data)

# log outbound soap payload sent to CUCM AXL API
log.info('\n %s', etree.tostring(history.last_sent["envelope"], encoding="unicode", pretty_print=True))
# log inbound soap payload received from CUCM AXL API
log.info('\n %s', etree.tostring(history.last_received["envelope"], encoding="unicode", pretty_print=True))
# pretty print the parsed response by zeep library
log.info('\n %s', pprint.pformat(update_phone_response))

# execute applyPhone AXL method and pass the Phone name argument
apply_phone_response = service.applyPhone(name='CSFPOD31UCMUSER')

# log outbound soap payload sent to CUCM AXL API
log.info('\n %s', etree.tostring(history.last_sent["envelope"], encoding="unicode", pretty_print=True))
# log inbound soap payload received from CUCM AXL API
log.info('\n %s', etree.tostring(history.last_received["envelope"], encoding="unicode", pretty_print=True))
# pretty print the parsed response by zeep library
log.info('\n %s', pprint.pformat(apply_phone_response))

# execute getPhone AXL method and pass the Phone name argument
get_phone_response = service.getPhone(name='CSFPOD31UCMUSER')

# log outbound soap payload sent to CUCM AXL API
log.info('\n %s', etree.tostring(history.last_sent["envelope"], encoding="unicode", pretty_print=True))
# log inbound soap payload received from CUCM AXL API
log.info('\n %s', etree.tostring(history.last_received["envelope"], encoding="unicode", pretty_print=True))
# pretty print the parsed response by zeep library
log.info('\n %s', pprint.pformat(get_phone_response))

# Create variable to pass as arguments to addPhone AXL API service method
add_phone_data = {
    'name': 'CSFPOD31USER2',
    'description': 'Cisco Live LTRCOL-2574 - pod31user2',
    'product': 'Cisco Unified Client Services Framework',
    'class': 'Phone',
    'protocol': 'SIP',
    'protocolSide': 'User',
    'commonPhoneConfigName': 'Standard Common Phone Profile',
    'callingSearchSpaceName': 'Unrestricted_CSS',
    'devicePoolName': 'Default',
    'locationName': 'Hub_None',
    'securityProfileName': 'Universal Device Template - Model-independent Security Profile',
    'sipProfileName': 'Standard SIP Profile',
    'ownerUserName': 'pod31user2',
    'lines': {
        'line': {
            'index': '1',
            'dirn': {
                'pattern': '\\+19195310002',
                'routePartitionName': 'DN_PT'
            },
            'display': 'Pod31 User2',
            'displayAscii': 'Pod31 User2',
            'associatedEndusers': {
                    'enduser': {
                        'userId': 'pod31user2'
                    }
            }
        }
    }
}

# execute addPhone AXL method and unpack the add_phone_data dictionary and pass it as keyword arguments
add_phone_response = service.addPhone(phone=add_phone_data)

# log outbound soap payload sent to CUCM AXL API
log.info('\n %s', etree.tostring(history.last_sent["envelope"], encoding="unicode", pretty_print=True))
# log inbound soap payload received from CUCM AXL API
log.info('\n %s', etree.tostring(history.last_received["envelope"], encoding="unicode", pretty_print=True))
# pretty print the parsed response by zeep library
log.info('\n %s', pprint.pformat(add_phone_response))
