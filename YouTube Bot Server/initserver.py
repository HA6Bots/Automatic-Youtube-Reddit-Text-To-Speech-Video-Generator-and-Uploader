import settings
settings.generateConfigFile()

import reddit
import socketserverhandler
import socketservervideogenerator
from time import sleep
import database
import datetime
from threading import Thread
import atexit

def getScripts():
    global lastUpdate
    print("Grabbing more scripts...")
    info = reddit.getInfo('AskReddit', settings.reddit_amount_posts)
    new_scripts = len([script for script in info if not script.update])
    updating_scripts = len([script for script in info if script.update])
    print("Adding %s new scripts, updating %s" % (new_scripts, updating_scripts))
    for script in info:
        if script.update:
            database.updateSubmission(script)
        else:
            database.addSubmission(script)
    lastUpdate = datetime.datetime.now()


lastUpdate = None

def updateScripts():

    while True:

        sleep(10)
        if lastUpdate is None:
            getScripts()

        now = datetime.datetime.now()
        if not lastUpdate.hour == now.hour:
            print("Getting more scripts - last update at %s" % lastUpdate)
            getScripts()



def init():
    socketserverhandler.startServer()
    socketservervideogenerator.startVideoGeneratorServer()
    thread = Thread(target=updateScripts)
    thread.start()

    #youtubequeue.initQueue()
    #socketclient.connectToServer()
    #print(checkValueExists("scriptid", "t5_2qh1i"))
    #updateScriptStatus("EDITING", "t5_2qh1i")
    #print(getVideoCountFromStatus("RAW"))
    #print(getRowCount("scripts"))x

def exit_handler():
    print("Safe Exit")
    socketserverhandler.socket.close()
    socketservervideogenerator.socket.close()

if __name__ == "__main__":
    atexit.register(exit_handler)
    init()