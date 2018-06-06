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

from forms.uisettingsdialog import Ui_SettingsDialog
from PyQt5.QtWidgets import QDialog
from functools import partial
import logging


class SettingsDialog(QDialog, Ui_SettingsDialog):

    def __init__(self, parent):
        super(SettingsDialog, self).__init__(parent)

        self.parent = parent
        self.configDefaults = {}
        self.config = {}
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)
        self.checkBoxes = {}
        self.uiObjects = {}
        self.collectUiObjects()
        self.open()

    def collectUiObjects(self):
        logging.debug(self.ui.__dict__.keys())
        for n, obj in self.ui.__dict__.items():
            if n.startswith('checkBox_'):
                self.checkBoxes[n[9:]] = obj
            elif n.startswith('lineEdit_'):
                self.uiObjects[n[9:]] = obj
            elif n.startswith('textEdit_'):
                self.uiObjects[n[9:]] = obj
            elif n.startswith('default_'):
                obj.clicked.connect(partial(self.restoreDefaultCommand, n[8:]))

    def onApply(self, button):
        if button.text() != 'Apply':
            return
        value = self.value()
        self.parent.updateConfig(value)

    def restoreDefaultCommand(self, command):
        if command == 'CustomSpec':
            value = self.configDefaults.get('custom_spec', '')
            self.uiObjects[command].setText(str(value))
            return

        c = 'override_{0}_cmd'.format(command.lower())
        try:
            value = self.configDefaults.get(c, None)
            self.uiObjects[command].setText(value)
        except Exception as e:
            logging.debug(e)

    def updateGeneral(self):
        config = self.config
        ask_save_on_close = config.get('ask_save_on_close', True)
        if ask_save_on_close:
            self.checkBoxes['AskSaveOnClose'].setCheckState(2)
        else:
            self.checkBoxes['AskSaveOnClose'].setCheckState(0)

        show_splashscreen = config.get('show_splashscreen', True)
        if show_splashscreen:
            self.checkBoxes['SplashScreen'].setCheckState(2)
        else:
            self.checkBoxes['SplashScreen'].setCheckState(0)

        keep_recent_files = config.get('keep_recent_files', True)
        if keep_recent_files:
            self.checkBoxes['RecentFiles'].setCheckState(2)
        else:
            self.checkBoxes['RecentFiles'].setCheckState(0)

    def updateBlacklist(self):
        config = self.config
        use_app_blacklist = config.get('use_app_blacklist', False)
        if use_app_blacklist:
            self.checkBoxes['BlacklistApp'].setCheckState(2)
        else:
            self.checkBoxes['BlacklistApp'].setCheckState(0)

        use_buildozer_blacklist = config.get('use_buildozer_blacklist', False)
        if use_buildozer_blacklist:
            self.checkBoxes['BlacklistBuildozer'].setCheckState(2)
        else:
            self.checkBoxes['BlacklistBuildozer'].setCheckState(0)

        app_blacklist = config.get('app_blacklist', '')
        self.uiObjects['BlacklistApp'].insertPlainText(str(app_blacklist))

        buildozer_blacklist = config.get('buildozer_blacklist', '')
        self.uiObjects['BlacklistBuildozer'].insertPlainText(str(buildozer_blacklist))

    def updateSubstitute(self):
        config = self.config
        use_app_substitute = config.get('use_app_substitute', False)
        if use_app_substitute:
            self.checkBoxes['SubApp'].setCheckState(2)
        else:
            self.checkBoxes['SubApp'].setCheckState(0)

        use_buildozer_substitute = config.get('use_buildozer_substitute', False)
        if use_buildozer_substitute:
            self.checkBoxes['SubBuildozer'].setCheckState(2)
        else:
            self.checkBoxes['SubBuildozer'].setCheckState(0)

        app_substitute = config.get('app_substitute', '')
        self.uiObjects['SubApp'].insertPlainText(str(app_substitute))

        buildozer_substitute = config.get('buildozer_substitute', '')
        self.uiObjects['SubBuildozer'].insertPlainText(str(buildozer_substitute))

    def updateCommands(self):
        config = self.config
        override = config.get('override_build', False)
        if override:
            self.checkBoxes['Build'].setCheckState(2)
        else:
            self.checkBoxes['Build'].setCheckState(0)

        override = config.get('override_clean', False)
        if override:
            self.checkBoxes['Clean'].setCheckState(2)
        else:
            self.checkBoxes['Clean'].setCheckState(0)

        override = config.get('override_deploy', False)
        if override:
            self.checkBoxes['Deploy'].setCheckState(2)
        else:
            self.checkBoxes['Deploy'].setCheckState(0)

        override = config.get('override_distclean', False)
        if override:
            self.checkBoxes['Distclean'].setCheckState(2)
        else:
            self.checkBoxes['Distclean'].setCheckState(0)

        override = config.get('override_run', False)
        if override:
            self.checkBoxes['Run'].setCheckState(2)
        else:
            self.checkBoxes['Run'].setCheckState(0)

        override = config.get('override_serve', False)
        if override:
            self.checkBoxes['Serve'].setCheckState(2)
        else:
            self.checkBoxes['Serve'].setCheckState(0)

        override = config.get('override_terminal', False)
        if override:
            self.checkBoxes['Terminal'].setCheckState(2)
        else:
            self.checkBoxes['Terminal'].setCheckState(0)

        override = config.get('override_build_cmd', 'buildozer {target} build')
        self.uiObjects['Build'].setText(str(override))

        override = config.get('override_clean_cmd', 'buildozer {target} clean')
        self.uiObjects['Clean'].setText(str(override))

        override = config.get('override_deploy_cmd', 'buildozer {target} deploy')
        self.uiObjects['Deploy'].setText(str(override))

        override = config.get('override_distclean_cmd', 'buildozer distclean')
        self.uiObjects['Distclean'].setText(str(override))

        override = config.get('override_run_cmd', 'buildozer {target} run')
        self.uiObjects['Run'].setText(str(override))

        override = config.get('override_serve_cmd', 'buildozer {target} serve')
        self.uiObjects['Serve'].setText(str(override))

        override = config.get('override_terminal_cmd', 'xterm -hold -e')
        self.uiObjects['Terminal'].setText(str(override))

    def updateBuildozerSpec(self):
        config = self.config
        use_custom_spec = config.get('use_custom_spec', False)
        if use_custom_spec:
            self.checkBoxes['CustomSpec'].setCheckState(2)
        else:
            self.checkBoxes['CustomSpec'].setCheckState(0)

        self.uiObjects['CustomSpec'].clear()
        spec = config.get('custom_spec', '')
        self.uiObjects['CustomSpec'].insertPlainText(str(spec))

    def updateCustomTargets(self):
        config = self.config
        targets = config.get('custom_target', '')
        self.uiObjects['CustomTarget'].insertPlainText(targets)

    def setDefaultConfig(self, config):
        self.configDefaults.update(config)

    def setConfig(self, config):
        self.config.update(config)
        self.updateGeneral()
        self.updateCommands()
        self.updateCustomTargets()
        self.updateSubstitute()
        self.updateBlacklist()
        self.updateBuildozerSpec()

    def getCheckboxBool(self, check):
        if self.checkBoxes[check].checkState():
            return True
        else:
            return False

    def value(self):
        config = {}
        config['ask_save_on_close'] = self.getCheckboxBool('AskSaveOnClose')
        config['show_splashscreen'] = self.getCheckboxBool('SplashScreen')
        config['keep_recent_files'] = self.getCheckboxBool('RecentFiles')
        for x in ['clean', 'build', 'distclean', 'run',
                  'deploy', 'serve', 'terminal']:
            config['override_{}_cmd'.format(x.lower())] = self.uiObjects[x.title()].text()
            config['override_{}'.format(x.lower())] = self.getCheckboxBool(x.title())

        config['custom_target'] = self.uiObjects['CustomTarget'].toPlainText()

        config['app_blacklist'] = self.uiObjects['BlacklistApp'].toPlainText()
        config['use_app_blacklist'] = self.getCheckboxBool('BlacklistApp')

        config['buildozer_blacklist'] = self.uiObjects['BlacklistBuildozer'].toPlainText()
        config['use_buildozer_blacklist'] = self.getCheckboxBool('BlacklistBuildozer')

        config['app_substitute'] = self.uiObjects['SubApp'].toPlainText()
        config['use_app_substitute'] = self.getCheckboxBool('SubApp')

        config['buildozer_substitute'] = self.uiObjects['SubBuildozer'].toPlainText()
        config['use_buildozer_substitute'] = self.getCheckboxBool('SubBuildozer')

        config['custom_spec'] = self.uiObjects['CustomSpec'].toPlainText()
        config['use_custom_spec'] = self.getCheckboxBool('CustomSpec')
        config['custom_spec'] = self.uiObjects['CustomSpec'].toPlainText()
        config['use_custom_spec'] = self.getCheckboxBool('CustomSpec')
        return config
