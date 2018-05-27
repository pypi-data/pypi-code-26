from threading import *
from socket import *

############################# CONNECTION CLASS ##############################

class Connection():

    NOT_RESULTS = []
    RESULTS = []
    ScreenLock = Semaphore(1)

    @classmethod
    def _PortScan(cls, SvcHost, SvcPort):
        
        try:
            SvcScan = socket(AF_INET, SOCK_STREAM)
            SvcScan.connect((SvcHost, SvcPort))

            SvcScan.send('flag\t'.encode())
            flag_value = SvcScan.recv(500)

            cls.ScreenLock.acquire()
            cls.RESULTS.append(SvcPort)

        except:
            cls.ScreenLock.acquire()
            cls.NOT_RESULTS.append(SvcPort)
            
        finally:       
            cls.ScreenLock.release()
            SvcScan.close()

    @classmethod
    def _HostConnect(cls, TcpHost, TcpPort=None):
        try:
            tgtIP = gethostbyname(TcpHost)

        except:
            return False

        try:
            tgtName = gethostbyaddr(tgtIP)
            
        except:
            tgtName = tgtIP

        setdefaulttimeout(1)
        
        if TcpPort:
            for ServerPort in TcpPort:

                _thread = Thread(target=cls._PortScan, args=(TcpHost, int(ServerPort)))
                _thread.start()
        else:
            
            for ServerPort in range(1, 100):

                _thread = Thread(target=cls._PortScan, args=(TcpHost, int(ServerPort)))
                _thread.start()
                
        _thread.join()
        return None

    @classmethod
    def Scan(cls, Host, Port, complete_result=False):
        
        if isinstance(Port, str):
            TargetPort = list(Port.split(","))
            
        elif isinstance(Port, (tuple,list,set,frozenset)):
            TargetPort = list(Port)

        else:
            raise ValueError("Ports must be in a tuple, or separated by commas in a string.")

        try:
            if complete_result:
                cls._HostConnect(Host, TargetPort)
                return (cls.RESULTS, cls.NOT_RESULTS)

            else:
                cls._HostConnect(Host, TargetPort)
                return cls.RESULTS

        except:
            return False

    @classmethod
    def scan(cls, Host, port):
        try:
            lonley_port = []
            lonley_port.append(port)
            
            cls._HostConnect(Host, lonley_port)
            if not cls.RESULTS:
                return False
            else:
                return True
        except:
            return None


    @classmethod
    def Server(cls, func):     
        """
        Port -> One   : 15000
                Two   : 15897
                Three : 43201
                Four  : 32798
        """
        def wrap():
            try:
                cls.Server_TCP(15000, func)
                return True
            except:    
                try:
                    cls.Server_TCP(15897, func)
                except:
                    try:
                        cls.Server_TCP(43201, func)
                    except:
                        try:
                            cls.Server_TCP(32798, func)
                        except:
                            return False
        return wrap


    @classmethod
    def Server_TCP(cls, port, func, address='', _backlog=3, buffer=4096):
        
        if _backlog == 0 or _backlog > 500:
            return False

        while True:
            
            try:
                s = socket()
                s.bind((address,port))
                s.listen(_backlog)
                
            except socket.error as sk_error:
                cls.Server_TCP(address, (_backlog-1))

            connection, client_address = s.accept()

            try:
                try:
                    _queue = connection.recv(buffer).decode()
                    res = func(str(_queue))
                    
                    res = str(res)
                    res = res.encode()
                    
                    connection.send(res)
                    connection.close()
                except:
                    connection.send('Flag Error : Server-Failed-Queue'.encode())
                    connection.close()
                    
            except:
                pass

        s.close()
        return True

    @classmethod
    def Client_Queue(cls, address, command, buffer=4096):
        
        try:
            s = socket()
            s.connect(address)
        except error as sk_error:
            return False

        try:
            command = str(command)
            command = command.encode()
            s.send(command)
            data = s.recv(buffer)
            s.close()
            return data.decode()
            
        except error as sk_error:
            raise sk_error
 
