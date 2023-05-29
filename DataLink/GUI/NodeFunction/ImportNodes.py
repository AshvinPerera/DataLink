from PyQt6.QtCore import QPointF

from DataLink.GUI.Core.Node import Node
from DataLink.GUI.Core.Sockets import Socket
from DataLink.GUI.Support.Enums import PropertyUI
from DataLink.GUI.Core.NodeProperties import NodeProperties
from DataLink.GUI.Support.DataManager import CSVImportManager, SchemaManager, ValidationManager


class CSVInputNode(Node):
    def __init__(
            self,
            node_editor,
            index: int,
            node_properties: NodeProperties,
            position: QPointF,
            title: str = 'CSV Import',
            width: int = 120,
            height: int = 65
    ):
        super().__init__(
            node_editor,
            self,
            index,
            node_properties,
            position,
            '../icons/import-csv.png',
            title,
            width,
            height
        )
        self.csv_manager = CSVImportManager()
        self.schema_manager = SchemaManager()
        self.validation_manager = ValidationManager()
        self.setup()
        self.setup_sockets()

    def setup(self):
        self.node_properties.create_ui(PropertyUI.IMPORT_CSV_UI)
        self.node_view.property_ui_setter = self.set_property_ui
        self.node_view.property_ui_remover = self.remove_property_ui

    def setup_sockets(self):
        socket = Socket(self, 0)
        self.outputs.append(socket)

    def set_property_ui(self):
        self.node_properties.set_ui(
            PropertyUI.IMPORT_CSV_UI,
            self.csv_manager,
            self.schema_manager,
            self.validation_manager
        )

    def remove_property_ui(self):
        self.node_properties.set_ui(PropertyUI.NO_UI)
