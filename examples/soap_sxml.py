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

# Create variable for the CUCM 14 RISPORT WSDL File location

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

# Create the RisPort70 Service binding to your POD's CUCM RisPort70 service URL
# Defaults to https://localhost:8443/perfmonservice2/services/PerfmonService/

# Create variables to pass as arguments to SelectCmDeviceExt RisPort70 API service method

# execute selectCMDevice RisPort70 method and pass the StateInfo and cm_selection_criteria as arguments

# Create variable for the CUCM 14 PerfMon WSDL File location

# execute perfmonCollectCounterData PerfMon method and pass the Host and Object arguments
