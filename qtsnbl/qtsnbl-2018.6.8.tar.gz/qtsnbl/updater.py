#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from PyQt5 import QtCore, QtWidgets, QtNetwork


class WUpdates(QtWidgets.QMessageBox):
    sigNewVersion = QtCore.pyqtSignal(str, bool)

    def __init__(self, parent, version):
        super().__init__(parent)
        self.version = version
        self.checkUpdatesByUser = False
        self.web = QtNetwork.QNetworkAccessManager()
        self.url = QtCore.QUrl(self.version.url)
        # noinspection PyUnresolvedReferences
        self.web.finished.connect(self.parse)
        self.sigNewVersion.connect(self.showNewVersion)
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle('Check updates')
        self.setStandardButtons(self.Ok)
        self.cb = QtWidgets.QCheckBox('Do not check updates automatically')
        self.setCheckBox(self.cb)

    def error(self, text):
        self.setIcon(self.Critical)
        self.setText('There has been an error during update checking')
        self.setInformativeText(text)
        self.exec()

    def success(self, main, info):
        self.setIcon(self.Information)
        if info:
            self.setText(main)
            self.setInformativeText(info)
        else:
            self.setText('There are no new updates')
        self.exec()

    def loadSettings(self):
        s = QtCore.QSettings()
        self.cb.setChecked(s.value('Version/doNotCheckUpdates', False, bool))

    def saveSettings(self):
        s = QtCore.QSettings()
        s.setValue('Version/doNotCheckUpdates', self.cb.isChecked())

    def checkNewVersion(self):
        if not self.version.url or self.cb.isChecked():
            return
        self.checkUpdatesByUser = False
        self.check()

    def checkNewVersionByUser(self):
        if not self.version.url:
            return
        self.checkUpdatesByUser = True
        self.check()

    def showNewVersion(self, text, error):
        if self.checkUpdatesByUser:
            self.error(text) if error else self.success(self.version.text, text)
        else:
            if not error and not self.cb.isChecked() and text:
                self.success(self.version.text, text)
        self.checkUpdatesByUser = False

    def check(self):
        self.web.get(QtNetwork.QNetworkRequest(self.url))

    def parse(self, reply):
        text = reply.readAll().data().decode(errors='ignore')
        current = datetime.datetime(*[int(i) for i in self.version.string.split('.')])
        strings = []
        put = False
        boldline = False
        first = True
        parsing = False
        for line in text.split('\n'):
            if not line:
                continue
            if line == self.version.token:
                parsing = True
                continue
            if parsing:
                if line.startswith('..'):
                    continue
                items = line.split()
                try:
                    newv = [int(i) for i in items[1].split('.')]
                except (IndexError, ValueError):
                    pass
                else:
                    try:
                        put = datetime.datetime(*newv) > current
                    except ValueError:
                        pass
                    boldline = True
                if put:
                    line = line.strip()
                    line = line[line.index(" ") + 1:]
                    if boldline:
                        boldline = False
                        if not first:
                            strings.append('</ul>')
                        strings.append(f'<span style="font-weight: bold; color: red">{line}</span>'
                                       f'<ul style="list-style-type:disc">')
                    else:
                        strings.append(f'<li>{line}</li>')
                    first = False
        if strings:
            strings.append('</ul>')
        self.sigNewVersion.emit('\n'.join(strings), False)
