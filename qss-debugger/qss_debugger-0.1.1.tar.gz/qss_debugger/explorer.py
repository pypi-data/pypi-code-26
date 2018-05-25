# *********************************************************************
# +++ IMPORTS
# *********************************************************************
import os
import subprocess
import hashlib

from PySide import QtGui, QtCore


# *********************************************************************
# +++ CLASS
# *********************************************************************
class VisualTreeExplorer(QtGui.QDialog):
    # =====================================================================
    # +++ SIGNALS
    # =====================================================================
    selection_changed = QtCore.Signal(list)
    update_style_requested = QtCore.Signal()
    closing = QtCore.Signal()

    # =====================================================================
    # +++ CONSTRUCTOR
    # =====================================================================
    def __init__(self, parent=None):
        super(VisualTreeExplorer, self).__init__(parent)
        self._validation_controls = {'folder_exists': [], 'file_exists': []}

        self._init_ui()
        self._validate()

    # ====================================================================
    # +++ PRIVATE METHODS
    # =====================================================================
    def _init_ui(self):
        # -- Visual Tree Tab
        self._debug_tree = QtGui.QTreeWidget()
        self._debug_tree.setUniformRowHeights(True)
        self._debug_tree.setColumnCount(2)
        self._debug_tree.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self._debug_tree.itemSelectionChanged.connect(self._selection_changed)

        # -- Settings Tab
        watch_css_folder_path_label = QtGui.QLabel('Segmented Css Folder Path:')
        self._watch_css_folder_path_widget = QtGui.QLineEdit()
        self._watch_css_folder_path_widget.textChanged.connect(self._validate)
        self._validation_controls['folder_exists'].append(self._watch_css_folder_path_widget)

        watch_vars_folder_path_label = QtGui.QLabel('Segmented Vars Folder Path:')
        self._watch_vars_folder_path_widget = QtGui.QLineEdit()
        self._watch_vars_folder_path_widget.textChanged.connect(self._validate)
        self._validation_controls['folder_exists'].append(self._watch_vars_folder_path_widget)

        compiled_file_path_label = QtGui.QLabel('Output Css File Path:')
        self._compiled_file_path_widget = QtGui.QLineEdit()
        self._compiled_file_path_widget.textChanged.connect(self._validate)
        self._validation_controls['file_exists'].append(self._compiled_file_path_widget)

        manual_update_widget = QtGui.QPushButton('Reload Css')
        manual_update_widget.pressed.connect(lambda: self.update_style_requested.emit())

        settings_layout = QtGui.QVBoxLayout()
        settings_layout.addWidget(watch_css_folder_path_label)
        settings_layout.addWidget(self._watch_css_folder_path_widget)
        settings_layout.addWidget(watch_vars_folder_path_label)
        settings_layout.addWidget(self._watch_vars_folder_path_widget)
        settings_layout.addWidget(compiled_file_path_label)
        settings_layout.addWidget(self._compiled_file_path_widget)

        settings_layout.addWidget(manual_update_widget)
        settings_layout.addStretch(1)

        settings_wrapper_widget = QtGui.QWidget()
        settings_wrapper_widget.setLayout(settings_layout)

        # -- Tab widget
        tab_widget = QtGui.QTabWidget()
        tab_widget.addTab(self._debug_tree, 'Visual Tree')
        tab_widget.addTab(settings_wrapper_widget, 'Settings')

        # -- Log
        self._log_widget = QtGui.QTextEdit()

        # -- Splitter
        splitter = QtGui.QSplitter()
        splitter.setOrientation(QtCore.Qt.Vertical)
        splitter.addWidget(tab_widget)
        splitter.addWidget(self._log_widget)

        root_layout = QtGui.QVBoxLayout()
        root_layout.addWidget(splitter)
        self.setLayout(root_layout)

    def _validate(self):
        valid_style = 'border: 1px solid black;'
        invalid_style = 'border: 2px solid red;'

        for validation_type, control_list in self._validation_controls.iteritems():
            for control in control_list:
                control.setStyleSheet(valid_style)
                control.setProperty('valid', True)

                if (validation_type == 'file_exists' and not os.path.isfile(control.text())) or \
                   (validation_type == 'folder_exists' and not os.path.isdir(control.text())):
                    control.setStyleSheet(invalid_style)
                    control.setProperty('valid', False)

    # ====================================================================
    # +++ GET/SET
    # =====================================================================
    @property
    def watch_css_folder_path(self):
        return self._watch_css_folder_path_widget.text()

    @watch_css_folder_path.setter
    def watch_css_folder_path(self, value):
        self._watch_css_folder_path_widget.setText(value)

    @property
    def watch_vars_folder_path(self):
        return self._watch_vars_folder_path_widget.text()

    @watch_vars_folder_path.setter
    def watch_vars_folder_path(self, value):
        self._watch_vars_folder_path_widget.setText(value)

    @property
    def compiled_file_path(self):
        return self._compiled_file_path_widget.text()

    @compiled_file_path.setter
    def compiled_file_path(self, value):
        self._compiled_file_path_widget.setText(value)

    @property
    def is_settings_valid(self):
        self._validate()
        invalid_controls = [control
                            for controls in self._validation_controls.values()
                            for control in controls
                            if control.property('valid') is False]

        return not len(invalid_controls)

    # ====================================================================
    # +++ PUBLIC METHODS
    # =====================================================================
    def log_message(self, message):
        current_text = self._log_widget.toPlainText()
        current_text += '\n{}'.format(message)
        self._log_widget.setText(current_text)
        print 'text set'

    def update_tree(self, visual_root, tree_root=None):

        if not tree_root:
            self._debug_tree.clear()
            tree_root = QtGui.QTreeWidgetItem(self._debug_tree, ['*', '*'])

        for visual_child in visual_root.children():
            visual_child_hash = hashlib.md5(str(visual_child)).hexdigest()
            tree_child = QtGui.QTreeWidgetItem(tree_root, [str(type(visual_child)), visual_child_hash])
            tree_child.setData(2, QtCore.Qt.ItemDataRole, visual_child)

            if visual_child.children():
                self.update_tree(visual_child, tree_child)

    def set_selected_item(self, visual_item):
        visual_child_hash = hashlib.md5(str(visual_item)).hexdigest()
        tree_item = self._debug_tree.findItems(visual_child_hash, QtCore.Qt.MatchRecursive, 1)

        if tree_item:
            self._debug_tree.setCurrentItem(tree_item[0], 0, QtGui.QItemSelectionModel.ClearAndSelect)
            self._debug_tree.resizeColumnToContents(0)
            self._debug_tree.resizeColumnToContents(1)

    # ====================================================================
    # +++ OVERRIDES
    # =====================================================================
    def closeEvent(self, event):
        self.closing.emit()

    # ====================================================================
    # +++ CALLBACKS
    # =====================================================================
    def _selection_changed(self):
        visual_items = [o.data(2, QtCore.Qt.ItemDataRole) for o in self._debug_tree.selectedItems()
                        if o.data(2, QtCore.Qt.ItemDataRole)]

        self.selection_changed.emit(visual_items)
