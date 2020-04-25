import socket
from threading import Thread
import datetime
import pickle
import hashlib
import youtubequeue

musicTypes = None

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

last_upload_times = None
isRequestingScripts = False
# Connect the socket to the port where the server is listening
server_address = ('localhost', 11000)

def flagscript(scriptno, flagtype):
    print("%s VID GEN CLIENT requesting to flag script" % datetime.datetime.now())
    payload = ("flag-scripts", scriptno, flagtype)
    sendToServer(sock, payload)

def updateUploadDetails(scriptno, timeuploaded, scedualedrelease):
    payload = ("fin-script", scriptno, timeuploaded, scedualedrelease)
    sendToServer(sock, payload)

def login(username, password):
    payload = ("login-attempt-generator", username, hashlib.md5(password.encode()).hexdigest())
    sendToServer(sock, payload)

def getLastUploadedScripts():
    print("%s VID GEN CLIENT requesting last uploaded vids" % datetime.datetime.now())
    payload = ("last-uploaded",)
    sendToServer(sock, payload)

def sendToServer(server, payloadattachment):
    payload_attach = pickle.dumps(payloadattachment)
    HEADERSIZE = 10
    payload = bytes(f"{len(payload_attach):<{HEADERSIZE}}", 'utf-8') + payload_attach
    server.sendall(payload)

# change scriptIBuffer to scriptnos
def requestScripts(current_scripts):
    global isRequestingScripts
    isRequestingScripts = True
    print("%s VID GEN CLIENT requesting scripts current (%s)" % (datetime.datetime.now(), current_scripts))
    payload = ("video-generator-request-scripts", current_scripts)
    sendToServer(sock, payload)

def connectToServer():
    print('video generator connecting to %s port %s' % server_address)
    try:
        sock.connect(server_address)
    except ConnectionRefusedError:
        input("Could not connect to server. Press enter to continue")
        exit()
    thread = Thread(target=downloadListenThread)
    thread.start()


def downloadListenThread():
    global last_upload_times, isRequestingScripts, musicTypes
    print("Client listen thread active")
    HEADERSIZE = 10
    while True:
        full_msg = b''
        new_msg = True
        while True:
            try:
                buf = sock.recv(2048)
            except OSError:
                # happens when disconnecting
                break
            if new_msg:
                msglen = int(buf[:HEADERSIZE])
                print("%s VID GEN CLIENT new message (%s)" %( datetime.datetime.now(), msglen))
                new_msg = False

            full_msg += buf
            #print("%s VID GEN CLIENT received %s%% (%s/%s)" % (datetime.datetime.now(), round(len(full_msg) / msglen * 100, 2), str(len(full_msg) / 1000000) + "MB", str(msglen / 1000000) + "MB"))

            if len(full_msg) - HEADERSIZE == msglen:
                print("%s VID GEN CLIENT received full message (%s)" % (datetime.datetime.now(), len(full_msg) - HEADERSIZE))
                incomingdata = pickle.loads(full_msg[HEADERSIZE:])
                new_msg = True
                full_msg = b""
                if incomingdata[0] == "login-success":
                    print("VID GEN LOGIN SUCCESS")
                    pass
                elif incomingdata[0] == "script-send-to-generator":
                    scripts = incomingdata[1]
                    musicTypes = incomingdata[2]
                    print("%s VID GEN CLIENT received %s scripts" % (
                    datetime.datetime.now(), len(scripts)))
                    for script in scripts:
                        youtubequeue.scriptIBuffer.append(script)
                    youtubequeue.parseScripts()
                    isRequestingScripts = False
                elif incomingdata[0] == "last-uploaded":
                    last_times = incomingdata[1]
                    last_upload_times = last_times
                    print("%s VID GEN CLIENT received last upload times" % (
                    datetime.datetime.now()))

