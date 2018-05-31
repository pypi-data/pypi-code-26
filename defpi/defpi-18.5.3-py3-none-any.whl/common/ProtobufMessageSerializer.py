import glob
import importlib


class ProtobufMessageSerializer:

    def __init__(self, user=False):
        self.protoModule = []
        if not user:
            self.protoModule.append(importlib.import_module('defpi.protobufs.Connection_pb2'))
            self.protoModule.append(importlib.import_module('defpi.protobufs.Service_pb2'))
        else:
            for name in glob.glob('/usr/local/defpi/service/model/*_pb2.py'):
                protoModule = '.'.join(name[:-3].split('/'))
                self.protoModule.append(importlib.import_module(protoModule))

    def serialize(self, message):
        msgTypeName = message.DESCRIPTOR.name
        msgTypeLen = len(msgTypeName).to_bytes(1, byteorder='big')

        return msgTypeLen + msgTypeName.encode() + message.SerializeToString()

    def deserialize(self, data, withName=False):
        msgTypeLen = data[0]
        if msgTypeLen <= 0:
            raise Exception('Received data is not a valid message: {}'.format(data))
        if len(data) < (msgTypeLen + 2):
            raise Exception('Received data is not a valid message: {}'.format(data))

        msgTypeName = data[1:(msgTypeLen+1)].decode()
        try:
            parser = None
            for module in self.protoModule:
                try:
                    testparser = getattr(module, msgTypeName)()
                    parser = testparser
                except:
                    pass
            if parser is None:
                raise Exception('Unable to find parser for message type {}'.format(msgTypeName))
            parser.ParseFromString(data[(msgTypeLen+1):])
            if withName:
                return parser, msgTypeName
            else:
                return parser
        except AttributeError as e:
            raise Exception('Unable to find parser for message type {}'.format(msgTypeName))
        except BaseException as e:
            raise Exception('Unable to parse message: {}'.format(e))
