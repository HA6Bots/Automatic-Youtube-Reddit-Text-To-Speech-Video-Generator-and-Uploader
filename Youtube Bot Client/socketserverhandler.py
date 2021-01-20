import socket as pythonsocket
from threading import Thread
from time import sleep
import datetime
import pickle
import datetime
import database
import reddit
import string
import random
import settings

socket = pythonsocket.socket(pythonsocket.AF_INET, pythonsocket.SOCK_STREAM)


def startServer():
    database.beginDataBaseConnection()
    database.initDatabase()
    server_address = (settings.server_location, int(settings.server_port))
    print('Starting server on %s port %s' % server_address)
    socket.setsockopt(pythonsocket.SOL_SOCKET, pythonsocket.SO_REUSEADDR, 1)
    socket.settimeout(None)
    socket.bind(server_address)
    socket.listen(5)
    socket.settimeout(None)
    thread = Thread(target=waitConnect)
    thread.start()
    servertick = Thread(target=serverTick)
    servertick.start()


clients = []


class Client():
    def __init__(self, connection, address, authorized):
        self.connection = connection
        self.address = address
        self.authorized = authorized
        self.key = None
        self.username = None
        self.editingScript = None
        self.disconnect = False
        self.lastPing = datetime.datetime.now()
        self.scriptsComplete = []


def waitConnect():
    print("Server wait client thread started")
    while True:
        sleep(0.1)
        connection, address = socket.accept()
        print("%s Client connected on %s" % (datetime.datetime.now(), address))
        client = Client(connection, address, False)
        clients.append(client)
        clientthread = Thread(target=clientTick, args=[clients[len(clients) - 1]])
        clientthread.start()


def getAllClientConnections():
    return [client.connection for client in clients]


def sendToAllClients(payload):
    for client_con in getAllClientConnections():
        try:
            sendToClient(client_con, payload)
        except Exception:
            print("couldn't send to connection %s" % client_con)


def clientTick(client):
    print("Server tick thread started for client")
    HEADERSIZE = 10
    while True:
        if client.disconnect:
            print("%s SERVER user %s disconnected" % (datetime.datetime.now(), repr(client.username)))
            break
        full_msg = b''
        new_msg = True
        while True:
            try:
                client_connection = client.connection
                buf = client_connection.recv(2048)
                if new_msg:
                    try:
                        msglen = int(buf[:HEADERSIZE])
                    except ValueError:
                        print("client disconnect error")
                        # happens when client disconnects
                        break
                    new_msg = False

                full_msg += buf
            except ConnectionResetError:
                print("%s SERVER user %s connecton reset error" % (datetime.datetime.now(), repr(client.username)))
                break
            download_size = len(full_msg) - HEADERSIZE
            if download_size == msglen:
                if download_size > 100000:
                    print(
                        "%s SERVER received large message (%s)" % (
                        datetime.datetime.now(), str(download_size / 1000000) + "MB"))
                try:
                    incomingdata = pickle.loads(full_msg[HEADERSIZE:])
                except EOFError:
                    print("%s SERVER user %s disconnected" % (datetime.datetime.now(), repr(client.username)))
                    break
                new_msg = True
                full_msg = b""

                if not client.authorized:
                    if "login-attempt" == incomingdata[0]:
                        print("%s SERVER user %s login attempt" % (datetime.datetime.now(), repr(incomingdata[1])))
                        username = incomingdata[1]
                        password = incomingdata[2]
                        login = (database.login(username, password))
                        online_users = database.getOnlineUsers()
                        if username in online_users:
                            print("%s SERVER user %s already logged in" % (
                            datetime.datetime.now(), repr(incomingdata[1])))
                            sendToClient(client_connection, ("login-success", False, None))
                        else:
                            if login:
                                key = generateKey()
                                client.key = key
                                client.username = username
                                sendToClient(client_connection, ("login-success", True, key))
                                client.authorized = True
                                print("%s SERVER user %s logged in" % (datetime.datetime.now(), repr(incomingdata[1])))
                                database.updateUserStatus(username, "ONLINE")
                            else:
                                sendToClient(client_connection, ("login-success", False, None))
                                print("%s SERVER user %s wrong password" % (
                                datetime.datetime.now(), repr(incomingdata[1])))

                else:
                    if "request-scripts" == incomingdata[1]:
                        print("%s SERVER user %s request scripts" % (datetime.datetime.now(), repr(client.username)))
                        if incomingdata[0] == client.key:
                            print("%s SERVER sending scripts to user %s" % (
                            datetime.datetime.now(), repr(client.username)))
                            amount = incomingdata[2]
                            filter = incomingdata[3]
                            if filter == "ups":
                                data = database.getScripts(amount, "ups")
                                sendToClient(client_connection, ("scripts-return", data, settings.music_types))
                            elif filter == "latest posts":
                                data = database.getScripts(amount, "timecreated")
                                sendToClient(client_connection, ("scripts-return", data, settings.music_types))
                            elif filter == "recently added":
                                data = database.getScripts(amount, "timegathered")
                                sendToClient(client_connection, ("scripts-return", data, settings.music_types))
                            elif filter == "comments":
                                data = database.getScripts(amount, "num_comments")
                                sendToClient(client_connection, ("scripts-return", data, settings.music_types))

                            pass
                        else:
                            print("%s SERVER user %s key does not match up" % (
                            datetime.datetime.now(), repr(client.username)))
                    elif "edit-script" == incomingdata[1]:
                        scriptno = incomingdata[2]
                        print("%s SERVER user %s request to edit script %s" % (
                        datetime.datetime.now(), repr(client.username), scriptno))
                        if incomingdata[0] == client.key:
                            script_status = database.getScriptStatus(scriptno)
                            if script_status == "RAW":
                                print("%s SERVER allowing user %s to edit script %s" % (
                                    datetime.datetime.now(), repr(client.username), scriptno))
                                client.editingScript = scriptno
                                database.updateScriptStatus("EDITING", client.username, scriptno)
                                sendToClient(client.connection, ('edit-script-success', True, scriptno))
                                sendToAllClients(('script-status-update', scriptno, "EDITING", client.username))
                                print("%s SERVER sending all clients (%s) status update for %s" % (
                                datetime.datetime.now(), len(getAllClientConnections()), scriptno))
                            elif script_status == "EDITING":
                                print("%s SERVER refusing user %s to edit script %s" % (
                                    datetime.datetime.now(), repr(client.username), scriptno))
                                sendToClient(client.connection, ('edit-script-success', False, scriptno))
                        else:
                            print("%s SERVER user %s key does not match up" % (
                            datetime.datetime.now(), repr(client.username)))
                    elif "upload-video" == incomingdata[1]:
                        if incomingdata[0] == client.key:
                            scriptno = incomingdata[2]
                            video_generator_payload = incomingdata[3]
                            script_status = database.getScriptStatus(scriptno)
                            if script_status == "EDITING":
                                if scriptno == client.editingScript:
                                    print("%s SERVER allowing user %s to upload script number %s" % (
                                    datetime.datetime.now(), repr(client.username), scriptno))
                                    if database.uploadVid(video_generator_payload, scriptno):
                                        database.updateScriptStatus("COMPLETE", client.username, scriptno)
                                        sendToClient(client_connection, ('script-upload-success', True, scriptno))
                                        client.scriptsComplete.append(scriptno)
                                        client.editingScript = None
                                    else:
                                        sendToClient(client_connection, ('script-upload-success', False, scriptno))

                                    sendToAllClients(('script-status-update', scriptno, "COMPLETE", client.username))

                                else:
                                    print(
                                        "%s SERVER user %s script number %s does not match what client is editing %s" % (
                                            datetime.datetime.now(), repr(client.username), scriptno,
                                            client.editingScript))

                            else:
                                print("%s SERVER user %s script status is %s" % (
                                    datetime.datetime.now(), repr(client.username), script_status))

                        else:
                            print("%s SERVER user %s key does not match up" % (
                            datetime.datetime.now(), repr(client.username)))

                    elif "quit-editing" == incomingdata[1]:
                        if incomingdata[0] == client.key:
                            scriptno = incomingdata[2]
                            if client.editingScript == scriptno:
                                database.updateScriptStatus("RAW", None, scriptno)
                                print("%s SERVER user %s quit editing %s" % (
                                    datetime.datetime.now(), repr(client.username), scriptno))
                                sendToAllClients(('script-status-update', scriptno, "RAW", None))

                                client.editingScript = None
                            else:
                                print("%s SERVER user %s not editing script %s" % (
                                datetime.datetime.now(), repr(client.username), scriptno))
                        else:
                            print("%s SERVER user %s key does not match up" % (
                            datetime.datetime.now(), repr(client.username)))

                    elif "flag-scripts" == incomingdata[1]:
                        if incomingdata[0] == client.key:
                            scriptno = incomingdata[2]
                            flagtype = incomingdata[3]
                            database.updateScriptStatus(flagtype, client.username, scriptno)
                            print("%s SERVER user %s flagging script %s as %s" % (
                                datetime.datetime.now(), repr(client.username), scriptno, flagtype))
                            sendToAllClients(('script-status-update', scriptno, flagtype, client.username))
                            client.editingScript = None
                        else:
                            print("%s SERVER user %s key does not match up" % (
                            datetime.datetime.now(), repr(client.username)))

                    elif "add-script" == incomingdata[1]:
                        if incomingdata[0] == client.key:
                            url = incomingdata[2]
                            try:
                                post = reddit.getPostByUrl(url)

                                if post is not None:

                                    all_scripts = database.getScriptIds()

                                    scriptIds = [scriptid[1] for scriptid in all_scripts]
                                    print("Got script ids")
                                    if post.submission_id in scriptIds:
                                        print("Found script with same id")
                                        database.updateScriptStatusById("RAW", client.username, post.submission_id)
                                        print("Set it to raw.")
                                        database.updateSubmission(post)
                                        print("Updated submission")
                                        print("%s SERVER user %s reset script %s" % (
                                        datetime.datetime.now(), repr(client.username), post.submission_id))
                                        sendToClient(client_connection,
                                                     ('add-script-success', True, "Reset script"))
                                    else:
                                        print("%s SERVER user %s added script %s" % (
                                        datetime.datetime.now(), repr(client.username), post.submission_id))
                                        database.addSubmission(post)
                                        sendToClient(client_connection,
                                                     ('add-script-success', True, "Successfully added script"))

                                else:
                                    print("%s SERVER user %s attempted to add script that already exists" % (
                                        datetime.datetime.now(), repr(client.username)))
                                    sendToClient(client_connection,
                                                 ('add-script-success', False, "Error occured with url."))
                            except Exception as e:
                                print("%s SERVER user %s error attempting to add script %s" % (
                                    datetime.datetime.now(), repr(client.username), url))
                                print(e)
                                sendToClient(client_connection,
                                             ('add-script-success', False, "An error occured trying to add the script"))

                        else:
                            print("%s SERVER user %s key does not match up" % (
                            datetime.datetime.now(), repr(client.username)))

                    elif "PING" == incomingdata[1]:
                        if incomingdata[0] == client.key:
                            client.lastPing = datetime.datetime.now()
                            print("%s SERVER sending PONG to %s" % (datetime.datetime.now(), repr(client.username)))
                            sendToClient(client.connection, ('PONG',))
                        else:
                            print("%s SERVER user %s key does not match up" % (
                            datetime.datetime.now(), repr(client.username)))

                    if (datetime.datetime.now().minute - client.lastPing.minute) > 2:
                        print("%s SERVER no PING from %s in 2 minutes. Disconnecting" % (
                        datetime.datetime.now(), repr(client.username)))
                        client.disconnect = True

        print("%s SERVER Thread shutting down" % datetime.datetime.now())
        client.disconnect = True
        break


def sendToClient(client_connection, payloadattachment):
    payload_attach = pickle.dumps(payloadattachment)
    HEADERSIZE = 10
    payload = bytes(f"{len(payload_attach):<{HEADERSIZE}}", 'utf-8') + payload_attach
    client_connection.sendall(payload)


def handleCompletedScripts():
    while True:
        pass


def serverTick():
    global clients
    while True:
        sleep(0.1)
        scriptsbeingedited = database.getScriptEditInformation()  # gets information of scripts with EDITING status
        sciptsbeingeditedby = [editedby[2] for editedby in scriptsbeingedited]  # gets names of scripts with editedby
        online_users = database.getOnlineUsers()
        clientIndexToRemove = []
        if clients:
            for i, client in enumerate(clients):

                if client.username in sciptsbeingeditedby:
                    indexOfScript = sciptsbeingeditedby.index(client.username)
                    scriptno = scriptsbeingedited[indexOfScript][0]

                    # set script client was editing to raw
                    if not client.editingScript == scriptno and scriptno not in client.scriptsComplete:
                        print("%s SERVER setting status of script %s to RAW because client is not editing it" % (
                        datetime.datetime.now(), scriptno))
                        database.updateScriptStatus("RAW", None, scriptno)
                        for client_con in getAllClientConnections():
                            sendToClient(client_con, ('script-status-update', scriptno, "RAW", None))

                if client.disconnect:  # if client disconnects set script to raw
                    clientIndexToRemove.append(i)

        else:
            if scriptsbeingedited:
                for script in scriptsbeingedited:
                    database.updateScriptStatus("RAW", None, script[0])
                    for client_con in getAllClientConnections():
                        sendToClient(client_con, ('script-status-update', scriptno, "RAW", None))
                print("%s SERVER setting status of all scrips to RAW as there are no clients." % (
                    datetime.datetime.now()))
            if online_users:
                for user in online_users:
                    database.updateUserStatus(user, None)
                    print("%s SERVER removing online status for %s as there are no clients" % (
                    datetime.datetime.now(), user))

        if clientIndexToRemove:
            for index in clientIndexToRemove:
                print("deleted clients")
                try:
                    if clients[index].username is not None:
                        database.updateUserStatus(clients[index].username, None)
                        for client in clients:
                            if not client.disconnect:
                                sendToClient(client.connection,
                                             ('script-status-update', clients[index].editingScript, "RAW", None))
                except IndexError:
                    pass

                try:
                    new_clients = []
                    for i in range(len(clients)):
                        if not clients[index] == clients[i]:
                            new_clients.append(clients[i])
                    clients = new_clients
                except IndexError:
                    print("could not update client list")
        if scriptsbeingedited:
            pass


def generateKey():
    """Generate a random string of letters, digits and special characters """
    password_characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(password_characters) for i in range(10))
