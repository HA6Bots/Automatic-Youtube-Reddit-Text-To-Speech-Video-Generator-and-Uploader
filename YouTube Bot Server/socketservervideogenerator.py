import settings
import socket
from time import sleep
from threading import Thread
import database
import datetime
import pickle

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

connectedVideoGenerator = None

class VideoGeneratorClient():
    def __init__(self, connection, address, authorized):
        self.connection = connection
        self.address = address
        self.authorized = authorized

def startVideoGeneratorServer():
    server_address = (settings.server_location, int(settings.server_port_vid_gen))
    print('Starting video generator server on %s port %s' % server_address)
    socket.bind(server_address)
    socket.listen(5)
    thread = Thread(target=waitConnect)
    thread.start()
    servertick = Thread(target=serverTick)
    servertick.start()

def waitConnect():
    print("Server Video Generator wait client thread started")
    global connectedVideoGenerator
    while True:
        if connectedVideoGenerator is None:
            connection, address = socket.accept()
            print("%s Video Generator connected on %s" % (datetime.datetime.now(), address))
            connectedVideoGenerator = (connection, address)
            clientthread = Thread(target=videoGeneratorTick)
            clientthread.start()

def sendToClient(client_connection, payloadattachment):
    try:
        payload_attach = pickle.dumps(payloadattachment)
        HEADERSIZE = 10
        payload = bytes(f"{len(payload_attach):<{HEADERSIZE}}", 'utf-8') + payload_attach
        client_connection.sendall(payload)
    except ConnectionResetError:
        print("Couldn't send message cuz client disconnected")

def videoGeneratorTick():
    global connectedVideoGenerator
    print("Server tick thread started for Video Generator")
    HEADERSIZE = 10
    disconnect = False
    while not disconnect:
        full_msg = b''
        new_msg = True
        while True:
            try:
                client_connection = connectedVideoGenerator[0]
                buf = client_connection.recv(2048)
                if new_msg:
                    try:
                        msglen = int(buf[:HEADERSIZE])
                    except ValueError:
                        # happens when client disconnects
                        disconnect = True
                        break
                    new_msg = False

                full_msg += buf
            except ConnectionResetError:
                print("%s VID GEN SERVER connecton reset error" % (datetime.datetime.now()))
                disconnect = True
                break
            download_size = len(full_msg) - HEADERSIZE
            if download_size == msglen:
                if download_size > 100000:
                    print(
                        "%s VID GEN SERVER received large message (%s)" % (datetime.datetime.now(), str(download_size / 1000000) + "MB"))
                try:
                    incomingdata = pickle.loads(full_msg[HEADERSIZE:])
                except EOFError:
                    print("%s VID GEN SERVER disconnected" % (datetime.datetime.now()))
                    break
                new_msg = True
                full_msg = b""
                if "video-generator-request-scripts" == incomingdata[0]:
                    current_scripts_in_generator = incomingdata[1]
                    print("%s VID GEN SERVER request scripts: current scripts %s" % (datetime.datetime.now(), current_scripts_in_generator))
                    scripts = retrieveScripts(current_scripts_in_generator)
                    sendToClient(client_connection, ('script-send-to-generator', scripts, settings.music_types))
                elif "flag-scripts" == incomingdata[0]:
                    scriptno = incomingdata[1]
                    flagtype = incomingdata[2]
                    database.updateScriptStatus(flagtype, None, scriptno)
                    print("%s VID GEN SERVER user %s flagging script %s as %s" % (
                        datetime.datetime.now(), None, scriptno, flagtype))
                elif "fin-script" == incomingdata[0]:
                    scriptno = incomingdata[1]
                    timeuploaded = incomingdata[2]
                    scedualedrelease = incomingdata[3]
                    database.completeUpload(scriptno, timeuploaded, scedualedrelease)
                    print("%s VID GEN SERVER completing script %s time uploaded %s scedualedrelease %s" % (
                        datetime.datetime.now(), scriptno, timeuploaded, scedualedrelease))
                elif "last-uploaded" == incomingdata[0]:
                    last_times = database.getLastUploadedScripts()
                    if last_times is None:
                        sendToClient(client_connection, ('last-uploaded', 0))
                    else:
                        sendToClient(client_connection, ('last-uploaded', last_times))
                    print("%s VID GEN SERVER sending last uploaded videos times" % (
                        datetime.datetime.now()))

    print("VID GEN CLIENT DISCONNECTED")
    connectedVideoGenerator = None

def retrieveScripts(scripts_in_generator):
    completed_scripts = database.getCompletedScripts(5)
    print("%s VID GEN SERVER downloaded %s video scripts from server" % (datetime.datetime.now(), len(completed_scripts)))
    scripts_to_send = []
    scriptnostosend = []
    for script in completed_scripts:
        if script[0] not in scripts_in_generator:
            scriptnostosend.append(script[0])
            scripts_to_send.append(script)
    print("%s VID GEN SERVER scripts to send %s (%s)" % (datetime.datetime.now(), len(scripts_to_send), scriptnostosend))
    return scripts_to_send

def serverTick():
    global connectedVideoGenerator
    while True:
        sleep(0.1)
        #print(database.getCompletedScripts())
