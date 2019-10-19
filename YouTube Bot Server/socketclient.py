
import socket
from time import sleep
import sys
import pickle
from threading import Thread
import hashlib
import datetime

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 10000)
access_key = None

def connectToServer():
    print('connecting to %s port %s' % server_address)
    sock.connect(server_address)

    thread = Thread(target=serverResponseListen)
    thread.start()
    login("admin", "icecream")

def login(username, password):
    payload = ("login-attempt", username, hashlib.md5(password.encode()).hexdigest())
    data = pickle.dumps(payload)
    sock.sendall(data)

def shutdown():
    print("CLIENT shut down")
    sock.shutdown(socket.SHUT_RDWR)


def downloadScripts(amount):
    print("%s CLIENT requesting scripts" % datetime.datetime.now())
    payload = (access_key, "request-scripts", amount)
    data = pickle.dumps(payload)
    sock.sendall(data)

def editScript(scriptNo):
    print("%s CLIENT requesting to edit script %s" % (datetime.datetime.now(), scriptNo))
    payload = (access_key, "edit-script", scriptNo)
    data = pickle.dumps(payload)
    sock.sendall(data)

def safeDisconnect():
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()

def serverResponseListen():
    global access_key
    print("Client listen thread active")
    while True:
        sleep(0.1)
        buf = sock.recv(800000)
        incomingdata = pickle.loads(buf)
        if incomingdata[0] == "login-success":
            login_success = incomingdata[1]
            access_key = incomingdata[2]
            print("%s CLIENT received %s %s" % (datetime.datetime.now(), incomingdata[0], login_success))
            downloadScripts(30)
        elif incomingdata[0] == "scripts-return":
            data = incomingdata[1]
            print("%s CLIENT received %s scripts" % (datetime.datetime.now(), len(data)))
            editScript(29)
            sleep(10)
            safeDisconnect()
            break
    print("%s CLIENT disconnected" % datetime.datetime.now())

