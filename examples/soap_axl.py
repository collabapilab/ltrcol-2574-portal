"""
Sample python script demonstrating CUCM AXL with zeep library
"""
import pprint
import logging
from lxml import etree
import requests
import urllib3
# Import zeep library

# Set up logging with a default level of INFO
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
# Create a logging instance
log = logging.getLogger(__name__)

# Create variables for your pod CUCM host and credentials

# Create variable for the CUCM 14 AXL WSDL File location

# Create an instance of requests.Session that we will use with the zeep.Client

# Create an instance of zeep HistoryPlugin in order to debug the sent and received SOAP Payloads

# Create an instance of the zeep.Client using the axl_wsdl file
# and the session object as the transport and with the history plugin

# Create the AXL Service binding to your POD's CUCM AXL service URL
# Defaults to https://ccmservername:8443/axl/

# Create variables to pass as arguments to listPhone AXL API service method

# execute listPhone AXL method and pass the searchCriteria and returnedTags as arguments

# log outbound soap payload sent to CUCM AXL API

# Create variable to pass as arguments to updatePhone AXL API service method

# execute updatePhone AXL method and unpack the update_phone_data dictionary and pass it as keyword arguments

# execute applyPhone AXL method and pass the Phone name argument

# execute getPhone AXL method and pass the Phone name argument

# Create variable to pass as arguments to addPhone AXL API service method

# execute addPhone AXL method and unpack the add_phone_data dictionary and pass it as keyword arguments
