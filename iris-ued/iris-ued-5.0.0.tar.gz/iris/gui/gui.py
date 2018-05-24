# -*- coding: utf-8 -*-
"""
Main GUI for iris
"""

import sys
from os.path import dirname, join
from pathlib import Path
from shutil import copy2

import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets

from skued import diffread

# Get all proper subclasses of AbstractRawDataset
# to build a loading menu
from .. import AbstractRawDataset, __version__
from ..plugins import PLUGIN_DIR
from .angular_average_dialog import AngularAverageDialog
from .calibrate_q_dialog import QCalibratorDialog
from .control_bar import ControlBar
from .controller import ErrorAware, IrisController
from .data_viewer import ProcessedDataViewer
from .metadata_edit_dialog import MetadataEditDialog
from .powder_viewer import PowderViewer
from .processing_dialog import ProcessingDialog
from .qbusyindicator import QBusyIndicator
from .symmetrize_dialog import SymmetrizeDialog

image_folder = join(dirname(__file__), 'images')

class Iris(QtWidgets.QMainWindow, metaclass = ErrorAware):
    
    dataset_path_signal             = QtCore.pyqtSignal(str)
    raw_dataset_path_signal         = QtCore.pyqtSignal(str, object)    # path and class
    single_picture_path_signal      = QtCore.pyqtSignal(str)
    error_message_signal            = QtCore.pyqtSignal(str)
    restart_signal                  = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.peak_dynamics_window = None

        self._controller_thread = QtCore.QThread(parent = self)
        self.controller = IrisController() # No parent so that we can moveToThread
        self.controller.moveToThread(self._controller_thread)
        self._controller_thread.start()

        self.dataset_path_signal.connect(self.controller.load_dataset)
        self.raw_dataset_path_signal.connect(self.controller.load_raw_dataset)

        self.controls = ControlBar(parent = self)
        self.controls.raw_data_request.connect(self.controller.display_raw_data)
        self.controls.averaged_data_request.connect(self.controller.display_averaged_data)
        self.controls.baseline_computation_parameters.connect(self.controller.compute_baseline)
        self.controls.baseline_removed.connect(self.controller.powder_background_subtracted)
        self.controls.relative_powder.connect(self.controller.enable_powder_relative)
        self.controls.relative_averaged.connect(self.controller.enable_averaged_relative)
        self.controls.notes_updated.connect(self.controller.set_dataset_notes)
        self.controls.time_zero_shift.connect(self.controller.set_time_zero_shift)
        self.controls.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.MinimumExpanding)

        self.controller.raw_dataset_loaded_signal.connect(lambda b: self.viewer_stack.setCurrentWidget(self.raw_data_viewer))
        self.controller.raw_dataset_loaded_signal.connect(self.controls.raw_dataset_controls.setVisible)

        self.controller.processed_dataset_loaded_signal.connect(lambda b: self.viewer_stack.setCurrentWidget(self.processed_viewer))
        self.controller.processed_dataset_loaded_signal.connect(self.controls.diffraction_dataset_controls.setVisible)
        self.controller.processed_dataset_loaded_signal.connect(self.controls.stack.setVisible)

        self.controller.powder_dataset_loaded_signal.connect(lambda b: self.viewer_stack.setCurrentWidget(self.powder_viewer))
        self.controller.powder_dataset_loaded_signal.connect(self.controls.powder_diffraction_dataset_controls.setVisible)
        
        self.controller.raw_dataset_metadata.connect(self.controls.update_raw_dataset_metadata)
        self.controller.dataset_metadata.connect(self.controls.update_dataset_metadata)

        # Progress bar --------------------------------------------------------
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum)

        self.controller.processing_progress_signal.connect(self.progress_bar.setValue)
        self.controller.powder_promotion_progress.connect(self.progress_bar.setValue)
        self.controller.angular_average_progress.connect(self.progress_bar.setValue)

        # Status bar ----------------------------------------------------------
        # Operation in progress widget
        # Including custom 'busy' indicator
        status_bar = QtWidgets.QStatusBar(parent = self)
        self.controller.status_message_signal.connect(lambda msg : status_bar.showMessage(msg, 10e3))
        self.setStatusBar(status_bar)

        # Progress bar added to status bar ------------------------------------
        status_bar.addPermanentWidget(self.progress_bar)

        # Version label -------------------------------------------------------
        version_label = QtWidgets.QLabel('  Version ' + __version__ + '  ')
        status_bar.addWidget(version_label, 2)

        # Busy indicator ------------------------------------------------------
        busy_indicator = QBusyIndicator(parent = self)
        self.controller.operation_in_progress.connect(busy_indicator.toggle_animation)
        status_bar.addPermanentWidget(busy_indicator, 2)

        # Viewers -------------------------------------------------------------
        self.raw_data_viewer = pg.ImageView(parent = self, name = 'Raw data')
        self.raw_data_viewer.resize(self.raw_data_viewer.maximumSize())
        self.controller.raw_data_signal.connect(lambda obj: self.raw_data_viewer.clear() if obj is None else self.raw_data_viewer.setImage(obj))

        self.processed_viewer = ProcessedDataViewer(parent = self)
        self.processed_viewer.peak_dynamics_roi_signal.connect(self.controller.time_series)
        self.controller.averaged_data_signal.connect(self.processed_viewer.display)
        self.controller.time_series_signal.connect(self.processed_viewer.display_peak_dynamics)
        self.controls.enable_peak_dynamics.connect(self.processed_viewer.toggle_peak_dynamics)

        self.powder_viewer = PowderViewer(parent = self)
        self.powder_viewer.peak_dynamics_roi_signal.connect(self.controller.powder_time_series)
        self.controller.powder_data_signal.connect(self.powder_viewer.display_powder_data)
        self.controller.powder_time_series_signal.connect(self.powder_viewer.display_peak_dynamics)
        # UI components
        self.controller.error_message_signal.connect(self.show_error_message)
        self.error_message_signal.connect(self.show_error_message)

        self.file_dialog = QtWidgets.QFileDialog(parent = self)      
        self.menu_bar = self.menuBar()

        self.viewer_stack = QtWidgets.QTabWidget()
        self.viewer_stack.addTab(self.raw_data_viewer, 'View raw dataset')
        self.viewer_stack.addTab(self.processed_viewer, 'View processed dataset')
        self.viewer_stack.addTab(self.powder_viewer, 'View azimuthal averages')

        self.controller.raw_dataset_loaded_signal.connect(lambda toggle: self.viewer_stack.setTabEnabled(0, toggle))
        self.controller.processed_dataset_loaded_signal.connect(lambda toggle: self.viewer_stack.setTabEnabled(1, toggle))
        self.controller.powder_dataset_loaded_signal.connect(lambda toggle: self.viewer_stack.setTabEnabled(2, toggle))

        ###################
        # Actions

        self.file_menu = self.menu_bar.addMenu('&File')
        self.file_menu.setToolTipsVisible(True)
        load_raw_submenu = self.file_menu.addMenu('Load raw dataset...')

        # Dynamically add an option for each implementation of AbstractRawDataset
        # Note : because of dynamical nature of these bindings,
        # it must be done in a separate method
        for cls in AbstractRawDataset.implementations:
            self._create_load_raw(cls, load_raw_submenu)

        self.load_dataset_action = QtWidgets.QAction(QtGui.QIcon(join(image_folder, 'locator.png')), '& Load dataset', self)
        self.load_dataset_action.triggered.connect(self.load_dataset)

        self.load_single_picture_action = QtWidgets.QAction(QtGui.QIcon(join(image_folder, 'locator.png')), '& Load diffraction picture', self)
        self.load_single_picture_action.triggered.connect(self.load_single_picture)

        self.close_raw_dataset_action = QtWidgets.QAction(QtGui.QIcon(join(image_folder, 'locator.png')), '& Close raw dataset', self)
        self.close_raw_dataset_action.triggered.connect(self.controller.close_raw_dataset)
        self.close_raw_dataset_action.setEnabled(False)
        self.controller.raw_dataset_loaded_signal.connect(self.close_raw_dataset_action.setEnabled)

        self.load_plugin_action = QtWidgets.QAction(QtGui.QIcon(join(image_folder, 'eye.png')), '& Load plug-in (restarts program)', self)
        self.load_plugin_action.setToolTip('Copy a plug-in file into the internal storage. The application will restart and the new plug-in will be available.')
        self.load_plugin_action.triggered.connect(self.load_plugin)
        self.controller.operation_in_progress.connect(self.load_plugin_action.setDisabled)  # wouldn't want to restart during processing

        self.close_dataset_action = QtWidgets.QAction(QtGui.QIcon(join(image_folder, 'locator.png')), '& Close dataset', self)
        self.close_dataset_action.triggered.connect(self.controller.close_dataset)
        self.close_dataset_action.setEnabled(False)
        self.controller.powder_dataset_loaded_signal.connect(self.close_dataset_action.setEnabled)
        self.controller.processed_dataset_loaded_signal.connect(self.close_dataset_action.setEnabled)

        self.file_menu.addAction(self.load_dataset_action)
        self.file_menu.addAction(self.load_single_picture_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.close_raw_dataset_action)
        self.file_menu.addAction(self.close_dataset_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.load_plugin_action)

        ###################
        # Operations on Diffraction Datasets
        self.processing_action = QtWidgets.QAction(QtGui.QIcon(join(image_folder, 'analysis.png')), '& Process raw data', self)
        self.processing_action.triggered.connect(self.launch_processsing_dialog)
        self.controller.raw_dataset_loaded_signal.connect(self.processing_action.setEnabled)

        self.symmetrize_action = QtWidgets.QAction(QtGui.QIcon(join(image_folder, 'analysis.png')), '& Symmetrize data (beta)', self)
        self.symmetrize_action.triggered.connect(self.launch_symmetrize_dialog)
        self.controller.processed_dataset_loaded_signal.connect(self.symmetrize_action.setEnabled)

        self.promote_to_powder_action = QtWidgets.QAction(QtGui.QIcon(join(image_folder, 'analysis.png')), '& Calculate angular average', self)
        self.promote_to_powder_action.triggered.connect(self.launch_promote_to_powder_dialog)
        self.controller.processed_dataset_loaded_signal.connect(self.promote_to_powder_action.setEnabled)

        self.update_metadata_action = QtWidgets.QAction(QtGui.QIcon(join(image_folder, 'save.png')), '& Update dataset metadata', self)
        self.update_metadata_action.triggered.connect(self.launch_metadata_edit_dialog)
        self.controller.processed_dataset_loaded_signal.connect(self.update_metadata_action.setEnabled)
        self.controller.powder_dataset_loaded_signal.connect(self.update_metadata_action.setEnabled)

        self.recompute_angular_averages = QtWidgets.QAction(QtGui.QIcon(join(image_folder, 'analysis.png')), '& Recompute angular average', self)
        self.recompute_angular_averages.triggered.connect(self.launch_recompute_angular_average_dialog)
        self.controller.powder_dataset_loaded_signal.connect(self.recompute_angular_averages.setEnabled)

        self.calibrate_scattvector_action = QtWidgets.QAction(QtGui.QIcon(join(image_folder, 'analysis.png')), '& Calibrate scattering vector', self)
        self.calibrate_scattvector_action.triggered.connect(self.launch_calq_dialog)
        self.controller.powder_dataset_loaded_signal.connect(self.calibrate_scattvector_action.setEnabled)

        self.diffraction_dataset_menu = self.menu_bar.addMenu('&Dataset')
        self.diffraction_dataset_menu.addAction(self.processing_action)
        self.diffraction_dataset_menu.addAction(self.symmetrize_action)
        self.diffraction_dataset_menu.addSeparator()
        self.diffraction_dataset_menu.addAction(self.promote_to_powder_action)
        self.diffraction_dataset_menu.addAction(self.update_metadata_action)
        self.diffraction_dataset_menu.addSeparator()
        self.diffraction_dataset_menu.addAction(self.recompute_angular_averages)
        self.diffraction_dataset_menu.addAction(self.calibrate_scattvector_action)

        ###################
        # Helps and misc operations

        self.launch_documentation_action = QtWidgets.QAction(QtGui.QIcon(join(image_folder, 'revert.png')), '& Open online documentation', self)
        self.launch_documentation_action.triggered.connect(self.launch_documentation)

        self.goto_repository_action = QtWidgets.QAction(QtGui.QIcon(join(image_folder, 'revert.png')), '& Go to GitHub Repository', self)
        self.goto_repository_action.triggered.connect(self.goto_repository)

        self.report_issue_action = QtWidgets.QAction(QtGui.QIcon(join(image_folder, 'revert.png')), '& Report issue', self)
        self.report_issue_action.triggered.connect(self.report_issue)

        self.help_menu = self.menu_bar.addMenu('&Help')
        self.help_menu.addAction(self.launch_documentation_action)
        self.help_menu.addSeparator()
        self.help_menu.addAction(self.goto_repository_action)
        self.help_menu.addAction(self.report_issue_action)

        ###################
        # Layout
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addWidget(self.viewer_stack)
        self.layout.addWidget(self.controls)

        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)
        
        # Initialization
        self.controller.raw_dataset_loaded_signal.emit(False)
        self.controller.powder_dataset_loaded_signal.emit(False)
        self.controller.processed_dataset_loaded_signal.emit(False)
        self.controller.processing_progress_signal.emit(0)
        self.controller.powder_promotion_progress.emit(0)
        self.controller.angular_average_progress.emit(0)
        
        self.viewer_stack.setCurrentWidget(self.raw_data_viewer)
        self.viewer_stack.resize(self.viewer_stack.maximumSize())

        #Window settings ------------------------------------------------------
        # Set un-maximizzed geometry to be 75% of availiable screen space
        available = QtWidgets.QApplication.desktop().availableGeometry()
        available.setSize(0.75*available.size())
        self.setGeometry(available)

        self.setWindowIcon(QtGui.QIcon(join(image_folder, 'eye.png')))
        self.setWindowTitle('Iris - UED data exploration')
        self.center_window()
        self.showMaximized()
    
    def _create_load_raw(self, cls, submenu):
        # Note : because of dynamical nature of these bindings,
        # it must be done in a separate method
        return submenu.addAction(QtGui.QIcon(join(image_folder, 'locator.png')),
                                 '&Load {}'.format(cls.__name__),
                                 lambda : self.load_raw_dataset(cls))
        
    def closeEvent(self, event):
        self._controller_thread.quit()
        super().closeEvent(event)
    
    @QtCore.pyqtSlot(str)
    def show_error_message(self, msg):
        self.error_dialog = QtWidgets.QErrorMessage(parent = self)
        self.error_dialog.showMessage(msg)
    
    @QtCore.pyqtSlot()
    def launch_processsing_dialog(self):
        processing_dialog = ProcessingDialog(parent = self, raw = self.controller.raw_dataset)
        processing_dialog.resize(0.75*self.size())
        processing_dialog.processing_parameters_signal.connect(self.controller.process_raw_dataset)
        processing_dialog.exec_()
        processing_dialog.processing_parameters_signal.disconnect(self.controller.process_raw_dataset)

    @QtCore.pyqtSlot()
    def launch_symmetrize_dialog(self):
        symmetrize_dialog = SymmetrizeDialog(parent = self, 
                                             image = self.controller.dataset.diff_data(timedelay = self.controller.dataset.time_points[0]))
        symmetrize_dialog.resize(0.75*self.size())
        symmetrize_dialog.symmetrize_parameters_signal.connect(self.controller.symmetrize)
        symmetrize_dialog.exec_()
        symmetrize_dialog.symmetrize_parameters_signal.disconnect(self.controller.symmetrize)
    
    @QtCore.pyqtSlot()
    def launch_metadata_edit_dialog(self):
        metadata_dialog = MetadataEditDialog(parent = self, config = self.controller.dataset.metadata)
        metadata_dialog.updated_metadata_signal.connect(self.controller.update_metadata)
        metadata_dialog.exec_()
        metadata_dialog.updated_metadata_signal.disconnect(self.controller.update_metadata)

    @QtCore.pyqtSlot()
    def launch_promote_to_powder_dialog(self):
        image = self.controller.dataset.diff_data(self.controller.dataset.time_points[0])
        promote_dialog = AngularAverageDialog(image, parent = self)
        promote_dialog.resize(0.75*self.size())
        promote_dialog.angular_average_signal.connect(self.controller.promote_to_powder)
        promote_dialog.exec_()
        promote_dialog.angular_average_signal.disconnect(self.controller.promote_to_powder)
    
    @QtCore.pyqtSlot()
    def launch_recompute_angular_average_dialog(self):
        image = self.controller.dataset.diff_data(self.controller.dataset.time_points[0])
        dialog = AngularAverageDialog(image, parent = self)
        dialog.resize(0.75*self.size())
        dialog.angular_average_signal.connect(self.controller.recompute_angular_average)
        dialog.exec_()
        dialog.angular_average_signal.disconnect(self.controller.recompute_angular_average)
    
    @QtCore.pyqtSlot()
    def launch_calq_dialog(self):
        I = self.controller.dataset.powder_eq(bgr = True)
        dialog = QCalibratorDialog(I, parent = self)
        dialog.resize(0.75*self.size())
        dialog.calibration_parameters.connect(self.controller.powder_calq)
        dialog.exec_()
        dialog.calibration_parameters.disconnect(self.controller.powder_calq)
    
    @QtCore.pyqtSlot(object)
    def load_raw_dataset(self, cls):
        path = self.file_dialog.getExistingDirectory(parent = self, caption = 'Load raw dataset')
        if not path:
            return
        self.raw_dataset_path_signal.emit(path, cls)

    @QtCore.pyqtSlot()
    def load_dataset(self):
        path = self.file_dialog.getOpenFileName(parent = self, caption = 'Load dataset', filter = '*.hdf5')[0]
        if not path:
            return
        self.dataset_path_signal.emit(path)
    
    @QtCore.pyqtSlot()
    def load_single_picture(self):
        path = self.file_dialog.getOpenFileName(parent = self, caption = 'Load diffraction picture', filter = 'Images (*.tif *.tiff *.mib)')[0]
        if not path:
            return

        viewer = SinglePictureViewer(path)
        viewer.resize(0.75*self.size())
        return viewer.exec_()
    
    @QtCore.pyqtSlot()
    def center_window(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    @QtCore.pyqtSlot()
    def load_plugin(self):
        """ Load plug-in and restart application. """
        path = self.file_dialog.getOpenFileName(parent = self, caption = 'Load plug-in file', filter = 'Python source (*.py)')[0]
        if not path:
            return
        
        path = Path(path)
        
        copy2(path, PLUGIN_DIR / path.name)

        self.controller.close_dataset()
        self.controller.close_raw_dataset()
        self.restart_signal.emit()
    
    @QtCore.pyqtSlot()
    def launch_documentation(self):
        """ Open online documentation in the default browser """
        return QtGui.QDesktopServices.openUrl(QtCore.QUrl("http://iris-ued.readthedocs.io/en/master/"))

    @QtCore.pyqtSlot()
    def report_issue(self):
        """ Open a new GitHub issue in the default browser """
        return QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://github.com/LaurentRDC/iris-ued/issues/new"))

    @QtCore.pyqtSlot()
    def goto_repository(self):
        """ Open a new GitHub issue in the default browser """
        return QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://github.com/LaurentRDC/iris-ued/"))


class SinglePictureViewer(QtWidgets.QDialog):
    """ Dialog for representing a single image. """

    def __init__(self, fname, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #scikit-ued's diffread ensures that 'color' images are reduced to 2-dimensional greyscale
        im = diffread(fname)

        self.image_viewer = pg.ImageView(parent = self)
        self.image_viewer.setImage(im)

        layout = QtWidgets.QVBoxLayout()
        fname_label = QtWidgets.QLabel('Filename: ' + fname, parent = self)
        fname_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(fname_label)
        layout.addWidget(self.image_viewer)
        self.setLayout(layout)
