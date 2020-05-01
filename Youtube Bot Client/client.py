
import socket
from time import sleep
import sys
import pickle
from threading import Thread
import rawscriptsmenu
import hashlib
import videoscriptcore
import datetime
import publishmenu
import pandas as pd
import settings
from PyQt5 import QtWidgets
import configparser
from PyQt5.QtCore import *
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = (settings.server_address, int(settings.server_port))
access_key = None
loginwindowinstance = None
login_sucess = None
logged_in_as = None
sendingToServer = False
recievingFromServer = False
lastPing = None
addScriptResponse = None

musicTypes = None

class LoginWindow(QMainWindow):
    login_response = pyqtSignal()

    def __init__(self):
        QWidget.__init__(self)
        uic.loadUi("UI/login.ui", self)
        connectToServer()
        self.setWindowTitle("Login")
        self.login.clicked.connect(self.attemptLogin)
        self.login_response.connect(self.loginResponse)
        if not settings.auto_login_user == "":
            login(settings.auto_login_user, settings.auto_login_password, self)

    #admin icecream
    def attemptLogin(self):
        username = self.username.text()
        password = self.password.text()
        login(username, password, self)

    def loginResponse(self):
        if login_sucess:
            self.status.setText("Status: Login Success")
            self.close()
            self.rawscriptsmenu = rawscriptsmenu.ScriptsMenu(logged_in_as)
            self.rawscriptsmenu.show()
            downloadScripts(settings.amount_scripts_download, "ups")
        else:
            self.status.setText("Status: Login Fail")


def formatVideoScript(script):
    script_no = script.scriptno
    final_script = script.final_script
    videotype = script.videoType
    video_settings = script.videosettings
    music_type = script.music_type
    thumbnail = script.thumbnail
    characters_amount = script.charactersAmount
    youtube_title = script.youtube_title
    youtube_description = script.youtube_description
    youtube_tags = script.youtube_tags
    payload = (access_key, "upload-video", script_no, (final_script, videotype, video_settings, music_type, thumbnail, characters_amount, youtube_title, youtube_description, youtube_tags))
    sendToServer(sock, payload)


def connectToServer():
    print('connecting to %s port %s' % server_address)
    try:
        sock.connect(server_address)
        sock.settimeout(None)
    except ConnectionRefusedError:
        input("Could not connect to server. Press enter to continue")
        exit()
    thread = Thread(target=serverResponseListen)
    thread.start()
    thread = Thread(target=clientTick)
    thread.start()

def clientTick():
    global lastPing, recievingFromServer
    while True:
        sleep(1)
        if not sendingToServer and not recievingFromServer:
            if lastPing is None:
                sendToServer(sock, (access_key, "PING",))
                lastPing = datetime.datetime.now()
                print("%s CLIENT sending ping" % (datetime.datetime.now()))
            else:
                now = datetime.datetime.now()
                if not lastPing.minute == now.minute:
                    sendToServer(sock, (access_key, "PING",))
                    print("%s CLIENT sending ping (%s)" % (datetime.datetime.now(), now - lastPing))
                    lastPing = now


def login(username, password, loginwindowinstancearg = None):
    global loginwindowinstance, logged_in_as
    loginwindowinstance = loginwindowinstancearg
    logged_in_as = username
    payload = ("login-attempt", username, hashlib.md5(password.encode()).hexdigest())
    sendToServer(sock, payload)

def shutdown():
    print("CLIENT shut down")
    sock.shutdown(socket.SHUT_RDWR)


def flagscript(scriptno, flagtype):
    print("%s CLIENT requesting to flag script" % datetime.datetime.now())
    payload = (access_key, "flag-scripts", scriptno, flagtype)
    sendToServer(sock, payload)

def addScriptByURL(url):
    print("%s CLIENT attempting to add script %s" % (datetime.datetime.now(), url))
    payload = (access_key, "add-script", url)
    sendToServer(sock, payload)


def downloadScripts(amount, filter):
    global recievingFromServer
    recievingFromServer = True
    print("%s CLIENT requesting scripts" % datetime.datetime.now())
    payload = (access_key, "request-scripts", amount, filter)
    sendToServer(sock, payload)

def editScript(scriptNo):
    print("%s CLIENT requesting to edit script %s" % (datetime.datetime.now(), scriptNo))
    payload = (access_key, "edit-script", scriptNo)
    sendToServer(sock, payload)

def quitEditing(scriptNo):
    print("%s CLIENT requesting to edit script %s" % (datetime.datetime.now(), scriptNo))
    payload = (access_key, "quit-editing", scriptNo)
    sendToServer(sock, payload)

def safeDisconnect():
    print("%s CLIENT disconnecting" % (datetime.datetime.now()))
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
    exit()

def parseScripts(scripts):
    bannedWords = None

    if settings.censorWords:
        try:
            bannedWords = pd.read_csv("bannedwords.csv")
        except Exception as e:
            print(e)



    for i, script in enumerate(scripts):
        scriptno = script[0]
        subreddit = script[1]
        title = script[2]
        author = script[3]
        ups = script[4]
        downs = script[5]
        rawscript = script[6]
        subid = script[7]
        status = script[8]
        editedby = script[9]
        comments_amount = script[10]
        newscript = []
        for x, commentThread in enumerate(rawscript):
            comment_to_append = ()
            for y, comment in enumerate(commentThread):
                author_comment = comment[0]
                text_comment = comment[1]

                if settings.censorWords:
                    individual_words = text_comment.split(" ")
                    for word in individual_words:
                        for badWord in bannedWords["Banned Word"].tolist():
                            if word.upper() == badWord:
                                index = (bannedWords.index[bannedWords["Banned Word"] == word.upper()].tolist())[0]
                                text_comment = (text_comment.replace(word, bannedWords["Replacement"][index]))

                upvotes_comment = comment[2]

                comment_to_append = comment_to_append + (videoscriptcore.CommentWrapper(author_comment, text_comment, upvotes_comment), )
            newscript.append(comment_to_append)

        videoscriptcore.VideoScript(vidno=i, scriptno=scriptno, submission_id=subid, category=subreddit,
                                    title=title,
                                    author=author, upvotes=ups, comments=downs,
                                    videotype="standardredditformat",
                                    commentInformation=newscript, music_type="Funny", status=status, editedby=editedby, commentsamount=comments_amount)
    loginwindowinstance.rawscriptsmenu.addRawScriptsToTree()



def sendToServer(server, payloadattachment):
    global sendingToServer
    try:
        sendingToServer = True
        payload_attach = pickle.dumps(payloadattachment)
        HEADERSIZE = 10
        payload = bytes(f"{len(payload_attach):<{HEADERSIZE}}", 'utf-8') + payload_attach
        server.sendall(payload)
        sendingToServer = False
    except Exception:
        print("Socket Broken!")


def serverResponseListen():
    global access_key, loginwindowinstance, login_sucess, recievingFromServer, addScriptResponse, musicTypes
    print("Client listen thread active")
    HEADERSIZE = 10
    while True:
        full_msg = b''
        new_msg = True
        while True:
            try:
                buf = sock.recv(2048)
            except OSError:
                print("Socket Broken")
                break
            if new_msg:
                msglen = int(buf[:HEADERSIZE])
                print("%s CLIENT new message (%s)" %( datetime.datetime.now(), msglen))
                new_msg = False

            full_msg += buf
            recievingFromServer = True
            print("%s CLIENT received %s%% (%s/%s)" % (datetime.datetime.now(), round(len(full_msg) / msglen * 100, 2), str(len(full_msg) / 1000000) + "MB", str(msglen / 1000000) + "MB"))

            if len(full_msg) - HEADERSIZE == msglen:
                print("%s CLIENT received full message (%s)" % (datetime.datetime.now(), len(full_msg) - HEADERSIZE))
                incomingdata = pickle.loads(full_msg[HEADERSIZE:])
                new_msg = True
                recievingFromServer = False
                full_msg = b""
                if incomingdata[0] == "login-success":
                    login_success_arg = incomingdata[1]
                    access_key = incomingdata[2]
                    print("%s CLIENT received %s %s" % (datetime.datetime.now(), incomingdata[0], login_success_arg))
                    if loginwindowinstance is not None:
                        if login_success_arg:
                            login_sucess = True
                        else:
                            login_sucess = False
                        loginwindowinstance.login_response.emit()
                elif incomingdata[0] == "scripts-return":
                    data = incomingdata[1]
                    musicTypes = incomingdata[2]
                    print("%s CLIENT received %s scripts" % (datetime.datetime.now(), len(data)))
                    parseScripts(data)
                    break
                elif incomingdata[0] == "edit-script-success":

                    edit_script_success = incomingdata[1]
                    edit_script_id = incomingdata[2]
                    if loginwindowinstance is not None:
                        if edit_script_success:
                            loginwindowinstance.rawscriptsmenu.edit_response_true.emit()
                            print("%s CLIENT edit approval for script %s" % (datetime.datetime.now(), edit_script_id))

                        else:
                            loginwindowinstance.rawscriptsmenu.edit_response_false.emit()
                            print("%s CLIENT edit denied for script %s" % (datetime.datetime.now(), edit_script_id))
                elif incomingdata[0] == "script-status-update":
                    script_no = incomingdata[1]
                    script_status = incomingdata[2]
                    script_editedby = incomingdata[3]
                    print("%s CLIENT server updated script status %s to %s. User: %s" % (datetime.datetime.now(), script_no, script_status, script_editedby))
                    videoscriptcore.updateScriptStatus(script_no, script_status, script_editedby)
                    loginwindowinstance.rawscriptsmenu.update_table.emit()
                    #loginwindowinstance.rawscriptsmenu.addRawScriptsToTree()
                elif incomingdata[0] == "add-script-success":
                    success = incomingdata[1]
                    response = incomingdata[2]
                    print("%s CLIENT server received response for add script %s %s" % (datetime.datetime.now(), success, response))
                    addScriptResponse = response
                    loginwindowinstance.rawscriptsmenu.add_url_response.emit()
                    #videoscriptcore.updateScriptStatus(script_no, script_status, script_editedby)
                    #loginwindowinstance.rawscriptsmenu.update_table.emit()
                elif incomingdata[0] == "script-upload-success":
                    success = incomingdata[1]
                    scriptno = incomingdata[2]
                    if success:
                        print("%s CLIENT server successfully uploaded video %s" % (
                        datetime.datetime.now(), scriptno))
                        loginwindowinstance.rawscriptsmenu.reset_editing_status.emit()
                        publishmenu.currentPublishMenu.upload_success_true.emit()
                    else:
                        print("%s CLIENT server couldn't upload video %s" % (
                        datetime.datetime.now(), scriptno))
                        publishmenu.currentPublishMenu.upload_success_false.emit()
                elif incomingdata[0] == "PONG":
                    print("%s CLIENT recieved PONG" % (
                        datetime.datetime.now()))

    print("%s CLIENT disconnected" % datetime.datetime.now())

