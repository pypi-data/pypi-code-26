from threading import *
from socket import *
import subprocess

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
    def Server(cls, funct):     
        """
        Port -> One   : 15000
                Two   : 15897
                Three : 43201
                Four  : 32798
        """
        def wrap():
            try:
                cls.Stable_Server(15000, func=funct)
                return True
            except:    
                try:
                    cls.Stable_Server(15897, func=funct)
                except:
                    try:
                        cls.Stable_Server(43201, func=funct)
                    except:
                        try:
                            cls.Stable_Server(32798, func=funct)
                        except:
                            return False
        return wrap

    @classmethod
    def Server_RESPONSE_NULL(data):
        return data

    @classmethod
    def Stable_Client(cls, host, port, buffer=4096):
        try:
            NO_RES = subprocess.run("chcp 65001", shell=True, stdout=subprocess.PIPE)
        except:
             pass

        _HOST = host
        _PORT = port

        socket_backdoor = socket()
        socket_backdoor.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        socket_backdoor.connect((_HOST, _PORT))

        while True:
            command = input('>>>')
            socket_backdoor.send(command.encode())

            data = socket_backdoor.recv(buffer).decode()
            print(data)

        socket_backdoor.close()
        return None

    @classmethod
    def Stable_Server(cls, port, func=None, address='', _backlog=3, buffer=4096, listener=1):

        if _backlog == 0 or _backlog > 200:
            return False

        try:
            socket_server = socket()
            socket_server.bind((address,port))
            socket_server.listen(listener)

        except error as sk_error:
            cls.Stable_Server(port, _backlog=(_backlog-1))

        connection, (client_IP, client_PORT) = socket_server.accept()

        while True:
            try:

                _recieveData = connection.recv(buffer).decode()

                if func:
                    response = func(str(_recieveData))
                else:
                    response = cls.Server_RESPONSE_NULL(str(_recieveData))

                response = str(response)
                response = response.encode()

                connection.send(response)

            except:
                connection.send('Flag Error :: Server-Failed-Queue'.encode())
            
        connection.close()
        socket_server.close()
            

    @classmethod
    def Server_TCP(cls, port, func, address='', _backlog=3, buffer=4096, listener=1):
        
        if _backlog == 0 or _backlog > 500:
            return False

        while True:
            
            try:
                s = socket()
                s.bind((address,port))
                s.listen(listener)
                
            except error as sk_error:
                cls.Server_TCP(port, func, _backlog=(_backlog-1))

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
                    connection.send('Flag Error :: Server-Failed-Queue'.encode())
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
 
