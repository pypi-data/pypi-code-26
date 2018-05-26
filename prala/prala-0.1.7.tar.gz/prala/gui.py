import sys
from prala.common.common import getSetupIni
from prala.accessories import (_, Enum, PicButton, ConfigIni, removeControlChars,
    Property)
from prala.core import FilteredDictionary
from prala.core import Record
from prala.exceptions import EmptyDictionaryError
from prala.exceptions import NoDictionaryError

from PyQt5.QtWidgets import (QWidget, QGridLayout, QFrame, QMainWindow,
    QLabel, QPushButton, QLineEdit, QApplication, QHBoxLayout, QVBoxLayout,
    QTextEdit, QDesktopWidget, QSizePolicy, QAction, QToolButton, QMessageBox, 
    QFileDialog, QComboBox, QToolBar)   
from PyQt5.QtGui import QPainter, QFont, QColor, QIcon, QPixmap, QPalette, QTextCharFormat
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QSize, QEvent

import pyttsx3
import functools
from threading import Thread
from pkg_resources import resource_string, resource_filename
from time import sleep
from optparse import OptionParser
import re

class GuiPrala(QMainWindow):

    HEIGHT = 220
    WIDTH = 550

    BASIC_FONT = "Arial"
    BASIC_SIZE = 10
    BASIC_COLOR = Qt.black
    BASIC_BG = Qt.white
    BASIC_ITALIC = False
    BASIC_BOLD = False

    def __init__(self, file_name="", part_of_speech_filter="", extra_filter="", setup=None):

        super().__init__()

#        self.file_name = file_name
#        self.part_of_speech_filter = part_of_speech_filter
#        self.extra_filter = extra_filter

        #
        # --- Tool Bar --- 
        #
 
        # OPEN
        open_action = QAction(QIcon( resource_filename(__name__, "/".join(("images", "open-tool.png"))) ), _("MAIN.TOOLBAR.OPEN"), self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_dict_file)

        # START
        self.start_action = QAction(QIcon( resource_filename(__name__, "/".join(("images", "start-tool.png"))) ), _("MAIN.TOOLBAR.START"), self)
        self.start_action.setShortcut("Ctrl+S")
        self.start_action.triggered.connect( self.startClicked )

        # SAY OUT
        self.sayout_action = QAction(QIcon( resource_filename(__name__, "/".join(("images", "say-tool.png"))) ), _("MAIN.TOOLBAR.SAYOUT"), self)
        self.sayout_action.setShortcut("Ctrl+T")
        self.sayout_action.triggered.connect(self.sayOut)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # QUIT
        quit_action = QAction(QIcon( resource_filename(__name__, "/".join(("images", "quit-tool.png"))) ), _("MAIN.TOOLBAR.QUIT"), self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(QApplication.instance().quit)

        # ENABLE TO SAY
        enable_to_say_icon = QIcon()
        enable_to_say_icon.addPixmap(QPixmap( resource_filename(__name__, "/".join(("images", "enable-to-say-on-tool.png"))) ), QIcon.Normal, QIcon.On )
        enable_to_say_icon.addPixmap(QPixmap( resource_filename(__name__, "/".join(("images", "enable-to-say-off-tool.png"))) ), QIcon.Normal, QIcon.Off)
        self.enable_to_say_button = QToolButton()
        self.enable_to_say_button.setFocusPolicy(Qt.NoFocus)
        self.enable_to_say_button.setIcon(enable_to_say_icon)
        self.enable_to_say_button.setCheckable(True)
        self.enable_to_say_button.toggled.connect(self.changeEnableToSay)

        # ENABLE TO SHOW NOTE
        enable_to_show_note_icon = QIcon()
        enable_to_show_note_icon.addPixmap(QPixmap( resource_filename(__name__, "/".join(("images", "enable-to-show-note-on-tool.png"))) ), QIcon.Normal, QIcon.On )
        enable_to_show_note_icon.addPixmap(QPixmap( resource_filename(__name__, "/".join(("images", "enable-to-show-note-off-tool.png"))) ), QIcon.Normal, QIcon.Off)
        self.enable_to_show_note_button = QToolButton()
        self.enable_to_show_note_button.setFocusPolicy(Qt.NoFocus)
        self.enable_to_show_note_button.setIcon(enable_to_show_note_icon)
        self.enable_to_show_note_button.setCheckable(True)
        self.enable_to_show_note_button.toggled.connect(self.changeEnableToShowNote)        

        # ENABLE TO SHOW PATTERN
        enable_to_show_pattern_icon = QIcon()
        enable_to_show_pattern_icon.addPixmap(QPixmap( resource_filename(__name__, "/".join(("images", "enable-to-show-pattern-on-tool.png"))) ), QIcon.Normal, QIcon.On )
        enable_to_show_pattern_icon.addPixmap(QPixmap( resource_filename(__name__, "/".join(("images", "enable-to-show-pattern-off-tool.png"))) ), QIcon.Normal, QIcon.Off)
        self.enable_to_show_pattern_button = QToolButton()
        self.enable_to_show_pattern_button.setFocusPolicy(Qt.NoFocus)
        self.enable_to_show_pattern_button.setIcon(enable_to_show_pattern_icon)
        self.enable_to_show_pattern_button.setCheckable(True)
        self.enable_to_show_pattern_button.toggled.connect(self.changeEnableToShowPattern)        

        # BASE LANGUAGE DROPDOWN
        self.base_language_dropdown = QComboBox(self)
        self.base_language_dropdown.setFocusPolicy(Qt.NoFocus)
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        #flag = QIcon( resource_filename(__name__, "/".join(("images", "open-tool.png"))) )
        #[base_language_dropdown.addItem( flag, removeControlChars( i.languages[0].decode("utf-8") ) ) for i in voices]
        # Eliminates the languages having longer name as 2
        [self.base_language_dropdown.addItem(j) for j in [removeControlChars( i.languages[0].decode("utf-8")) for i in voices] if len(j) == 2]
        #[self.base_language_dropdown.addItem(  removeControlChars( i.languages[0].decode("utf-8") ) ) for i in voices]
        self.base_language_dropdown.activated[str].connect(self.changeBaseLanguage)

        # LEARNING LANGUAGE DROPDOWN
        self.learning_language_dropdown = QComboBox(self)
        self.learning_language_dropdown.setFocusPolicy(Qt.NoFocus)
        #[self.learning_language_dropdown.addItem(  removeControlChars( i.languages[0].decode("utf-8") ) ) for i in voices]
        # Eliminates the languages having longer name as 2
        [self.learning_language_dropdown.addItem(j) for j in [removeControlChars( i.languages[0].decode("utf-8")) for i in voices] if len(j) == 2]
        self.learning_language_dropdown.activated[str].connect(self.changeLearningLanguage)

        # POS FILTER DROPDOWN
        self.pos_filter_dropdown = QComboBox(self)
        self.pos_filter_dropdown.setFixedWidth(100)
        self.pos_filter_dropdown.setFocusPolicy(Qt.NoFocus)
        self.pos_filter_dropdown.activated[str].connect(self.changePOSFilter)

        # EXTRA FILTER DROPDOWN
        self.extra_filter_dropdown = QComboBox(self)
        self.extra_filter_dropdown.setFixedWidth(100)
        self.extra_filter_dropdown.setFocusPolicy(Qt.NoFocus)
        self.extra_filter_dropdown.activated[str].connect(self.changeExtraFilter)    

        #
        # Default settings
        #
        config_ini = ConfigIni.getInstance()
        self.sayout_action.setEnabled(False)
        self.start_action.setEnabled(False)
        self.createAskingCanvas( file_name, part_of_speech_filter, extra_filter, False )

        self.enable_to_say_button.setChecked(config_ini.isSayOut())
        self.enable_to_show_note_button.setChecked(config_ini.isShowNote())
        self.enable_to_show_pattern_button.setChecked(config_ini.isShowPattern())
        self.base_language_dropdown.setCurrentText( config_ini.getBaseLanguage())
        self.learning_language_dropdown.setCurrentText( config_ini.getLearningLanguage())

        # Selector Toolbar
        selectorToolbar = QToolBar("Selector toolbar") 
        self.addToolBar(Qt.LeftToolBarArea, selectorToolbar)
        selectorToolbar.setMovable(False)
        selectorToolbar.addWidget(self.pos_filter_dropdown)
        selectorToolbar.addWidget(self.extra_filter_dropdown)
        #selectorToolbar.addSeparator()
        #selectorToolbar.addWidget(self.base_language_dropdown)
        #selectorToolbar.addWidget(self.learning_language_dropdown)

        # Main Toolbar
        mainToolbar = self.addToolBar('Main toolbar' )
        mainToolbar.addAction(open_action)
        mainToolbar.addSeparator()
        mainToolbar.addAction(self.start_action)
        mainToolbar.addAction(self.sayout_action)
        mainToolbar.addSeparator()
        mainToolbar.addWidget(self.enable_to_say_button)
        mainToolbar.addWidget(self.enable_to_show_note_button)
        mainToolbar.addWidget(self.enable_to_show_pattern_button)
        mainToolbar.addWidget(self.base_language_dropdown)
        mainToolbar.addWidget(self.learning_language_dropdown)
        #mainToolbar.addWidget(self.pos_filter_dropdown)
        #mainToolbar.addWidget(self.extra_filter_dropdown)
        mainToolbar.addSeparator()
        mainToolbar.addWidget(spacer)
        mainToolbar.addAction(quit_action)
        
        #
        # --- Status Bar ---
        #
        #self.statusBar().showMessage("")

        #
        # --- Window ---
        #
        self.setWindowTitle( setup['title'] + " - " + setup['version'])
        self.resize(GuiPrala.WIDTH, GuiPrala.HEIGHT)
        #self.setFixedHeight(GuiPrala.HEIGHT)        
        #self.setFixedWidth(GuiPrala.WIDTH)
        self.center()
        self.show()

    def center(self):
        """Aligns the window to middle on the screen"""
        fg=self.frameGeometry()
        cp=QDesktopWidget().availableGeometry().center()
        fg.moveCenter(cp)
        self.move(fg.topLeft())

    def createAskingCanvas( self, file_name, pos_filter, extra_filter, enabledErrorMessage=True ):
        """
        The cases when this method is called:
        - In the constructor
        mainT Open a new dict file clicking on the Open toolbar
        - When the selected element in the filter dropdown changed
        """
        try:

            # try to open the file and create a selection by the filters
            self.asking_canvas = AskingCanvas( self.statusBar(), file_name, pos_filter, extra_filter )

            # if the file and the selectors was OK, then we can change them
            self.file_name = file_name
            self.part_of_speech_filter = pos_filter
            self.extra_filter = extra_filter

            # Hide CenterWidget
            self.setCentralWidget( None )  

            # Enable Start button
            self.start_action.setEnabled(True)        

            # Disable Say out
            self.sayout_action.setEnabled(False)

            # Clear the StatusBar
            self.statusBar().showMessage("")

            # Fill up the POS Filter selectors
            self.pos_filter_dropdown.clear()
            self.pos_filter_dropdown.addItems(self.asking_canvas.myFilteredDictionary.getPOSFilterList())
            self.pos_filter_dropdown.setCurrentText( self.part_of_speech_filter )

            # Fill up the EXTRA Filter selectors
            self.extra_filter_dropdown.clear()
            self.extra_filter_dropdown.addItems(self.asking_canvas.myFilteredDictionary.getExtraFilterList())
            self.extra_filter_dropdown.setCurrentText( self.extra_filter )

        except EmptyDictionaryError as e:
            if enabledErrorMessage:
                QMessageBox.critical(self, _("ERROR"), _("ERROR_MESSAGE.DICTIONARY_IS_EMPTY") + ":\n" + e.dict_file_name)
        except NoDictionaryError as f:
            if enabledErrorMessage:
                QMessageBox.critical(self, _("ERROR"), _("ERROR_MESSAGE.DICTIONARY_NOT_FOUND") + ":\n" + f.dict_file_name)

    def open_dict_file(self):
        """
        Opens the file selector dialog window for selecting a dict file.
        Called when the Open button is clicked
        """
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        fileName, sel = QFileDialog.getOpenFileName(
            self,
            _("FILE_SELECTOR.TITLE.SELECT_DICT"), 
            "",
            "Dictionary Files (*" + FilteredDictionary.DICT_EXT + ")", 
            options=options)

        if fileName:
            self.createAskingCanvas(fileName, "", "")            

    def startClicked(self):
        """
        -Asking WIdget shown in Central Widget
        -Start button disabled
        -Say out button enabled
        -Answer field in focus
        -Start the asking round
        """
        self.setCentralWidget( self.asking_canvas )
        self.start_action.setEnabled(False)
        self.sayout_action.setEnabled(True)
        self.asking_canvas.answer_field.setFirstFocus()
        self.asking_canvas.round()

    def sayOut(self):
        if self.asking_canvas.ok_button.status == OKButton.STATUS.ACCEPT:
            Thread(target = self.asking_canvas.record.say_out_base, args = ()).start()
        else:
            Thread(target = self.asking_canvas.record.say_out_learning, args = ()).start()

    def changeEnableToSay(self, checked):
        ConfigIni.getInstance().setSayOut( checked )
        #self.say_out = checked

    def changeEnableToShowNote(self, checked):
        ConfigIni.getInstance().setShowNote( checked )
        #self.show_note = checked
        if( not checked and hasattr(self, 'asking_canvas')):
            self.asking_canvas.note_field.setText("")

    def changeEnableToShowPattern(self, checked):
        ConfigIni.getInstance().setShowPattern( checked )
        if checked and hasattr(self, 'asking_canvas'):
            self.asking_canvas.answer_field.showPattern()
        elif hasattr(self, 'asking_canvas'):
            self.asking_canvas.answer_field.hidePattern()
        self.asking_canvas.answer_field.setFirstFocus()            
        #self.say_out = checked     

    def changeBaseLanguage( self, text ):
        ConfigIni.getInstance().setBaseLanguage(text)
        #if there is NO record yet
        if not self.start_action.isEnabled():
            self.asking_canvas.record.setBaseLanguage(text)
        self.asking_canvas.myFilteredDictionary.setBaseLanguage(text)

    def changeLearningLanguage( self, text ):
        ConfigIni.getInstance().setLearningLanguage(text)
        #if there is NO recor yet
        if not self.start_action.isEnabled():
            self.asking_canvas.record.setLearningLanguage(text)
        self.asking_canvas.myFilteredDictionary.setLearningLanguage(text)

    def changePOSFilter( self, filter ):
        self.part_of_speech_filter = filter
        self.createAskingCanvas(self.file_name, filter, self.extra_filter)

    def changeExtraFilter( self, filter ):
        self.extra_filter = filter
        self.createAskingCanvas(self.file_name, self.part_of_speech_filter, filter )

class AskingCanvas(QWidget):
    FIELD_DISTANCE = 3
    
    def __init__(self, status_bar, file_name, part_of_speech_filter, extra_filter):
        super().__init__()

        config_ini=ConfigIni.getInstance()
        self.status_bar = status_bar

        self.myFilteredDictionary=FilteredDictionary(
            file_name, 
            config_ini.getBaseLanguage(), 
            config_ini.getLearningLanguage(), 
            part_of_speech_filter,
            extra_filter
        ) 
       
        good_answer=[""]

        self.pos_field=TextLabel("", font="Courier New", size=10, color=Qt.gray)

        self.question_field=TextLabel("", font="Courier New", size=13, color=QColor(212, 140, 95))

        self.note_field=TextLabel("", font="Courier New", size=10, color=Qt.gray, bold=True, italic=True)

        self.answer_field=AnswerComplexField(good_answer, spacing=AskingCanvas.FIELD_DISTANCE, font="Courier new", size=15, color=Qt.blue, bg=self.palette().color(QPalette.Background))
        #self.answer_field.disableText()

        self.good_answer_field=ExpectedAnswerComplexField(good_answer, spacing=AskingCanvas.FIELD_DISTANCE, font="Courier new", size=15, color=Qt.black, bg=self.palette().color(QPalette.Background))

        self.result_lamp=ResultLamp(failed_position_list=None)

        self.ok_button = OKButton( self )

        # --------------------
        # general grid setting
        # --------------------
        #
        grid=QGridLayout()
        self.setLayout(grid)
        grid.setSpacing(1)      # space between the fields

        # --------------------
        # Fields location
        # --------------------

        fields_columns=4

        # PART OF SPEECH field
        grid.addWidget( self.pos_field, 0, 0, 1, fields_columns )

        # QUESTION field
        grid.addWidget( self.question_field, 1, 0, 1, fields_columns-1 )

        # NOTE field
        grid.addWidget( self.note_field, 1, fields_columns-1, 1, 1, Qt.AlignRight )

        # ANSWER field
        grid.addWidget( self.answer_field, 5, 0, 1, fields_columns-1)

        # EXPECTED ANSWER field
        grid.addWidget( self.good_answer_field, 6, 0, 1, fields_columns-1 )

        # OK buttn
        grid.addWidget( self.ok_button, 5, fields_columns-1, 1, 1, Qt.AlignRight )

        # RESULT lamp
        grid.addWidget( self.result_lamp, 6, fields_columns-1, 1, 1, Qt.AlignRight )

#        self.setGeometry(300, 300, 450, 150)
#        self.setWindowTitle(_("TITLE_WINDOW"))    
#        self.show()


    def showStat(self):
        overall=self.myFilteredDictionary.get_recent_stat_list()                    
                    
        good = str(overall[1])
        all = str(overall[0])
        remains = str(overall[2]) if overall[2] > 0 else ""
        success = str(int(100 * overall[1] / overall[0])) + "%" if overall[0] != 0 else ""
        recent_stat = self.record.get_recent_stat()
        sequence =  ", ".join( [str(i) for i in recent_stat])
        points = str(self.myFilteredDictionary.get_points(recent_stat))


        message = good + "/" + all + ("/" + remains if len(remains.strip()) > 0 else "") + " | " + success + " | " + points + " | " + sequence  
        self.status_bar.showMessage( message )
        
    def round( self, wrong_record=None ):
        """
            Frame of asking word.
            The other part of hte round is in the OKButton's on_click() method

            -calculates the the new word to ask
            -fill up the POS field
            -fill up the QUESTION field
            -fill up the ANSWER field
            -fill up the EXPECTED ANSWER field
            -say out the question
            -waiting for the user response

            Input
                wrong_record
                    - It is unrelevant until all words was answerd
                    - If it is EMPTY then the chance depends on the points
                    - If it is NOT EMPTY the the same question will be asked until it answered
            
        """
        
        # hides the result lamp
        self.result_lamp.set_result(None)

        self.record = self.myFilteredDictionary.get_next_random_record(wrong_record)
        good_answer = self.record.learning_words

        # pos field
        self.pos_field.setText(self.record.part_of_speach)

        # question
        self.question_field.setText( self.record.base_word )

        config_ini = ConfigIni.getInstance()

        # note field
        if config_ini.isShowNote():
            self.note_field.setText(self.record.note)

        # answer
        self.answer_field.setExpectedWordList( good_answer )
        self.answer_field.enableText()

        # expected answer
        self.good_answer_field.setExpectedWordList( good_answer )

        # say out the question in a thread
        if config_ini.isSayOut():
            Thread(target = self.record.say_out_base, args = ()).start()

        self.answer_field.setFirstFocus()

        # shows statistics
        self.showStat()


class OKButton(PicButton):
    STATUS = Enum(
        ACCEPT = 0,
        NEXT = 1
    )

    def __init__(self, asking_object):
        self.asking_object = asking_object

        ok_button_pixmap = QPixmap(resource_filename(__name__, "/".join(("images", "ok-button.png"))))        
        ok_button_hover_pixmap = QPixmap(resource_filename(__name__, "/".join(("images", "ok-button-hover.png"))))
        ok_button_focus_pixmap = QPixmap(resource_filename(__name__, "/".join(("images", "ok-button-focus.png"))))        
        ok_button_pressed_pixmap = QPixmap(resource_filename(__name__, "/".join(("images", "ok-button-pressed.png"))))   
        super().__init__(ok_button_pixmap, ok_button_focus_pixmap, ok_button_hover_pixmap, ok_button_pressed_pixmap)

        self.clicked.connect(self.on_click)
        self.status = OKButton.STATUS.ACCEPT

    def on_click(self):
                
        if self.status == OKButton.STATUS.ACCEPT:
        
            self.asking_object.answer_field.disableText()

            # shows the difference between the the answer and the good answer -> tuple
            # [0] -> False/True
            # [1] -> list of list of thedisable positions of the difference in the words
            self.result=self.asking_object.record.check_answer(self.asking_object.answer_field.getFieldsContentList())

            # write back the stat
            self.asking_object.myFilteredDictionary.add_result_to_stat(self.asking_object.record.word_id,self.result[0])

            # show the result in green/red lamp
            if self.result[0]:
                self.asking_object.result_lamp.set_result(True)
            else:
                self.asking_object.result_lamp.set_result(False)

            # shows the expected answer with differences
            self.asking_object.good_answer_field.showText(self.result[1], self.asking_object.answer_field.getFieldsContentList())

            # shows statistics
            self.asking_object.showStat()

            self.status = OKButton.STATUS.NEXT
            
            # say out the right answer in thread          
            if ConfigIni.getInstance().isSayOut():
                Thread(target = self.asking_object.record.say_out_learning, args = ()).start()

        elif self.status == OKButton.STATUS.NEXT:

            self.status  = OKButton.STATUS.ACCEPT

            # starts a new round
            self.asking_object.round( None if self.result[0] else self.asking_object.record )

            # shows statistics
            self.asking_object.showStat()

 

class TextLabel(QLabel):
    """
    This class represents a simple text label with specific caracteristics of font
    """

    def __init__(self, text, font=None, size=None, color=None, bold=None, italic=None):
        super().__init__()        

        if font is None:
            self.font = GuiPrala.BASIC_FONT
        else:
            self.font = font
        if size is None:
            self.size = GuiPrala.BASIC_SIZE
        else:
            self.size = size
        if color is None:
            self.color = GuiPrala.BASIC_COLOR
        else:
            self.color = color
        if bold is None:
            self.bold = GuiPrala.BASIC_BOLD
        else:
            self.bold = bold
        if italic is None:
            self.italic = GuiPrala.BASIC_ITALIC
        else:
            self.italic = italic
 
        # font type
        #self.setFont(QFont(self.font_name,pointSize=self.font_size, weight=QFont.Bold))
        font = QFont(self.font, pointSize=self.size)
        font.setBold( self.bold)
        font.setItalic( self.italic )
        self.setFont( font )
        
        # font color
        palette = QPalette()
        palette.setColor(self.foregroundRole(), self.color)
        self.setPalette( palette )

        self.setText(text)

    def setText(self, text):
        super().setText(text)


class ComplexFieldInterface(QWidget):
    SPACING = 1
 
    def __init__(self, secondary_word_list, spacing=None, font=None, size=None, color=None, bg=None, bold=None, italic=None):
        super().__init__()        
        
        #
        # DEFAULT parameters
        #
        if font is None:
            self.font = GuiPrala.BASIC_FONT
        else:
            self.font = font
        if size is None:
            self.size = GuiPrala.BASIC_SIZE
        else:
            self.size = size
        if color is None:
            self.color = GuiPrala.BASIC_COLOR
        else:
            self.color = color
        if bg is None:
            self.bg = GuiPrala.BASIC_BG
        else:
            self.bg = bg
        if bold is None:
            self.bold = GuiPrala.BASIC_BOLD
        else:
            self.bold = bold
        if italic is None:
            self.italic = GuiPrala.BASIC_ITALIC
        else:
            self.italic = italic
        if spacing is None:
            self.spacing = ComplexFieldInterface.SPACING
        else:
            self.spacing = spacing
        
        #
        # LAYOUT
        #
        layout = QHBoxLayout()
        layout.setSpacing( self.spacing )
        self.setLayout(layout)

        self.generateWidgetsForSecondaryWordList(secondary_word_list)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def generateWidgetsForSecondaryWordList(self, secondary_word_list):
        """
        Every time when it is called, a new layout will be generated
        """

        self.__secondary_word_list = secondary_word_list
    
        # remove all widgets
        self.__clear_layout(self.layout())
          
        for i in secondary_word_list:
            self.layout().addWidget( self.generateSingleField(i) )

        self.layout().addStretch(1)
 
    def generateSingleField(self, word):  raise NotImplementedError

    def getSingleFieldType(self): raise NotImplementedError #return SingleField

    def clearText(self):
        """
        Clear all fields of text
        """
        for widget in self.getFieldIterator():
            widget.clear()

    def disableText(self):
        """
        Disable all fields
        """
        for widget in self.getFieldIterator():
            widget.setEnabled( False )

    def enableText(self):
        """
        Clears and Enables all fields to edit
        """
        for widget in self.getFieldIterator():
            widget.clear()
            widget.setEnabled( True )

    def getFieldIterator(self):
        """
        Returns the SingleField widgets
        """
        for widget in self.children():
            if isinstance( widget, self.getSingleFieldType() ):
                yield widget

    def __clear_layout(self, layout):
        
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.__clear_layout(item.layout())

    def getSecondaryWordList(self):
        return self.__secondary_word_list
    
    def getContentOfFieldsList(self):
        """
        Returns the contents of the fields in a list
        """
        fields_content_list = []
        
        for widget in self.getFieldIterator():
            
            # adds the text from the field to the list
            fields_content_list.append( widget.toPlainText().strip() )

        return fields_content_list

    def setFirstFocus(self):
        self.layout().itemAt(0).widget().setFocus()
 
    
class AnswerComplexField(ComplexFieldInterface):
    """
    This class represents fields in one row with specific characteristics of font.
    The fields are for typing the answer for the question.
    The fields are enabled for typing when the app expecting the answer for the question.
    The fields are disabled for typing when the app showing the right answer for the question
    """ 
#    def __init__(self, expected_word_list, spacing=None, font=None, size=None, color=None, bg=None, bold=None, italic=None):
#        super().__init(expected_word_list, spacing=spacing, font=font, size=size, color=color, bg=bg, bold=bold, italic=italic)

    def generateSingleField(self, word):
        """
        Returns the empty SingleField of the specific part of the word
        with the right length, font size, basic_bg for inside use
        """
        return SingleFieldWithPattern(word, font=self.font, size=self.size, color=self.color, bg=self.bg)
 
    def getSingleFieldType(self):
        return SingleFieldWithPattern

    def showPattern(self):
        for widget in self.getFieldIterator():
            widget.showPattern()

    def hidePattern(self):
        for widget in self.getFieldIterator():
            widget.hidePattern()

    # TODO delete
    def setExpectedWordList(self, good_answer):
        self.generateWidgetsForSecondaryWordList(good_answer)

    def getFieldsContentList(self):
        return self.getContentOfFieldsList()




class ExpectedAnswerComplexField(ComplexFieldInterface):
    """
    This class represents the right answer fro the question.
    The vertical positions of the characters are synchronized with the characters in the answer's fields
    """
    WRONG_COLOR = Qt.red
    GOOD_COLOR = Qt.green

    def __init__(self, expected_word_list, spacing=None, font=None, size=None, color=None, bg=None, bold=None, italic=None):
        
        self.wrong_color = ExpectedAnswerComplexField.WRONG_COLOR
        self.good_color = ExpectedAnswerComplexField.GOOD_COLOR

        super().__init__(expected_word_list, spacing=spacing, font=font, size=size, color=color, bg=bg, bold=bold, italic=italic)

    def generateSingleField(self, word):
        """
        Returns the empty SingleField of the specific part of the word
        with the right length, font size, basic_bg for inside use
        """
        single_field = SingleField(word, font=self.font, size=self.size, color=self.color, bg=self.bg)
        single_field.setEnabled(False)
        return single_field

    def getSingleFieldType(self):
        return SingleField

    def setExpectedWordList(self, good_answer):
        self.generateWidgetsForSecondaryWordList(good_answer)

    def getFieldsContentList(self):
        return self.getContentOfFieldsList()

 
    def showText(self, failed_position_list, answer_list):      
        """
        Shows the expected answer, coloring the faild characters in position
        """

        good_answer_list = self.getSecondaryWordList()

        # go trough the answer and the failed_position_list pairs        
        #word_failed_position_pair_list = list(zip( completed_answer, failed_position_list ))
        word_failed_position_pair_list = list(zip( good_answer_list, failed_position_list ))

        self.clearText()

        i = 0
        for widget in self.getFieldIterator():

            # go trough all characters in the widget
            for pos in range(len(word_failed_position_pair_list[i][0])):

                if pos in word_failed_position_pair_list[i][1]:
                    widget.appendText(word_failed_position_pair_list[i][0][pos], color=self.wrong_color)
                          
                else:
                    widget.appendText(word_failed_position_pair_list[i][0][pos], color=self.good_color)
            i += 1


class SingleFieldWithPattern(QWidget):
    """
    This widget is a SingleField with template if it is enabled.
    Actually it is two SingleFields placed on each other.
    In the foregrand there is the 'pattern' which is disabled and shows special characters ".,!?"
    and underscores '_" in alphanumerical positions
    In the background there is the 'input' field which is enabled but opaque for being able 
    to see the 'pattern'
    """
    PATTERN_COLOR=Qt.blue
    PATTERN_BG=Qt.white
    def __init__(self, word, font=None, size=None, color=None, bg=None):
        super().__init__()

        self.word = word

        # This field is the patter - just right under the input field - disabled - not focusable
        self.patternField = SingleField(word, parent=self, font=font, size=size, color=type(self).PATTERN_COLOR, bg=type(self).PATTERN_BG)
        if ConfigIni.getInstance().isShowPattern():
            self.showPattern()
        self.patternField.setEnabled(False)
        self.patternField.move(0, 0)
        self.patternField.setFocusPolicy(Qt.NoFocus)    

        # Input field - Transparent - behind it the pattern is visible
        self.textField = SingleField(word, parent=self, font=font, size=size, color=color, bg=bg)
        self.textField.move(0, 0)
        self.textField.viewport().setAutoFillBackground(False)

        self.setMinimumSize(self.textField.minimumSize())

    def hidePattern(self):
        self.patternField.setText("")

    def showPattern(self):
        template=re.sub(r"[^, \!\?\.]", "_", self.word)
        self.patternField.setText(template)        

    def setFocus(self):
        self.textField.setFocus()

    def clear(self):
        self.textField.clear()

    def toPlainText(self):
        return self.textField.toPlainText()

class SingleField(QTextEdit):
    """
    This class represents a single field with specific characteristic of font.
    The max number of characters enabled to type determining the width of the field, defined by the 'length' parameter
    When this fields are part of the AnswerField class then it is possible to type characters in it by the user
    In this case the behavior of the field is the following:
        -Clicking Enter on the field causing the next widget (field/button) gets the focus
        -Reaching the max number of characters causing the next widget gets the focus
    """
 
    def __init__(self, word, parent=None, font=None, size=None, color=None, bg=None):
        super().__init__(parent)

        if font == None:
            self.basic_font=SingleField.BASIC_FONT
        else:
            self.basic_font=font
        if size == None:
            self.basic_size = SingleField.BASIC_SIZE
        else:
            self.basic_size = size
        if color == None:
            self.basic_color = SingleField.BASIC_COLOR
        else:
            self.basic_color = color
        if bg == None:
            self.basic_bg = SingleField.BASIC_BG
        else:
            self.basic_bg = bg

        self.word = word
        self.length = len(word)

        # No Border
        self.setFrameStyle(QFrame.NoFrame)
          
        # No ScrollBar
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # font, colors
        self.setFont(QFont(self.basic_font,pointSize=self.basic_size, weight=QFont.Bold))
        palette = self.viewport().palette()
        palette.setColor(self.viewport().backgroundRole(), self.basic_bg)
        self.viewport().setPalette(palette)
        self.setTextColor(self.basic_color)
  
        # Vertical size of the field (1 line)
        self.setFixedHeight(self.fontMetrics().height() + 3)

        # Horizontal size of the field
        self.setFixedWidth(self.fontMetrics().width("W" * self.length) + 10)

        # for control the number of the characters in the field
        self.textChanged.connect(self.changed_text)

    def appendText( self, text, color=None, bg=None ):
        if color == None:
            color = self.basic_color
        if bg == None:
            bg = self.basic_bg

        self.setTextColor(color)
        #self.setTextBackgroundColor(bg)
        self.insertPlainText(text)

    def keyPressEvent(self, event):
        key = event.key()
        if key in [ Qt.Key_Return, Qt.Key_Enter, Qt.Key_Tab ]:
            self.parent().focusNextChild()
        else:
            QTextEdit.keyPressEvent(self, event)
    
    def changed_text(self):
        self.setTextColor(self.basic_color)
        
        if len(self.toPlainText()) > self.length:
            self.setPlainText( self.toPlainText().strip()[0:self.length] )
        
            cursor = self.textCursor()
            cursor.setPosition(self.length)
            self.setTextCursor(cursor)

        elif len(self.toPlainText()) == self.length:
            self.parent().focusNextChild()

class ResultLamp(QLabel):
    """
    Shows the failed_position_list as a red/green light
    """
    WIDTH=42
    HEIGHT=42
    def __init__(self, failed_position_list=None):
        QLabel.__init__(self)

        self.setSizePolicy(QSizePolicy(
            QSizePolicy.Minimum,
            QSizePolicy.Minimum))

        self.set_result(failed_position_list)

    def set_result(self, failed_position_list):
        if failed_position_list is None:
            pixmap = QPixmap(resource_filename(__name__, "/".join(("images", "empty-light.png"))))        
        elif failed_position_list:
            pixmap = QPixmap(resource_filename(__name__, "/".join(("images", "green-light.png"))))        
        else:
            pixmap = QPixmap(resource_filename(__name__, "/".join(("images", "red-light.png"))))        

        pixmap = pixmap.scaled(type(self).WIDTH, type(self).HEIGHT, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.setPixmap(pixmap)

    def sizeHint(self): 
        return QSize(type(self).WIDTH, type(self).HEIGHT)


def main():    
    
    #
    # Handle parameters
    #
    setup = getSetupIni()

    parser=OptionParser("%prog [dict_file_name] [-p PART_OF_SPEECH_FILTER] [-f EXTRA_FILTER]", version="%prog " + setup['version'])
    parser.add_option("--pos", "-p", dest="part_of_speech_filter", default="", type="string", help="specify part of speech")
    parser.add_option("--filter", "-f", dest="extra_filter", default="", type="string", help="specify extra filter")
    (options, args) = parser.parse_args()

    if len(args) > 1:   
        parser.error("Incorrect number of arguments")
        exit()

    #
    # parameters for the app
    #
    if len(args) == 1:
        file_name = args[0]
    else:
        file_name = ""
    part_of_speech_filter = options.part_of_speech_filter
    extra_filter = options.extra_filter

    #
    # Configuration file
    #
    #config_ini = ConfigIni.getInstance()

    #
    # Application
    #
    app = QApplication(sys.argv)
    ex = GuiPrala(
        file_name=file_name, 
        part_of_speech_filter=part_of_speech_filter, 
        extra_filter=extra_filter, 
        setup=setup
        )
    sys.exit(app.exec_())
    
   
 
