from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QLabel, QTableView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from ReportBuilder.GUI.DataManager import DataManager


def create_stack_data_tab(data_manager: DataManager) -> QWidget:
    page = QWidget()
    panel_layout = QVBoxLayout()
    import_button = QPushButton('Stack Data')

    panel_layout.addSpacing(20)
    panel_layout.addLayout(create_import_panel(data_manager))
    panel_layout.addSpacing(5)
    panel_layout.addWidget(import_button)
    panel_layout.addWidget(horizontal_line())
    panel_layout.addWidget(logger(data_manager))
    panel_layout.addStretch()

    import_button.clicked.connect(lambda: import_data(data_manager))
    page.setLayout(panel_layout)
    return page