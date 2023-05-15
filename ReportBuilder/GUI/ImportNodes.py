from PyQt6.QtCore import QPointF

from ReportBuilder.GUI.Node import Node
from ReportBuilder.GUI.Sockets import Socket
from ReportBuilder.GUI.Enums import PropertyUI
from ReportBuilder.GUI.NodeProperties import NodeProperties
from ReportBuilder.GUI.DataManager import CSVImportManager, SchemaManager, ValidationManager
from ReportBuilder.GUI.ImportUI import ImportUI


class CSVInputNode(Node):
    def __init__(
            self,
            node_editor,
            index: int,
            node_properties: NodeProperties,
            position: QPointF,
            title: str = 'Data Import',
            width: int = 120,
            height: int = 65
    ):
        super().__init__(
            node_editor,
            self,
            index,
            node_properties,
            position,
            '\\icons\\import-csv.png',
            title,
            width,
            height
        )
        self.csv_manager = CSVImportManager()
        self.schema_manager = SchemaManager()
        self.validation_manager = ValidationManager()
        self.import_ui = ImportUI()
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
