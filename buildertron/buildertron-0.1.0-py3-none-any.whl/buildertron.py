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


import json
import logging
import os
from os.path import basename, expanduser, exists, dirname, join, realpath
import sys

from ast import literal_eval as make_tuple
from configparser import SafeConfigParser
from functools import partial
from sys import platform
from subprocess import PIPE, call, check_output
from PyQt5.QtCore import (Qt, QTimer, QSize)
from PyQt5.QtGui import (QIcon, QPixmap, QColor)
from PyQt5.QtWidgets import (QApplication, QMainWindow, QSplashScreen, QAction, QLabel,
                             QComboBox, QFileDialog, QMessageBox, QColorDialog)


appPath = ''
if __name__ != '__main__':
    # this allows us to import relatively
    sys.path.append(dirname(realpath(__file__)))
    appPath = dirname(realpath(__file__)) + '/'


from dialogs import (aboutdialog, settingsdialog, submitissuedialog, androidpermissionsdialog)
from forms.uimainwindow import Ui_MainWindow
from spec import translate_objects
from spec.buildozerdefault import get_default_template
from spec.android_presplash_colors import get_android_presplash_colors
from version import __version__


if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)


if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


SYS_ARGS = {
    '--verbose': 0,
}
# verbosity
LOG_LEVELS = {
    '1': 20,  # Info
    '2': 10,  # Debug
    '3': 30,  # Warning
    '4': 40,  # Error
    '5': 50,  # Critical
}

SPLASH_TIMEOUT = 400
ANDROID_PRESPLASH_COLORS = get_android_presplash_colors()


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self._specfile = None
        self._config = {}
        self._config.update(self.appDefaults)

        self.checkBoxes = {}
        self.specObjects = {}
        self.envPaths = {}

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle('BuilderTron v{0}'.format(__version__))
        self.setWindowIcon(QIcon(appPath + 'buildertron.ico'))

        self.createToolbar()
        self.collectUiObjects()
        self.loadDefaultSpec()
        self.appLoadConfig()
        self.updateUI()
        if self.config.get('show_splashscreen', True):
            self.initSplash()
        self.show()

        self.refreshPreview()
        self.loadRecentFile()

    @property
    def appDefaults(self):
        return {
            'ask_save_on_close': True,
            'show_splashscreen': True,
            'keep_recent_files': True,
            'recent_files': [],
            'override_build': False,
            'override_build_cmd': 'buildozer {target} {buildmode}',
            'override_clean': False,
            'override_clean_cmd': 'buildozer {target} clean',
            'override_deploy': False,
            'override_deploy_cmd': 'buildozer {target} deploy',
            'override_distclean': False,
            'override_distclean_cmd': 'buildozer distclean',
            'override_run': False,
            'override_run_cmd': 'buildozer {target} run',
            'override_serve': False,
            'override_serve_cmd': 'buildozer {target} serve',
            'override_terminal': False,
            'override_terminal_cmd': 'xterm -hold -e',
            'custom_target': '',
            'use_app_blacklist': False,
            'app_blacklist': '',
            'use_buildozer_blacklist': False,
            'buildozer_blacklist': '',
            'use_app_substitute': False,
            'app_substitute': '',
            'use_buildozer_substitute': False,
            'buildozer_substitute': '',
            'use_custom_spec': False,
            'custom_spec': get_default_template(),
        }

    def appLoadConfig(self):
        logging.info('MainWindow->appLoadConfig')
        try:
            with open(self.settingsPath, 'r') as file:
                data = json.load(file)
                file.close()
                self.config.update(data)
        except Exception:
            self.appSaveConfig()
        self.appRestoreStore()

    def appRestoreStore(self):
        logging.info('MainWindow->appRestoreStore')
        self.updateRecentFilesMenu()

    def appSaveConfig(self):
        logging.info('MainWindow->appSaveConfig')
        try:
            with open(self.settingsPath, 'w') as file:
                json.dump(self.config, file, sort_keys=True, indent=2)
        except PermissionError:
            logging.info('PermissionError: you do not permission to save config')
        logging.info(self.config)

    @property
    def buildmode(self):
        buildmode = self.comboBuild.currentText()
        return buildmode

    @property
    def buildozerSpecDefault(self):
        return join(appPath, 'spec', 'buildozer-default.spec')

    @property
    def cmdBuild(self):
        default = self.appDefaults['override_build_cmd']
        if self.config.get('override_build', False):
            return self.config.get('override_build_cmd', default)
        return default

    @property
    def cmdClean(self):
        default = self.appDefaults['override_clean_cmd']
        if self.config.get('override_distclean', False):
            return self.config.get('override_clean_cmd', default)
        return default

    @property
    def cmdDeploy(self):
        default = self.appDefaults['override_deploy_cmd']
        if self.config.get('override_deploy', False):
            return self.config.get('override_deploy_cmd', default)
        return default

    @property
    def cmdDistclean(self):
        default = self.appDefaults['override_distclean_cmd']
        if self.config.get('override_distclean', False):
            return self.config.get('override_distclean_cmd', default)
        return default

    @property
    def cmdRun(self):
        default = self.appDefaults['override_run_cmd']
        if self.config.get('override_run', False):
            return self.config.get('override_run_cmd', default)
        return default

    @property
    def cmdServe(self):
        default = self.appDefaults['override_serve_cmd']
        if self.config.get('override_serve', False):
            return self.config.get('override_serve_cmd', default)
        return default

    @property
    def config(self):
        return self._config

    @property
    def settingsPath(self):
        if platform == 'linux':
            home = expanduser('~')
            base = '{0}/.local/share/buildertron/'.format(home)
            os.system('mkdir -p {0}'.format(base))
            path = join(base, 'settings.json')
        else:
            path = 'settings.json'
        return path

    @property
    def specfileDir(self):
        return dirname(self._specfile)

    @property
    def logcat(self):
        return self.comboLogcat.currentText()

    @property
    def targetname(self):
        return self.comboTarget.currentText()

    def checkCommandOutput(self, cmd):
        out = ''
        try:
            out = check_output(cmd).decode('utf8')
        except Exception:
            pass
        return out

    def clearRecentFiles(self):
        self.config['recent_files'] = []
        self.updateRecentFilesMenu()
        self.appSaveConfig()

    def closeEvent(self, event):
        try:
            self.splash.close()
        except Exception:
            pass

        if not self.config.get('ask_save_on_close', True):
            event.accept()
            return

        confirm = QMessageBox(self)
        confirm.setWindowTitle('Save changes?')
        confirm.setText('Save changes before closing')
        confirm.setStandardButtons(QMessageBox.No | QMessageBox.Cancel | QMessageBox.Save)
        ret = confirm.exec()
        if ret == QMessageBox.Save:
            save = self.onSave()
            if save is False:
                event.ignore()
                return
        elif ret == QMessageBox.Cancel:
            event.ignore()
            return

        self.appSaveConfig()
        event.accept()

    def closeFile(self):
        logging.info('MainWindow->closeFile')

    def collectUiObjects(self):
        logging.debug(self.ui.__dict__.keys())
        for n, obj in self.ui.__dict__.items():
            if n.startswith('checkbox_'):
                self.checkBoxes[n[9:]] = obj
            elif n.startswith('lineedit_'):
                self.specObjects[n[9:]] = obj
            elif n.startswith('lineedit2_'):
                self.specObjects[n[10:]] = obj
            elif n.startswith('checkbox2_'):
                self.specObjects[n[10:]] = obj
            elif n.startswith('combobox_'):
                self.specObjects[n[9:]] = obj
            elif n.startswith('spinbox_'):
                self.specObjects[n[8:]] = obj
            elif n.startswith('colorpick_'):
                obj.clicked.connect(self.openPresplashPicker)
            elif n.startswith('permissions_'):
                obj.clicked.connect(self.openAndroidPermissions)
            elif n.startswith('toolbutton_'):
                obj.clicked.connect(partial(self.onToolButton, name=n[11:]))

    def createToolbar(self):
        self.toolbar = self.addToolBar('Toolbar')
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolbar.setIconSize(QSize(32, 32))
        self.toolbar.setMovable(False)

        act = QAction(QIcon(self.iconPath('new.png')), 'New', self)
        self.toolbar.addAction(act)
        act.triggered.connect(self.onNew)

        act = QAction(QIcon(self.iconPath('open.png')), 'Open', self)
        self.toolbar.addAction(act)
        act.triggered.connect(self.onLoad)

        act = QAction(QIcon(self.iconPath('save.png')), 'Save', self)
        self.toolbar.addAction(act)
        act.triggered.connect(self.onSave)

        act = QAction(QIcon(self.iconPath('saveas.png')), 'Save As...', self)
        self.toolbar.addAction(act)
        act.triggered.connect(self.onSaveAs)

        self.toolbar.addSeparator()

        act = QAction(QIcon(self.iconPath('distclean.png')), 'Dist Clean', self)
        self.toolbar.addAction(act)
        act.triggered.connect(partial(self.onCmd, act))
        act.setToolTip('buildozer distclean')

        act = QAction(QIcon(self.iconPath('clean.png')), 'Clean', self)
        self.toolbar.addAction(act)
        act.triggered.connect(partial(self.onCmd, act))
        act.hovered.connect(partial(self.onToolbarHover, act))

        label = QLabel(self)
        label.setText(' Build: ')
        self.toolbar.addWidget(label)
        self.comboBuild = QComboBox(self)
        self.toolbar.addWidget(self.comboBuild)
        self.comboBuild.addItems(['debug', 'release'])

        act = QAction(QIcon(self.iconPath('build.png')), 'Build', self)
        self.toolbar.addAction(act)
        act.triggered.connect(partial(self.onCmd, act))
        act.hovered.connect(partial(self.onToolbarHover, act))
        self.toolbar.addSeparator()

        act = QAction(QIcon(self.iconPath('deploy.png')), 'Deploy', self)
        self.toolbar.addAction(act)
        act.triggered.connect(partial(self.onCmd, act))
        act.hovered.connect(partial(self.onToolbarHover, act))

        act = QAction(QIcon(self.iconPath('run.png')), 'Run', self)
        self.toolbar.addAction(act)
        act.triggered.connect(partial(self.onCmd, act))
        act.hovered.connect(partial(self.onToolbarHover, act))

        act = QAction(QIcon(self.iconPath('serve.png')), 'Serve', self)
        self.toolbar.addAction(act)
        act.triggered.connect(partial(self.onCmd, act))
        act.hovered.connect(partial(self.onToolbarHover, act))

        label = QLabel(self)
        label.setText(' Target: ')
        self.toolbar.addWidget(label)
        self.comboTarget = QComboBox(self)
        self.toolbar.addWidget(self.comboTarget)

        label = QLabel(self)
        label.setText(' Logcat: ')
        self.toolbar.addWidget(label)
        self.comboLogcat = QComboBox(self)
        self.toolbar.addWidget(self.comboLogcat)
        self.comboLogcat.addItems(['off', 'on'])

        label = QLabel(self)
        label.setText(' Log Level: ')
        self.toolbar.addWidget(label)
        self.comboLogLevel = QComboBox(self)
        self.toolbar.addWidget(self.comboLogLevel)
        self.comboLogLevel.addItems(['2', '1', '0'])
        self.specObjects['log_level'] = self.comboLogLevel

    def getObjectValue(self, object):
        # checkBox?
        value = None
        try:
            value = object.checkState()
            if value == 0:
                value = False
            else:
                value = True
            return value
        except Exception:
            pass
        # lineEdit?
        try:
            value = object.text()
            return value
        except Exception:
            pass
        # comboBox?
        try:
            value = object.currentText()
            return value
        except Exception:
            pass
        # spinBox?
        try:
            value = object.value()
            return value
        except Exception:
            pass

        return value

    def getSpec(self):
        """Returns specification"""
        spec = {}
        for k, v in self.specObjects.items():
            if not v.isEnabled():
                spec[k] = None
                continue
            spec[k] = self.getObjectValue(v)
        return spec

    def getSpecOutput(self):
        # TODO - needs refactoring
        target = self.getObjectValue(self.comboTarget)
        logcat = self.getObjectValue(self.comboLogcat)
        build = self.getObjectValue(self.comboBuild)

        app_blacklist = None
        use_app_blacklist = self.config.get('use_app_blacklist')
        if use_app_blacklist:
            app_blacklist = self.config.get('app_blacklist')
            app_blacklist = app_blacklist.replace('\n', '')
            app_blacklist = app_blacklist.split(',')

        buildozer_blacklist = None
        use_buildozer_blacklist = self.config.get('use_buildozer_blacklist')
        if use_buildozer_blacklist:
            buildozer_blacklist = self.config.get('buildozer_blacklist')
            buildozer_blacklist = buildozer_blacklist.replace('\n', '')
            buildozer_blacklist = buildozer_blacklist.split(',')

        app_substitute = {}
        appsub = {}
        use_app_substitute = self.config.get('use_app_substitute')
        if use_app_substitute:
            appsub = self.config.get('app_substitute')
            appsub = appsub.replace('\n', '')
            appsub = appsub.split(',')
            appsub = [k for k in appsub if '=' in k]

            for k in appsub:
                try:
                    key, sub = k.split('=')
                    app_substitute[key] = sub
                except Exception:
                    continue

        buildozer_substitute = {}
        buildozersub = {}
        use_buildozer_substitute = self.config.get('use_buildozer_substitute')
        if use_buildozer_substitute:
            buildozersub = self.config.get('buildozer_substitute')
            buildozersub = buildozersub.replace('\n', '')
            buildozersub = buildozersub.split(',')
            buildozersub = [k for k in buildozersub if '=' in k]
            for k in buildozersub:
                try:
                    key, sub = k.split('=')
                    buildozer_substitute[key] = sub
                except Exception:
                    continue

        spec = self.getSpec()
        trans = translate_objects.translate
        app_text = ''
        buildozer_text = ''
        if self.config.get('use_custom_spec', False):
            custom_spec = self.config.get('custom_spec')
        else:
            custom_spec = self.appDefaults['custom_spec']

        custom_spec += '[{0}]\n'.format('buildertron')
        custom_spec += '{0} = {1}\n'.format('targetname', target)
        custom_spec += '{0} = {1}\n'.format('logcat', logcat)
        custom_spec += '{0} = {1}\n'.format('build', build)
        if app_substitute:
            custom_spec += 'app_substitute = {0}\n'.format(list(app_substitute.items()))
        if buildozer_substitute:
            custom_spec += 'buildozer_substitute = {0}\n'.format(list(buildozer_substitute.items()))

        for k, v in trans['app'].items():
            if v not in spec:
                continue
            value = spec[v]
            if value is None:
                continue
            if app_blacklist and k in app_blacklist:
                continue
            j = None
            if app_substitute:
                j = app_substitute.get(k, None)
            if j:
                k = j
            app_text += ('{0} = {1}\n'.format(k, str(value)))

        for k, v in trans['buildozer'].items():
            if v not in spec:
                continue
            value = spec[v]
            if value is None:
                continue
            if buildozer_blacklist and k in buildozer_blacklist:
                continue
            if buildozer_substitute:
                j = buildozer_substitute.get(k, None)
            j = None
            if j:
                k = j
            buildozer_text += ('{0} = {1}\n'.format(k, str(value)))

        result = custom_spec.format(app=app_text, buildozer=buildozer_text)
        return result

    def loadDefaultSpec(self):
        logging.info('MainWindow->loadDefaultSpec')
        self.loadSpec('spec/buildozer-default.spec')
        for chk in self.checkBoxes.values():
            chk.setCheckState(0)

    def loadRecentFile(self):
        recent_files = self.config.get('recent_files', [])
        try:
            file = recent_files[0]
            if exists(file):
                self.loadSpec(file)
                self._specfile = file
                self.updateTitle()
        except Exception as e:
            logging.info('Failed to open recent file. {0}'.format(e))
        self.refreshPreview()

    def loadSpec(self, specfile):
        """Loads buildozer spec
        """
        logging.info('MainWindow->loadSpec')
        logging.info(specfile)
        specfile = realpath(specfile)
        if not exists(specfile):
            return

        config = SafeConfigParser()
        trans = translate_objects.translate
        config.read([specfile])
        config_dict = {}
        for s in config.sections():
            config_dict[s] = {}
            for k, v in config.items(s):
                try:
                    config_dict[s][k] = v
                except Exception as e:
                    continue

        app_substitute = {}
        buildozer_substitute = {}
        buildertron_conf = {}
        try:
            buildertron_conf = config_dict['buildertron']
        except Exception as e:
            logging.info(e)

        if buildertron_conf:
            target = buildertron_conf.get('targetname', None)
            if target:
                index = self.comboTarget.findText(target)
                self.comboTarget.setCurrentIndex(index)

            logcat = buildertron_conf.get('logcat', None)
            if logcat:
                index = self.comboLogcat.findText(logcat)
                self.comboLogcat.setCurrentIndex(index)

            build = buildertron_conf.get('build', None)
            if build:
                index = self.comboBuild.findText(str(build))
                self.comboBuild.setCurrentIndex(index)

            # unsubstitute values
            app_substitute = buildertron_conf.get('app_substitute', {})
            try:
                app_substitute = {v: k for k, v in make_tuple(str((app_substitute)))}
            except Exception as e:
                app_substitute = {}
                logging.info(e)

            try:
                buildozer_substitute = {v: k for k, v in make_tuple(str(buildozer_substitute))}
            except Exception as e:
                buildozer_substitute = {}
                logging.info(e)

        for section in config_dict:
            if section == 'buildertron':
                continue
            for key, value in config_dict[section].items():
                if section == 'app':
                    key = app_substitute.get(key, key)
                elif section == 'buildozer':
                    key = buildozer_substitute.get(key, key)

                t = trans[section].get(key)
                obj = self.specObjects.get(t)
                if not obj:
                    continue
                try:
                    self.setObjectValue(obj, value)
                except Exception as e:
                    logging.info(e)

                # also try to check box if it exists
                try:
                    self.checkBoxes[t].setCheckState(2)
                except Exception as e:
                    logging.info(e)

        return specfile

    def iconPath(self, icon):
        return join(appPath, 'icons', icon)

    def initSplash(self):
        self.splash = QSplashScreen(QPixmap(appPath + "splash.png"), Qt.WindowStaysOnTopHint)
        self.splash.show()
        QTimer.singleShot(SPLASH_TIMEOUT, lambda: self.splash.close())

    def onButton(self):
        print(1)

    def onCmd(self, act):
        label = act.text()
        if not self._specfile and label != 'Dist Clean':
            return
        if label == 'Dist Clean':
            label = 'Distclean'
        elif not self._specfile:
            return

        try:
            cmd = getattr(self, 'cmd' + label)
        except Exception as e:
            return
        logcat = self.logcat
        buildmode = self.buildmode
        targetname = self.targetname
        if logcat == 'on' and label not in ['Distclean', 'Clean']:
            logcat = ' logcat'
        else:
            logcat = ''
        cmd = '{c}{logcat}'.format(c=cmd.format(target=targetname, buildmode=buildmode), logcat=logcat)

        if label == 'Distclean':
            self.runCmd(cmd=cmd)
            return
        self.runCmd(cwd=self.specfileDir, cmd=cmd)

    def onLoad(self, **kwargs):
        logging.info('MainWindow->onLoad')
        ask_save = kwargs.get('ask_save', True)

        if ask_save:
            confirm = QMessageBox(self)
            confirm.setWindowTitle("Save changes?")
            confirm.setText("Save changes before loading another file?")
            confirm.setStandardButtons(QMessageBox.No | QMessageBox.Cancel | QMessageBox.Save)
            ret = confirm.exec()
            if ret == QMessageBox.Save:
                self.onSave()
            elif ret == QMessageBox.Cancel:
                return

        dlg = QFileDialog(self)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.ExistingFiles
        while True:
            specfile, _ = dlg.getOpenFileName(self, 'Load buildozer.spec', 'buildozer.spec', options=options)
            if not specfile:
                return
            if not basename(specfile) == 'buildozer.spec':
                continue
            break

        if not basename(specfile) == 'buildozer.spec':
            return

        self.loadSpec(specfile)
        self._specfile = specfile
        self.updateTitle()
        self.updateRecentFiles()

    def onMenubar(self, action):
        logging.info('MainWindow->Menubar->{}'.format(action.text()))
        text = action.text()
        if text == 'About...':
            self.openAbout()
        elif text == 'Build':
            self.onCmd(text)
        elif text == 'Clean':
            self.onCmd(text)
        elif text == 'Clear Recent Files':
            self.clearRecentFiles()
        elif text == 'Dist Clean':
            self.onCmd(text)
        elif text == 'Deploy':
            self.onCmd(text)
        elif text == 'Serve':
            self.onCmd(text)
        elif text == 'Exit':
            self.close()
        elif text == 'Load':
            self.onLoad()
        elif text == 'New':
            self.onNew()
        elif text == 'Settings':
            self.openSettings()
        elif text == 'Save':
            self.onSave()
        elif text == 'Save As...':
            self.onSaveAs()
        elif text == 'Submit Issue':
            self.openSubmitIssue()

    def onNew(self):
        logging.info('MainWindow->onNew')
        confirm = QMessageBox(self)
        confirm.setWindowTitle("Save changes?")
        confirm.setText("Save changes before creating new file?")
        confirm.setStandardButtons(QMessageBox.No | QMessageBox.Cancel | QMessageBox.Save)
        ret = confirm.exec()
        if ret == QMessageBox.Save:
            self.onSave()
        elif ret == QMessageBox.Cancel:
            return

        self.loadDefaultSpec()
        self._specfile = None
        self.updateTitle()

    def onRecentFile(self, file):
        logging.info('MainWindow->onRecentFile')
        confirm = QMessageBox(self)
        confirm.setWindowTitle('Load Recent File?')
        confirm.setText('Current changes will be lost. Continue?')
        confirm.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes)
        ret = confirm.exec()
        if ret != QMessageBox.Yes:
            return
        self.loadDefaultSpec()
        self._specfile = None
        file = self.loadSpec(file)
        if file:
            self._specfile = file
        self.updateTitle()

    def onSave(self, **kwargs):
        logging.info('MainWindow->onSave')
        msg = kwargs.get('msg', 'Save buildozer.spec')
        if not self._specfile:
            dlg = QFileDialog(self)
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            while True:
                specfile, _ = dlg.getSaveFileName(self, msg, 'buildozer.spec', options=options)
                if not specfile:
                    return False
                if not basename(specfile) == 'buildozer.spec':
                    continue
                break
            self._specfile = specfile

        specfile = self._specfile
        result = self.getSpecOutput()
        with open(specfile, 'w') as file:
            file.write(result)

        self.updateRecentFiles()
        self.appSaveConfig()
        self.updateTitle()

    def onSaveAs(self):
        dlg = QFileDialog(self)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        while True:
            specfile, _ = dlg.getSaveFileName(self, 'Save to buildozer.spec', 'buildozer.spec', options=options)
            if not specfile:
                return
            if not basename(specfile) == 'buildozer.spec':
                continue
            break
        self._specfile = specfile
        self.onSave()

    def onToolbarHover(self, act):
        label = act.text()
        try:
            cmd = getattr(self, 'cmd' + label)
        except Exception as e:
            return
        logcat = self.logcat
        buildmode = self.buildmode
        targetname = self.targetname
        if logcat == 'on' and label not in ['Dist Clean', 'Clean']:
            logcat = ' logcat'
        else:
            logcat = ''
        cmd = '{c}{logcat}'.format(c=cmd.format(target=targetname, buildmode=buildmode), logcat=logcat)
        act.setToolTip('cmd: {0}'.format(cmd))

    def onToolButton(self, name):
        logging.info('MainWindow->onToolButton->{0}'.format(name))
        object = self.specObjects[name]
        dlg = QFileDialog(self)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.DirectoryOnly
        folder = dlg.getExistingDirectory(self, 'Choose directory', '.', options=options)
        if not folder:
            return
        object.setText(folder)

    def openAbout(self):
        aboutdialog.AboutDialog(self)

    def openAndroidPermissions(self):
        perm = self.specObjects['android_permissions']
        ret = androidpermissionsdialog.AndroidPermissionsDialog(self)
        ret.setValue(perm.text())
        ret.accepted.connect(lambda: perm.setText(ret.value))
        ret.open()

    def openPresplashPicker(self):
        object = self.specObjects['android_presplash_color']
        dlg = QColorDialog(self)
        c = QColor(object.currentText())
        dlg.setCurrentColor(c)
        color = dlg.getColor()
        if not color.isValid():
            return
        object.setEditText(color.name())

    def openSettings(self):
        dlg = settingsdialog.SettingsDialog(self)
        dlg.setDefaultConfig(self.appDefaults)
        dlg.setConfig(self.config)
        dlg.accepted.connect(lambda: self.updateConfig(dlg.value()))
        dlg.exec()

    def openSubmitIssue(self):
        submitissuedialog.SubmitIssueDialog(self)

    def refreshPreview(self):
        logging.info('Refreshing preview text')
        preview = self.ui.previewText
        preview.clear()
        result = self.getSpecOutput()
        preview.insertPlainText(result)

    def refreshSystemDetails(self):
        logging.info('refreshSystemDetails')
        textEdit = self.ui.textEditSystem
        textEdit.clear()
        textEdit.insertPlainText('cmd: buildozer version\n')
        out = self.checkCommandOutput('buildozer version')
        out = out.replace('# Check configuration tokens', '')
        if out:
            textEdit.insertPlainText('{0}\n'.format(out))
        else:
            textEdit.insertPlainText('No output. Is buildozer installed?\n'.format(out))

        textEdit.insertPlainText('Pip checking dependency versions.\n')
        textEdit.insertPlainText('Note: This check may be using incorrect pip to check dependencies.')
        textEdit.insertPlainText('Future releases should improve this method.\n\n')

        out = self.checkCommandOutput('pip --version')
        textEdit.insertPlainText('{0}'.format(out))
        for d in ['cython', 'jinja2', 'pexpect', 'virtualenv']:
            cmd = 'pip show {0}'.format(d)
            textEdit.insertPlainText('cmd: {0}\n'.format(cmd))
            out = self.checkCommandOutput('{0}'.format(cmd))
            textEdit.insertPlainText('{0}\n'.format(out))
            if not out:
                textEdit.insertPlainText('No output. Is {} installed?\n\n'.format(d))

    def runCmd(self, cwd='.', cmd=''):
        logging.info('runCmd')
        print('runCmd')
        override_terminal = self.config.get('override_terminal', self.appDefaults['override_terminal'])
        override_terminal_cmd = self.config.get('override_terminal_cmd', self.appDefaults['override_terminal_cmd'])
        if override_terminal:
            override_terminal_cmd = self.config.get('override_terminal', self.appDefaults['override_terminal'])

        if platform == 'win32':
            return
        elif platform == 'linux':
            c = '{term} "'.format(term=override_terminal_cmd)
            c += 'cd {cwd} '.format(cwd=cwd)
            c += '&& {cmd}"'.format(cmd=cmd)
        logging.info(c)
        call(c, stdin=PIPE, shell=True)

    def setObjectValue(self, object, value):
        # checkBox?
        try:
            v = value
            if v == 'True':
                v = 2
            else:
                v = 0
            object.setCheckState(v)
            return
        except Exception:
            pass
        # lineEdit?
        try:
            object.setText(value)
            return
        except Exception:
            pass
        # comboBox?
        try:
            index = object.findText(str(value))
            object.setCurrentIndex(index)
            return
        except Exception:
            pass
        # spinBox?
        try:
            object.setValue(int(value))
            return
        except Exception:
            pass

    def updateConfig(self, config):
        self.config.update(config)
        if self.config['keep_recent_files'] is False:
            self.config['recent_files'] = []
            self.updateRecentFilesMenu()
        self.appSaveConfig()

        self.updateTargetNamesMenu()

    def updateRecentFiles(self):
        logging.info('MainWindow->updateRecentFiles')
        keep_recent_files = self.config.get('keep_recent_files', True)
        if keep_recent_files is False:
            self.config['recent_files'] = []
        else:
            recent_files = self.config.get('recent_files', [])
            if self._specfile in recent_files:
                idx = recent_files.index(self._specfile)
                del recent_files[idx]
            new = set()
            for f in recent_files:
                new.add(f)
            new = list(new)
            new.insert(0, self._specfile)
            self.config['recent_files'] = new[:10]
        self.updateRecentFilesMenu()
        self.appSaveConfig()

    def updateRecentFilesMenu(self):
        recent_files = self.config.get('recent_files', [])
        self.ui.menuRecentFiles.clear()
        for file in recent_files:
            act = QAction(self)
            act.setText(file)
            self.ui.menuRecentFiles.addAction(act)
            act.triggered.connect(partial(self.onRecentFile, file))

        self.ui.menuRecentFiles.addSeparator()
        act = QAction(self)
        act.setText('Clear Recent Files')
        self.ui.menuRecentFiles.addAction(act)
        if not recent_files:
            act.setEnabled(False)

    def updateTargetNamesMenu(self):
        custom_targets = self.config.get('custom_target', [])
        custom_targets = custom_targets.replace('\n', '')
        self.comboTarget.clear()
        self.comboTarget.addItems(['android', 'android_new', 'android_old', 'ios', 'osx'])
        self.comboTarget.addItems(custom_targets.split(','))

    def updateTitle(self):
        logging.info('MainWindow->updateTitle')
        title = 'BuilderTron v{0}'.format(__version__)
        if self._specfile:
            title += ' - {0}'.format(self._specfile)
        self.setWindowTitle(title)

    def updateUI(self):
        self.specObjects['android_presplash_color'].addItems(sorted(ANDROID_PRESPLASH_COLORS))
        self.updateTargetNamesMenu()


def check_root():
    """
    If effective user id is 0, display a warning and require
    user input to continue (or to cancel)
    """
    try:
        euid = os.geteuid() == 0
    except AttributeError:
        if sys.platform == 'win32':
            import ctypes
        euid = ctypes.windll.shell32.IsUserAnAdmin() != 0
    if euid:
        print('Running as root! Quitting')
        sys.exit()


def process_sys_args():
    res = {}
    for arg in sys.argv[1:]:
        if "=" not in arg:
            continue
        key, value = arg.split("=")[:2]
        res[key.lower()] = value.lower()
    return res


def set_logging_level():
    # Logging Configuration
    try:
        v = LOG_LEVELS[SYS_ARGS["--verbose"]]
        logging.basicConfig(level=v)
    except KeyError:
        pass


# logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.INFO)
def main():
    check_root()
    SYS_ARGS.update(process_sys_args())
    set_logging_level()
    app = QApplication(sys.argv)
    MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
