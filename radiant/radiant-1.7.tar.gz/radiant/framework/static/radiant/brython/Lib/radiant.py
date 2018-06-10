"""
Brython MDCFramework: Radiant
=============================



"""



from browser import ajax, window, websocket

#from tools import Tools
import json

########################################################################
class AndroidMain:
    """AndroidMain

    COnnectt with app

    """

    #----------------------------------------------------------------------
    def __init__(self, url=None, csrftoken=None):
        """Constructor"""

        self.url_ = url

        if csrftoken:
            self.csrftoken = csrftoken

        elif hasattr(window, 'csrftoken'):
            self.csrftoken = window.csrftoken
        else:
            self.csrftoken = "NO_CSRFTOKEN_PROVIDED"

        if url is None:
            #try:
                #self.url_ = '/'
                #self.test()
            #except:
            self.url_ = '/system_python'
            self.test()


    #----------------------------------------------------------------------
    def __getattr__(self, attr):
        """"""
        if attr.endswith('_async'):
            attr = attr.replace('_async', '')
            f = lambda *args, **kwargs: self.__request_async__(attr, *args, **kwargs)
        else:
            f = lambda *args, **kwargs: self.__request__(attr, *args, **kwargs)

        f.__name__ = attr
        return f


    #----------------------------------------------------------------------
    def __request__(self, attr, *args, **kwargs):
        """"""
        req = ajax.ajax()
        req.open('POST', self.url_, False)
        req.set_header('content-type','application/x-www-form-urlencoded')
        req.send({'name': attr, 'args': args, 'kwargs': kwargs, 'csrfmiddlewaretoken': self.csrftoken})
        return json.loads(req.text)['__RDNT__']


    #----------------------------------------------------------------------
    def __request_async__(self, attr, *args, **kwargs):
        """"""
        def __ajax__(fn):
            req = ajax.ajax()
            req.bind('complete', fn)
            req.open('POST', self.url_, True)
            req.set_header('content-type','application/x-www-form-urlencoded')
            req.send({'name': attr, 'args': args, 'kwargs': kwargs, 'csrfmiddlewaretoken': self.csrftoken})

        return __ajax__



########################################################################
class Exporter(AndroidMain):
    """Exporter

    COnnectt with app

    """

    #----------------------------------------------------------------------
    def __init__(self, url='/system_brython_export', csrftoken=None):
        """Constructor"""
        super().__init__(url, csrftoken)



########################################################################
class WebSocket:
    """WebSocket

    COnnectt with app

    """

    #----------------------------------------------------------------------
    def __init__(cls, ip):
        """"""
        if not websocket.supported:
            print("WebSocket is not supported by your browser")
            return
        # open a web socket
        #cls.ws = websocket.WebSocket("wss://192.168.1.20:8888")
        cls.ws = websocket.WebSocket(ip)
        # bind functions to web socket events
        cls.ws.bind('open', cls.on_open)
        cls.ws.bind('error', cls.on_error)
        cls.ws.bind('message', cls.on_message)
        cls.ws.bind('close', cls.on_close)

        print("Connectting to {}".format(ip))


        port_ip = ip.replace('wss://', '').replace('ws://', '').replace('/ws', '')

        # print(port_ip)


        #cls.ip = port_ip[:port_ip.find(":")]
        #cls.port =  port_ip[port_ip.find(":")+1:]
        cls.ip = port_ip
        cls.protocol = 'wss' if 'wss' in ip else 'ws'



    #----------------------------------------------------------------------
    def on_open(cls, evt):
        """"""
        print("Websocket engage.")


    # #----------------------------------------------------------------------
    # def on_connected(self, fn):
        # """"""
        # fn()



    #----------------------------------------------------------------------
    def on_error(cls, evt):
        """"""
        print("Error.")


    #----------------------------------------------------------------------
    def on_message(cls, evt):
        """"""
        print("Message received: {}".format(evt.data))


    #----------------------------------------------------------------------
    def on_close(cls, evt):
        """"""
        print("Websocket closed.")


    #----------------------------------------------------------------------
    def send(cls, data):
        """"""
        if data:
            cls.ws.send(data)


    #----------------------------------------------------------------------
    def close_connection(cls, ev):
        """"""
        cls.ws.close()
