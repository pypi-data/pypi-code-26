
from ms_lib import base_template



network_setting ={
    "addr": "192.168.86.10",
    "port": 4487,
    "ssl": {
        "cert": "jslarraz-auth.crt",
        "key": "jslarraz-auth.key"
    }
}

base_template(network_setting)