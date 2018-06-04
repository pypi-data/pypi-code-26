import pickle
from datatype import sendableData

def recvData(sock, buffSize):
    recvd = sendableData(sock.recv(buffSize))
    return recvd.decoded()

def decodeRecvdData(data):
    data = sendableData(data)
    return data.decoded()
