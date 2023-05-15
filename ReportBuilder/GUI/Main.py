from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QWidget, QTabWidget, QMenu, QVBoxLayout, QHBoxLayout, QFrame, QLabel
)
from PyQt6.QtGui import QIcon
import sys

from ReportBuilder.GUI.NodeProperties import NodeProperties
from ReportBuilder.GUI.NodeEditor import NodeEditor
from ReportBuilder.GUI.NodeBrowser import NodeBrowser

"""
Application class definition
"""


class ApplicationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Report Builder")                   # Application name
        self.setWindowIcon(QIcon("icon.jpg"))                   # Application icon
        self.node_properties = NodeProperties()                 # Datastructure that handles the node properties view UI
        self.node_editor = NodeEditor(self.node_properties)     # Datastructure that handles the node editor UI
        self.node_browser = NodeBrowser()                       # Datastructure that handles the node browser UI
        self.setup_app()                                        # Creates the GUI layout of the program
        self.showMaximized()                                    # Sets the application to maximized view

    def setup_app(self):
        self.create_menu()
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(self.create_ui())

    def create_menu(self):
        menu_bar = QMenuBar(self)
        file_menu = QMenu('&File', self)
        help_menu = QMenu('&Help', self)
        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(help_menu)
        self.setMenuBar(menu_bar)

    def create_ui(self) -> QHBoxLayout:
        main_layout = QHBoxLayout()
        left_panel = QWidget()
        right_panel = QWidget()
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 4)

        left_panel_layout = QVBoxLayout()
        left_panel_layout.addWidget(self.node_properties.get_node_properties())
        left_panel.setLayout(left_panel_layout)

        right_panel_layout = QVBoxLayout()
        right_panel_layout.addWidget(self.node_editor.get_node_editor(), 3)
        right_panel_layout.addWidget(self.node_browser.get_node_browser(), 1)
        right_panel.setLayout(right_panel_layout)

        return main_layout


def run() -> None:
    """ This is the application entry point. """
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = ApplicationWindow()
    window.show()
    sys.exit(app.exec())
