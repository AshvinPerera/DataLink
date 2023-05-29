""" This module is the only import required to successfully run the DataLink application

The ApplicationWindow class defines the application window opened when the user starts the application
The run methods creates the application window and starts the application loop

Example
-------
from DataLink.GUI.Main import run

if __name__ == '__main__':
    run()
"""

from PyQt6.QtWidgets import QApplication, QMainWindow, QMenuBar, QWidget, QMenu, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QIcon
import sys

from DataLink.GUI.Core.NodeProperties import NodeProperties
from DataLink.GUI.Core.NodeEditor import NodeEditor
from DataLink.GUI.Core.NodeBrowser import NodeBrowser


class ApplicationWindow(QMainWindow):
    """ Application class that defines methods to create the software ui and run the
    application loop

    The application stores and displays 3 primary ui elements

    Attributes
    ----------
    node_properties: NodeProperties
        Handle to the node property ui element class
    node_editor: NodeEditor
        Handle to the node editor ui element class
    node_browser: NodeBrowser
        Handle to the node browser ui element class
    """
    def __init__(self):
        """ Initialize application ui elements

         Application name: DataLink
         Application icon: TODO: create and include the actual icon using the setWindowIcon method

        this methods ensures that the application begins in maximized windowed mode. The
        window size is later adjustable by the user.
         """
        super().__init__()
        self.setWindowTitle("DataLink")
        self.setWindowIcon(QIcon("icon.jpg"))
        self.node_properties = NodeProperties()
        self.node_editor = NodeEditor(self.node_properties)
        self.node_browser = NodeBrowser()
        self.setup_app()
        self.showMaximized()

    def setup_app(self) -> None:
        """ Sets up the project menu and creates the ui layout for the main application interface """
        self.create_menu()
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(self.create_ui())

    def create_menu(self) -> None:
        """ Builds the application menu bar and adds menu options """
        menu_bar = QMenuBar(self)
        file_menu = QMenu('&File', self)
        help_menu = QMenu('&Help', self)
        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(help_menu)
        self.setMenuBar(menu_bar)

    def create_ui(self) -> QHBoxLayout:
        """ Ensures the correct placement of ui elements within the application interface using
        PyQT layouts

        Returns
        -------
        main_layout: QHBoxLayout
            PyQT horizontal layout containing the placement of the node properties, editor, and browser ui
        """
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
