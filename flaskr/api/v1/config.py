"""
Default server hostname/port/credentials
"""

DEFAULT_CUCM = {
    'host': 'cucm1a.pod31.col.lab',
    'port': 8443,
    'username': 'admin',
    'password': 'C1sco.123'
}

DEFAULT_CUC = {
    'host': 'cuc1a.pod31.col.lab',
    'port': 443,
    'username': 'admin',
    'password': 'C1sco.123'
}

DEFAULT_CMS = {
    'host': 'cms1a.pod31.col.lab',
    'port': 8443,
    'username': 'admin',
    'password': 'C1sco.123'
}

# Retrieve User access token from: https://developer.webex.com/docs/getting-started
WBX_USER_ACCESS_TOKEN = '___PASTE_PERSONAL_ACCESS_TOKEN_HERE___'

# Retrieve BOT access token from: https://developer.webex.com/my-apps
WBX_BOT_ACCESS_TOKEN = '___PASTE_BOT_ACCESS_TOKEN_HERE___'

# Participant pod number
POD_NUM = '31'

# Bot Webhook details
WBX_WEBHOOK_NAME = 'Cisco Live LTRCOL-2574 Webhook'
WBX_WEBHOOK_URL = 'http://collab-api-webhook.ciscolive.com:9031/api/v1/wbxt/events'
# Domain for all users in Control Hub
DOMAIN = 'collab-api.com'
