
import os.path


address = "http://localhost"
port = 4300

def wwwroot():
    return os.path.dirname(__file__) + "/wwwroot"

def root_url():
    return address + ":" + str(port) + "/"

def url_for(path):
    return address + ":" + str(port) + "/api" + path

