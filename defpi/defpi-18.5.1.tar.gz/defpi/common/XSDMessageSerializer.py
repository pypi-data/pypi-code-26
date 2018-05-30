import glob
import importlib
import pyxb


class XSDMessageSerializer:

    def __init__(self):
        pyxb.RequireValidWhenGenerating(False)
        pyxb.RequireValidWhenParsing(False)
        self.xsdModule = []
        for name in glob.glob('/usr/local/defpi/service/model/*/xsd.py'):
            xsdModule = '.'.join(name[:-3].split('/'))
            self.xsdModule.append(importlib.import_module(xsdModule))

    def serialize(self, message):
        return message.toxml('utf-8')

    def deserialize(self, data, withName=False):
        try:
            obj = None
            for module in self.xsdModule:
                try:
                    obj = module.CreateFromDocument(data)
                except:
                    pass
            if obj is None:
                raise Exception('Unable to find parser for message type {}'.format(data[:30]))
            if withName:
                return obj, obj.__class__.__name__
            else:
                return obj
        except BaseException as e:
            raise Exception('Unable to parse message: {}'.format(e))
