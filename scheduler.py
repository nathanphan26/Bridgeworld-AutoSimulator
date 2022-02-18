import config
import app
import time
import threading
import account as acc

# FIVE STATES THE PROCESS CAN BE IN
# 1: QUEST HASNT STARTED AND CAN REVEAL
# 2: QUEST HASNT STARTED AND REVEALED
# 3: QUEST STARTED AND CANT REVEAL YET
# 4: QUEST STARTED AND CAN REVEAL
# 5: QUEST STARTED AND REVEALED

def runQuest(account):
    print("{}: RUNNING QUEST FUNCTION FOR ACCOUNT...".format(account.id))

    seconds_until_questing = round(app.secondsLeftUntilQuesting(account), 0)        # Double check to see if quest is ready
    print("{}: SECONDS UNTIL QUESTING...: {}".format(account.id, str(seconds_until_questing)))

    while seconds_until_questing + 10 > 0:
        time.sleep(seconds_until_questing + 15)                                     # Sleep until ready
          
        seconds_until_questing = round(app.secondsLeftUntilQuesting(account), 0)
        print("{}: SECONDS UNTIL QUESTING...: {}".format(account.id, str(seconds_until_questing)))

    print("{}: QUESTING READY. STARTING QUEST FOR ACCOUNT...".format(account.id))
    app.executeRestartQuest(account, config.difficulties_input_array, config.quest_input_array)

    runReveal(account)
    
def runReveal(account):
    print("{}: RUNNING REVEAL FUNCTION FOR ACCOUNT...".format(account.id))

    isRevealReady = app.canReveal(account)      # Returns Error if revealed, False if waiting on reveal, and True if revealed
    print("{}: TOKEN READY FOR REVEAL?: {}".format(account.id, isRevealReady))

    if isRevealReady == 'Error':                # Revealed therefore runQuest
        runQuest(account)
    elif isRevealReady == 'False':              # Waiting on reveal therefore sleep until reveal
        print("{}: REVEAL NOT READY. SLEEPING FOR 4 MINUTES...".format(account.id))
        time.sleep(4 * 60)
        runReveal(account)
    elif isRevealReady == 'True':               # Ready to reveal therefore reveal
        print("{}: TOKEN READY FOR REVEAL. REVEALING TOKEN FOR ACCOUNT...".format(account.id))
        app.executeRevealQuest(account)
        runQuest(account)

def main():
    account_array = acc.init()
    for account in account_array:
        thread = threading.Thread(target=runReveal, args=(account,))
        thread.start()
        time.sleep(5)

main()