import requests
import config
from datetime import datetime

def postWebhook(data):
    result = requests.post(config.discord_webhook, json = data)
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Webhook delivered successfully, code {}.".format(result.status_code))

# Sends a Success Webhook for a Given Function Call
# PARAMS:
#   function_name   : Name of the Contract Function Called
#   tx_hash         : Transaction Hash
#   gas_used        : Total Gas Used
#   fees_paid       : Total Fees Paid
#   account_balance : Balance of Account
def sendWebhookSuccess(function_name, tx_hash, gas_used, fees_paid, account_balance):
    tx_url = "https://arbiscan.io/tx/" + tx_hash

    # Returns Timestamp, Gas Used, and Fees Paid
    data = {
        "username" : "Bridgeworld Update",
        "embeds": [
            {
                "title" : function_name + " Success",
                "description" : "[{}]({})".format(tx_url, tx_url),
                "color" : "1752220", # AQUA
                "fields": [
                    {
                        "name": "Current Time",
                        "value": datetime.now().strftime("%H:%M:%S")
                    },
                    {
                        "name": "Gas Used",
                        "value": gas_used,
                        "inline": True
                    },
                    {
                        "name": "Fees Paid",
                        "value": str(fees_paid) + " AETH",
                        "inline": True
                    },
                    {
                        "name": "Account Balance",
                        "value": str(account_balance) + " AETH",
                    }
                ]
            }
        ]
    }
    postWebhook(data)

# Sends a Failure Webhook for a Given Function Call and Message
# PARAMS:
#   function_name   : Name of the Contract Function Called
#   message         : Error Message
def sendWebhookFailure(function_name, message):
    # Returns Timestamp and Error Message
    data = {
        "username" : "Bridgeworld Update",
        "embeds" : [
            {
                "title" : function_name + " Warning",
                "description" : message,
                "color" : "16711680", # RED
                "fields": [
                    {
                        "name": "Current Time",
                        "value": datetime.now().strftime("%H:%M:%S")
                    }
                ]
            }
        ]
    }
    postWebhook(data)

# Sends a Info Webhook for a Given Message
# PARAMS:
#   message         : Message
def sendWebhookInfo(message):
    data = {
        "username" : "Bridgeworld Update",
        "embeds" : [
            {
                "title" : message,
                "color" : "16776960", # YELLOW
                "fields": [
                    {
                        "name": "Current Time",
                        "value": datetime.now().strftime("%H:%M:%S")
                    }
                ]
            }
        ]
    }
    postWebhook(data)