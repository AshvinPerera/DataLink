from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QAbstractItemView
from PyQt6.QtCore import Qt

from ReportBuilder.GUI.Node import Node
from ReportBuilder.GUI.ImportNodes import CSVInputNode
from ReportBuilder.GUI.CombineNodes import StackNode
from ReportBuilder.GUI.NodeEditor import NodeEditor
from ReportBuilder.GUI.NodeProperties import NodeProperties


class NodeBrowser:
    def __init__(self):
        self.node_creators = {
            'Data Importer': CSVInputNode,
            'Stack': StackNode
        }
        self._frame = BrowserFrame(list(self.node_creators.keys()))

    def get_node_browser(self):
        return self._frame


class BrowserFrame(QFrame):
    def __init__(self, node_list: list):
        super().__init__()
        self.search_bar = QLineEdit()
        self.node_list = QListWidget()
        self.setup(node_list)

    def setup(self, node_list: list):
        self.node_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.node_list.setDragEnabled(True)
        self.node_list.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addWidget(self.search_bar)
        main_layout.addWidget(self.node_list)

        for i in range(len(node_list)):
            item = QListWidgetItem(node_list[i])
            self.node_list.insertItem(i, item)
