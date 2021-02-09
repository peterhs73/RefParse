#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Main GUI for RefParse"""


import sys

from PySide2.QtWidgets import (
    QApplication,
    QLabel,
    QWidget,
    QPushButton,
    QRadioButton,
    QLineEdit,
    QTextEdit,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QSizePolicy,
    QShortcut,
    QButtonGroup,
)
from PySide2.QtGui import QKeySequence, QFont
from PySide2.QtCore import Slot, Signal, QThread, Qt

from refparse.api import RefAPI
import logging
from collections import defaultdict

root_logger = logging.getLogger()
gui_logger = logging.getLogger("GUI")


class ParserGUI(QWidget):
    def __init__(self, format_config):
        """The main GUI of the ref parser

        The class take output formats as an input
        """
        super().__init__()

        self.resize(800, 600)
        self.setWindowTitle("RefParse")
        self.init_layout(format_config)
        self.format_config = format_config
        self.api_object = None
        self.__threads = []

    def init_layout(self, format_config):
        """Initiate layouts

        For simplicity, the widget uses gridlayout with 2 columns
        """
        grid = QGridLayout()

        # - reference line
        self.ref_line = QLineEdit(self)
        grid.addWidget(QLabel("doi/arXiv:"), 0, 0)
        grid.addWidget(self.ref_line, 0, 1)

        # - search button
        self.search_btn = QPushButton("Search")
        self.search_btn.setShortcut("Return")
        self.search_btn.clicked.connect(self.access_reference)
        search = QHBoxLayout()
        search.addStretch(1)
        search.addWidget(self.search_btn)
        grid.addLayout(search, 1, 1)

        # - Output
        grid.addWidget(QLabel("Output:"), 2, 0)

        # - output format, set the first button to be true
        format_opt = QVBoxLayout()
        self.format_btns = QButtonGroup(self)
        self.format_btns.buttonClicked.connect(self.change_format)
        for format_type in format_config.keys():
            btn = QRadioButton(format_type, self)
            format_opt.addWidget(btn)
            self.format_btns.addButton(btn)
        # set first button checked
        self.format_btns.button(-2).setChecked(True)
        self.output_box = QTextEdit(self)

        grid.addLayout(format_opt, 3, 0, Qt.AlignTop)
        grid.addWidget(self.output_box, 3, 1)

        # - copy button
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.clicked.connect(self.copy)
        copy = QHBoxLayout()
        copy.addStretch(1)
        copy.addWidget(self.copy_btn)
        grid.addLayout(copy, 4, 1)

        # - log box (use custom logging handler that stream log to text box)
        self.log_box = QTextEdit(self)
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("background-color: transparent;")
        # set the log box to half of the size
        self.log_box.setMaximumHeight(self.log_box.sizeHint().height() / 2)

        # custom signal handler
        log_handler = QLogHandler(self)
        log_handler.setFormatter(
            logging.Formatter("[%(levelname)s] %(name)s - %(message)s")
        )
        root_logger.addHandler(log_handler)
        log_handler.signal.log_str.connect(self.log_box.append)

        grid.addWidget(QLabel("Log:"), 5, 0, Qt.AlignTop)
        grid.addWidget(self.log_box, 5, 1)

        # setup the overall layout for the widget
        self.setLayout(grid)

        # debug shortcuts
        self.debug = QShortcut(QKeySequence("Shift+F8"), self)
        self.debug.activated.connect(self.toggle_debug)

    def access_reference(self):
        """Create thread to run the api

        When the search button is pressed, the contents is reset
        and a new thread is created to run the api object
        """

        self.reset_content()
        reference = self.ref_line.text()

        if reference:
            gui_logger.info(f"Search reference: {reference}")
            ref_thread = RefThread(reference, self.format_config, parent=self)
            ref_thread.response_obj.connect(self.output)
            ref_thread.start()

        else:
            gui_logger.warning(f"Please enter doi or arXiv ID")

    @Slot(object)
    def output(self, api_object):
        """Link the api object to GUI class

        The slot for the signal from access_reference
        store the api object to the GUI
        """
        self.api_object = api_object
        self.change_format()

    def change_format(self):
        """Test the group of button if it is checked"""
        ref_format = self.format_btns.checkedButton().text()
        self.output_box.clear()
        if self.api_object.status:
            gui_logger.debug(f"{ref_format} format")
            format_thread = FormatThread(
                self.api_object, ref_format, parent=self
            )
            format_thread.response_str.connect(self.update_output)
            format_thread.start()

    @Slot(str)
    def update_output(self, output_str):
        """Update output from stored parsed api object

        This is done by first checking which format button is clicked
        """
        self.output_box.setText(output_str)

    def reset_content(self):
        """Clear and reset the contents"""
        self.output_box.clear()
        self.log_box.clear()

    def copy(self):
        """Copy the output text"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.output_box.toPlainText())
        gui_logger.info("text copied to clipboard")

    def toggle_debug(self):
        """Secret short cut shift + F8 to switch to debug mode"""

        if root_logger.isEnabledFor(logging.DEBUG):
            gui_logger.info("switch to regular mode")
            root_logger.setLevel(logging.INFO)
        else:
            gui_logger.info("switch to debug mode")
            root_logger.setLevel(logging.DEBUG)

    def closeEvent(self, event):
        """Exit and wait for the thread to finish"""
        for thread in self.__threads:
            thread[0].quit()
            thread[0].wait()


class RefThread(QThread):
    """Reference parsing thread for the GUI."""

    response_obj = Signal(object)

    def __init__(self, reference, format_config, parent=None):
        super().__init__(parent)
        self.reference = reference
        self.format_config = format_config

    def run(self):
        """Emit the parsed api object"""
        self.response_obj.emit(RefAPI(self.reference, self.format_config))


class FormatThread(QThread):
    """Convert result to templated formats"""

    response_str = Signal(str)

    def __init__(self, api_object, ref_format, parent=None):
        super().__init__(parent)
        self.api_object = api_object
        self.ref_format = ref_format

    def run(self):
        """Emit the parsed ref_format string"""
        self.response_str.emit(self.api_object.render(self.ref_format))


class QLogSignal(QThread):
    """Qt signal for logging

    To create a thread safe logging, need to use signal-slot to pass the
    logging and formatting message
    """

    log_str = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)


class QLogHandler(logging.Handler):
    """Custom handler to stream log to QTextEdit

    To have a thread safe to exit, need to define parent of the signal
    thread, here passed as the parent parameters.
    """

    def __init__(self, parent=None):
        super().__init__()
        self.signal = QLogSignal(parent)

    def emit(self, record):
        """Emit colored log record"""
        coloredlog = self.colorlog(record)
        self.signal.log_str.emit(coloredlog)

    def colorlog(self, record):
        """Set different color to error and warning levels

        The levels colored: warning - yellow, error - red
        and critical - purple

        """
        msg = self.format(record)
        color_format = "<span style='color:{}'>{}</span>"
        level_color = defaultdict(lambda: "black")
        level_color.update(
            {
                "WARNING": "DarkOrange",
                "ERROR": "red",
                "CRITICAL": "purple",
                "DEBUG": "SteelBlue",
            }
        )
        return color_format.format(level_color[record.levelname], msg)


def refparse_gui(formats):
    """main function call for GUI

    The function called by the commendline interface
    :param formats dict: dictionary of format configurations
    """
    parser = QApplication(sys.argv)
    font = QFont()
    font.setFamily("Arial")
    parser.setFont(font)
    parser.setStyle("fusion")
    main_parser = ParserGUI(formats)
    main_parser.show()
    sys.exit(parser.exec_())
