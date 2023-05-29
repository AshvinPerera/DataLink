from PyQt6.QtCore import QPointF

from DataLink.GUI.Node import Node
from DataLink.GUI.Sockets import Socket
from DataLink.GUI.NodeProperties import NodeProperties
from DataLink.GUI.DataStorage import FilterStorage, FilterData, PandasStorage
from DataLink.GUI.Enums import SocketType, PropertyUI
from DataLink.GUI.FilterUI import FilterUI


class ReplaceNode(Node):
    def __init__(
            self,
            node_editor,
            index: int,
            node_properties: NodeProperties,
            position: QPointF,
            title: str = 'Replace Data',
            width: int = 120,
            height: int = 65
    ):
        super().__init__(
            node_editor,
            self,
            index,
            node_properties,
            position,
            '',
            title,
            width,
            height
        )
        self.filter_storage = FilterStorage()
        self.filter_storage.add_new_filter()
        self.pandas_storage = PandasStorage()
        self.setup()
        self.setup_sockets()

    def setup(self):
        self.node_properties.create_ui(PropertyUI.CLEANER_REPLACE_UI)
        self.node_view.property_ui_setter = self.set_property_ui
        self.node_view.property_ui_remover = self.remove_property_ui

    def setup_sockets(self):
        self.inputs.append(Socket(self, 0, SocketType.INPUT))
        self.outputs.append(Socket(self, 0, SocketType.OUTPUT))

    def on_edge_connect(self, socket: Socket):
        self.pandas_storage = socket.node.csv_manager

    def set_property_ui(self):
        if self.pandas_storage is not None:
            self.node_properties.set_ui(
                PropertyUI.CLEANER_REPLACE_UI,
                self.filter_storage,
                self.pandas_storage.get_columns()
            )
        else:
            self.node_properties.set_ui(
                PropertyUI.CLEANER_REPLACE_UI,
                self.filter_storage
            )

    def remove_property_ui(self):
        self.node_properties.set_ui(PropertyUI.NO_UI)
