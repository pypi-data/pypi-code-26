import pickle
from datatype import sendableData

def sendData(sock, data):
    data = sendableData(data)
    sock.send(data.get())

def getSendableData(data):
    data = sendableData()
    return data.get()
