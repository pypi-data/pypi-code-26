#!/usr/bin/python3
# -*- coding: utf-8 -*
"""
Copyright (c) 2018 Simon Wu <swprojects@runbox.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from forms.uiandroidpermissionsdialog import Ui_AndroidPermissionsDialog
from PyQt5.QtWidgets import QDialog, QCheckBox
from functools import partial
from spec.android_permissions import get_android_permissions


permissions = get_android_permissions()


class AndroidPermissionsDialog(QDialog, Ui_AndroidPermissionsDialog):

    def __init__(self, parent):
        super(AndroidPermissionsDialog, self).__init__(parent)

        self.ui = Ui_AndroidPermissionsDialog()
        self.ui.setupUi(self)
        self.permissionsList = self.ui.permissionsList
        self.gridPermissions = self.ui.gridPermissions

        self.checkBoxes = {}
        for p in permissions:
            c = QCheckBox(self)
            self.checkBoxes[p] = c
            c.setText(p)
            self.gridPermissions.addWidget(c)
            c.toggled.connect(partial(self.onCheckBox, p))

    @property
    def value(self):
        return self.permissionsList.text()

    def onCheckBox(self, permission, state):
        perm_list = self.value.split(',')
        new_list = {p for p in perm_list if p in permissions}
        if state is True:
            new_list.add(permission)
        else:
            new_list.remove(permission)
        new_list = sorted(list(new_list))
        self.permissionsList.setText(','.join(new_list))

    def setValue(self, value):
        perm_list = value.split(',')
        new_list = {p for p in perm_list if p in permissions}
        new_list = sorted(list(new_list))
        for p in new_list:
            chk = self.checkBoxes.get(p, None)
            if not chk:
                continue
            self.checkBoxes[p].setCheckState(2)
        self.permissionsList.setText(','.join(new_list))
