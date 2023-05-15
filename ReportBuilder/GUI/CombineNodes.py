from PyQt6.QtCore import QPointF

from ReportBuilder.GUI.Node import Node
from ReportBuilder.GUI.Sockets import Socket
from ReportBuilder.GUI.NodeProperties import NodeProperties
from ReportBuilder.GUI.DataManager import CSVImportManager, SchemaManager, ValidationManager
from ReportBuilder.GUI.Enums import SocketType, PropertyUI
from ReportBuilder.GUI.ImportUI import ImportUI


class StackNode(Node):
    def __init__(
            self,
            node_editor,
            index: int,
            node_properties: NodeProperties,
            position: QPointF,
            title: str = 'Stack Datasets',
            width: int = 120,
            height: int = 85
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
        self.data_manager = DataManager()
        self.import_ui = create_import_csv_tab(self.data_manager)
        self.setup()
        self.setup_sockets()

    def setup(self):
        self.node_properties.create_ui(PropertyUI.IMPORT_CSV_UI)
        self.node_view.property_ui_setter = self.set_property_ui
        self.node_view.property_ui_remover = self.remove_property_ui

    def setup_sockets(self):
        for i in range(0, 2):
            self.inputs.append(Socket(self, i, SocketType.INPUT))
        self.outputs.append(Socket(self, 0, SocketType.OUTPUT))

    def set_property_ui(self):
        self.node_properties.set_ui(
            PropertyUI.IMPORT_CSV_UI,
            self.csv_manager,
            self.schema_manager,
            self.validation_manager
        )

    def remove_property_ui(self):
        self.node_properties.set_ui(PropertyUI.NO_UI)
