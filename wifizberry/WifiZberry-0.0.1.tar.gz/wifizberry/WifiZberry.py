# -*- coding: utf-8 -*-
import re
import subprocess

from wifi import Cell

class WifiZberry(object):
    def __init__(self):
        self._list_wifi = []

    @classmethod
    def scan(self):
        self._list_wifi = []
        try:
            wifis = Cell.all('wlan0')
        except:
            wifis = Cell.all('wlp2s0')

        for wifi in wifis:
            self._list_wifi.append(wifi.ssid)
        return self._list_wifi

    @classmethod
    def connect(self, user, password):
        self.read_write_wifi_file(user,password)
        subprocess.call(['systemctl', 'daemon-reload'])
        subprocess.call(['systemctl', 'restart', 'dhcpcd'])
        print('Connected!')

    @classmethod
    def read_write_wifi_file(self, ssid, psk):
        newtext = ''
        with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'r') as file:
            for line in file:
                line = line.strip('\n')
                line = line.strip('	')
                if re.search(r'^ssid="[\w*|\s*"$]', line):
                    line = 'ssid="{}"'.format(ssid)
                if re.search(r'^psk=[\w*|\s*"$]', line):
                    line = 'psk="{}"'.format(psk)

                newtext += line + '\n'
            file.close()

        with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as file:
            file.write(newtext)
            file.close()

if __name__ == "__main__":
    #Test write file
    a = WifiZberry()
    a.read_write_wifi_file('Renan', '123')
