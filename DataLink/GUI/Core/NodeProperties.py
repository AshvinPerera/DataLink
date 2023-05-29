from PyQt6.QtWidgets import QWidget, QFrame, QVBoxLayout, QStackedLayout, QLabel

from DataLink.GUI.Support.Enums import PropertyUI
from DataLink.GUI.NodeUI.ImportUI import ImportUI
from DataLink.GUI.NodeUI.FilterUI import FilterUI


class NodeProperties:
    def __init__(self):
        self.frame = PropertyFrame()
        self.ui_list = [PropertyUI.NO_UI]
        self.old_args = []

    def get_node_properties(self):
        return self.frame

    def set_ui(self, ui_type: PropertyUI, *args):
        self.frame.save_panel(*self.old_args)
        if ui_type == PropertyUI.NO_UI:
            self.old_args = []
        else:
            self.old_args = [*args]
        self.frame.set_panel(self.ui_list.index(ui_type), *args)

    def create_ui(self, ui_type: PropertyUI):
        if ui_type not in self.ui_list:
            self.ui_list.append(ui_type)
            if ui_type == PropertyUI.IMPORT_CSV_UI:
                self.frame.create_panel(int(ui_type), ImportUI())
            if ui_type == PropertyUI.CLEANER_REPLACE_UI:
                self.frame.create_panel(int(ui_type), FilterUI())


class PropertyFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.property_widget = QWidget()
        self.property_layout = QStackedLayout()
        self.title = QLabel('Node Properties')
        self.setup()

    def setup(self):
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        main_layout = QVBoxLayout()

        self.setLayout(main_layout)
        self.property_widget.setLayout(self.property_layout)

        main_layout.addWidget(self.title)
        main_layout.addWidget(self.property_widget)
        main_layout.addStretch()
        self.property_layout.insertWidget(0, QWidget())
        self.property_layout.setCurrentIndex(0)

    def create_panel(self, index: int, properties: QWidget):
        self.property_layout.insertWidget(index, properties)
        print('a')

    def set_panel(self, index: int, *args):
        self.property_layout.setCurrentIndex(index)
        if index != 0:
            self.property_layout.currentWidget().set_panel(*args)
        self.property_layout.update()

    def save_panel(self, *args):
        if self.property_layout.currentIndex() != 0:
            self.property_layout.currentWidget().save_panel(*args)
