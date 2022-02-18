import time
import config
import discord
from datetime import datetime
from web3 import Web3, exceptions

# Web3 connection
web3 = Web3(Web3.HTTPProvider(config.infura_arbitrum))
print("Web3 Connected: " + str(web3.isConnected()))

# Initialize Bridgeworld Contract
contract = web3.eth.contract(address=config.contract_url, abi=config.contract_abi)

### HELPER FUNCTIONS ###

# Returns Current Gas Prices
def getGasPrice():
    gasPrice = web3.eth.gasPrice                            # Current Gas Price
    cheaperGasPrice = gasPrice - web3.toWei(.1, 'gwei')     # Reduced Gas Price
    return web3.fromWei(cheaperGasPrice, 'gwei')

# Returns Wallet AETH Balance
def getWalletBalance():
    wallet_ballance =  web3.eth.get_balance(config.address)
    if wallet_ballance < .1:
        # Send Discord Warning
        todo = "TODO"
    return web3.fromWei(wallet_ballance, 'ether')

def getNewNonceForAddress(address):
    return web3.eth.getTransactionCount(address)

def getNewNonce():
    return getNewNonceForAddress(config.address)

# Returns Fields from a given Transaction Hash
# PARAMS:
#   tx_hash     : Transaction Hash
#
# RETURN:
#   gas_used    : Total Gas Used
#   fees_paid   : Total Fees Paid
def extractFieldsFromTransaction(tx_hash):
    print(tx_hash)
    count = 0
    gas_used = None
    gas_price = None
    fees_paid = None
    while count < 5:    # MAX 5 Retries
        try:
            print("Trying")
            gas_used = web3.eth.get_transaction_receipt(tx_hash).gasUsed                # Gas Used from TX
            print(gas_used)
            gas_price = web3.eth.get_transaction_receipt(tx_hash).effectiveGasPrice     # Gas Price Paid from TX
            print(gas_price)
            fees_paid = gas_used * web3.fromWei(gas_price, 'ether')                     # Total Fees Paid from TX
            print(fees_paid)
            count = 5                                                                   # Force quit
        except exceptions.TransactionNotFound as err:                                   # Catch Exception in case Transaction hasn't been posted to public pool
            print("error")
            count += 1  
            print("Count: " + str(count))                                                                
            discord.sendWebhookFailure("extractFieldsFromTransaction", str(err))        # Send Webhook per Failure
            time.sleep(5)                                                               # Make sure to add time between checks
    return (gas_used, fees_paid)


### CONTRACT HELPER FUNCTIONS ###

def getEncodedData(method_name, args):
    return contract.encodeABI(fn_name=method_name, args=args)

# Construct Transaction for Bridgeworld Functions on Arbitrum
# PARAMS:
#   gas_limit   : Gas Limit to be used
#
# RETURN:
#   tx          : Transaction to be sent to Bridgeworld Contract
def constructTx(gas_limit):
    nonce = getNewNonce()
    tx = {
        'nonce': nonce,
        'chainId': 42161,
        'from': config.address,
        'gas': gas_limit,
        'gasPrice': web3.toWei(getGasPrice(), 'gwei')
    }
    return tx

def constructTxRevealQuest():
    return constructTx(config.reveal_gas_limit)

def constructTxRestartQuest():
    return constructTx(config.restart_gas_limit)

### CONTRACT GETTER FUNCTIONS ###

# Returns Start Time of Quest for a Given Token
def getTokenIdToQuestStartTime(tokenId):
    start_time = None
    try:
        start_time = contract.functions.tokenIdToQuestStartTime(tokenId).call()
    except exceptions.ContractLogicError as err:
        discord.sendWebhookFailure("tokenIdToQuestStartTime", str(err))
    return start_time

def minutesLeftUntilQuesting(tokenId):
    start_time = getTokenIdToQuestStartTime(tokenId)
    date_start_time = datetime.fromtimestamp(start_time)
    current_time = time.time()
    date_current_time = datetime.fromtimestamp(current_time)
    seconds_since_questing = date_current_time - date_start_time
    eight_hours = 8 * 60 * 60
    return (eight_hours - seconds_since_questing.total_seconds()) / 60

def secondsLeftUntilQuesting(tokenId):
    start_time = getTokenIdToQuestStartTime(tokenId)
    date_start_time = datetime.fromtimestamp(start_time)
    current_time = time.time()
    date_current_time = datetime.fromtimestamp(current_time)
    seconds_since_questing = date_current_time - date_start_time
    eight_hours = 8 * 60 * 60 + 20
    return (eight_hours - seconds_since_questing.total_seconds())

def canQuest(tokenId):
    return False if secondsLeftUntilQuesting(tokenId) > 0 else True

def canReveal(tokenId):
    try:
        contract.functions.isQuestReadyToReveal(tokenId).call()
    except exceptions.ContractLogicError as err:
        return 'Error'
    else:
        return 'True' if contract.functions.isQuestReadyToReveal(tokenId).call() else 'False'

# def returnState(tokenId):
    # STATE 1: 

### CONTRACT FUNCTIONS ###

# Estimates gas for revealTokensQuests
def estimateGasRevealQuest(token_input_array):
    estimated_gas = None
    try: 
        estimated_gas = contract.functions.revealTokensQuests(token_input_array).estimateGas(constructTxRevealQuest())
    except exceptions.ContractLogicError as err:
        discord.sendWebhookFailure("revealTokensQuests", str(err))
    return estimated_gas

# Estimates gas for restartTokenQuests
def estimateGasRestartQuest(token_input_array, difficulties_input_array, quest_input_array):
    estimated_gas = None
    try: 
        estimated_gas = contract.functions.restartTokenQuests(token_input_array, difficulties_input_array, quest_input_array).estimateGas(constructTxRestartQuest())
    except exceptions.ContractLogicError as err:
        discord.sendWebhookFailure("restartTokenQuests", str(err))
    return estimated_gas

# Checks if Balance is enough to call revealTokensQuests
def checkBalanceIsEnoughForReveal(token_input_array):
    estimated_cost = web3.fromWei(estimateGasRevealQuest(token_input_array), 'gwei')
    account_balance = getWalletBalance()
    ret = True if account_balance - estimated_cost > 0 else False
    return ret

# Checks if Balance is enough to call restartTokenQuests
def checkBalanceIsEnoughForRestart(token_input_array, difficulties_input_array, quest_input_array):
    estimated_cost = web3.fromWei(estimateGasRestartQuest(token_input_array, difficulties_input_array, quest_input_array), 'gwei')
    account_balance = getWalletBalance()
    ret = True if account_balance - estimated_cost > 0 else False
    return ret

# Calls Function revealTokensQuests Locally
def callRevealQuest(token_input_array):
    function_call = None
    try:
        function_call = contract.functions.revealTokensQuests(token_input_array).call(constructTxRevealQuest())
    except exceptions.ContractLogicError as err:
        discord.sendWebhookFailure("revealTokensQuests", str(err))
    return function_call

# Calls Function restartTokenQuests Locally
def callRestartQuest(token_input_array, difficulties_input_array, quest_input_array):
    function_call = None
    try:
        function_call = contract.functions.restartTokenQuests(token_input_array, difficulties_input_array, quest_input_array).call(constructTxRestartQuest())
    except exceptions.ContractLogicError as err:
        discord.sendWebhookFailure("restartTokenQuests", str(err))
    return function_call

def executeRevealQuest(token_input_array):
    if checkBalanceIsEnoughForReveal(token_input_array) == False:
        return
    unsigned_tx = contract.functions.revealTokensQuests(token_input_array).buildTransaction(constructTxRevealQuest())
    signed_tx = web3.eth.account.sign_transaction(unsigned_tx, config.private)
    result = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    result_to_hex = result.hex()
    discord.sendWebhookPending(result_to_hex)

    (gas_used, fees_paid) = extractFieldsFromTransaction(result_to_hex)
    discord.sendWebhookSuccess("revealTokensQuests", result_to_hex, gas_used, fees_paid, getWalletBalance())
    return result

def executeRestartQuest(token_input_array, difficulties_input_array, quest_input_array):
    if checkBalanceIsEnoughForRestart(token_input_array, difficulties_input_array, quest_input_array) == False:
        return
    unsigned_tx = contract.functions.restartTokenQuests(token_input_array, difficulties_input_array, quest_input_array).buildTransaction(constructTxRestartQuest())
    signed_tx = web3.eth.account.sign_transaction(unsigned_tx, config.private)
    result = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    result_to_hex = result.hex()
    discord.sendWebhookPending(result_to_hex)

    (gas_used, fees_paid) = extractFieldsFromTransaction(result_to_hex)
    discord.sendWebhookSuccess("restartTokenQuests", result_to_hex, gas_used, fees_paid, getWalletBalance())
    return result
