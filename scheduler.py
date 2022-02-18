import config
import app
import time

# FIVE STATES THE PROCESS CAN BE IN
# 1: QUEST HASNT STARTED AND CAN REVEAL
# 2: QUEST HASNT STARTED AND REVEALED
# 3: QUEST STARTED AND CANT REVEAL YET
# 4: QUEST STARTED AND CAN REVEAL
# 5: QUEST STARTED AND REVEALED

def runQuest(tokenId):
    print("RUNNING QUEST FUNCTION...")
    token_array = [tokenId]

    seconds_until_questing = round(app.secondsLeftUntilQuesting(tokenId), 0)        # Double check to see if quest is ready
    print("SECONDS UNTIL QUESTING...: " + str(seconds_until_questing))

    while seconds_until_questing + 10 > 0:
        time.sleep(seconds_until_questing + 15)                                     # Sleep until ready
        
        seconds_until_questing = round(app.secondsLeftUntilQuesting(tokenId), 0)    
        print("SECONDS UNTIL QUESTING...: " + str(seconds_until_questing))

    print("QUESTING READY. STARTING QUEST...")
    app.executeRestartQuest(token_array, config.difficulties_input_array, config.quest_input_array)

    runReveal(tokenId)
    

def runReveal(tokenId):
    print("RUNNING REVEAL FUNCTION...")
    token_array = [tokenId]

    isRevealReady = app.canReveal(tokenId)      # Returns Error if revealed, False if waiting on reveal, and True if revealed
    print("TOKEN READY FOR REVEAL?: " + isRevealReady)

    if isRevealReady == 'Error':                # Revealed therefore runQuest
        runQuest(tokenId)
    elif isRevealReady == 'False':              # Waiting on reveal therefore sleep until reveal
        print("REVEAL NOT READY. SLEEPING FOR 4 MINUTES...")
        time.sleep(4 * 60)
        runReveal(tokenId)
    elif isRevealReady == 'True':               # Ready to reveal therefore reveal
        print("TOKEN READY FOR REVEAL. REVEALING TOKEN...")
        app.executeRevealQuest(token_array)
        runQuest(tokenId)

def main():
    runReveal(config.token_input_array_list[0][0])

main()