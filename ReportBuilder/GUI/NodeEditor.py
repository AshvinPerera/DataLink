from PyQt6.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QScrollBar, QListWidget
from PyQt6.QtCore import Qt, QRectF, QLine, QEvent, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QMouseEvent, QDragEnterEvent, QDropEvent, QDragMoveEvent
import math

from ReportBuilder.GUI.Enums import State
from ReportBuilder.GUI.Node import Node
from ReportBuilder.GUI.ImportNodes import CSVInputNode
from ReportBuilder.GUI.CombineNodes import StackNode
from ReportBuilder.GUI.Sockets import Socket
from ReportBuilder.GUI.Edge import Edge
from ReportBuilder.GUI.NodeProperties import NodeProperties
from ReportBuilder.GUI.Input import InputManager


class NodeEditor:
    def __init__(self, node_properties: NodeProperties):
        self.node_editor_scene = None
        self.node_editor_view = None
        self.node_browser = None
        self.node_properties = node_properties
        self.state = State.NO_OPERATION
        self.node_index = 1

        self.nodes = []
        self.edges = []
        self.scene_height = 64000
        self.scene_width = 64000

        self.setup()

    def setup(self):
        self.node_editor_scene = NodeEditorScene(self.scene_height, self.scene_width)
        self.node_editor_view = NodeEditorView(self)
        self.node_editor_view.setScene(self.node_editor_scene)
        self.node_editor_view.handle_node = self.handle_node

    def add_node(self, node: Node):
        self.nodes.append(node)
        self.node_editor_scene.addItem(node.node_view)

    def add_edge(self, edge: Edge):
        self.edges.append(edge)
        self.node_editor_scene.addItem(edge.edge_view)

    def remove_node(self, node: Node):
        self.nodes.remove(node)

    def remove_edge(self, edge: Edge):
        self.edges.remove(edge)

    def get_node_editor(self):
        return self.node_editor_view

    def handle_node(self, node_name: str, node_position: QPointF):
        if node_name == 'Data Importer':
            self.add_node(CSVInputNode(self, self.node_index, self.node_properties, node_position))
            self.node_index += 1
        elif node_name == 'Stack':
            self.add_node(StackNode(self, self.node_index, self.node_properties, node_position))
            self.node_index += 1


class NodeEditorScene(QGraphicsScene):
    def __init__(self, height: int, width: int):
        super().__init__()
        self.grid_size = 10
        self.grid_squares = 5
        light_line_colour = '#3d3d3d'
        dark_line_colour = '#272727'
        background_colour = '#313131'
        self.pen_light = QPen(QColor(light_line_colour))
        self.pen_dark = QPen(QColor(dark_line_colour))
        self.setBackgroundBrush(QColor(background_colour))
        self.pen_light.setWidth(1)
        self.pen_dark.setWidth(2)
        self.setSceneRect(-width // 2, -height // 2, width, height)

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        super().drawBackground(painter, rect)

        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.grid_size)
        first_top = top - (top % self.grid_size)

        lines_light, lines_dark = [], []
        for x in range(first_left, right, self.grid_size):
            if x % (self.grid_size * self.grid_squares) != 0:
                lines_light.append(QLine(x, top, x, bottom))
            else:
                lines_dark.append(QLine(x, top, x, bottom))

        for y in range(first_top, bottom, self.grid_size):
            if y % (self.grid_size * self.grid_squares) != 0:
                lines_light.append(QLine(left, y, right, y))
            else:
                lines_dark.append(QLine(left, y, right, y))

        painter.setPen(self.pen_light)
        painter.drawLines(*lines_light)

        painter.setPen(self.pen_dark)
        painter.drawLines(*lines_dark)


class NodeEditorView(QGraphicsView):
    def __init__(self, node_editor: NodeEditor):
        super().__init__()
        self.node_handle = node_editor
        self.input_manager = InputManager(self, node_editor)
        self.center_position = QPointF(0.0, 0.0)
        self.setup()

    def setup(self):
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing |
            QPainter.RenderHint.TextAntialiasing |
            QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setAcceptDrops(True)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.input_manager.on_left_mouse_button_press(super(), event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.input_manager.on_left_mouse_button_release(super(), event)
        else:
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.input_manager.on_left_mouse_button_double_click()
        else:
            super().mouseDoubleClickEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if type(event.source()) == QListWidget:
            event.setAccepted(True)

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        if type(event.source()) == QListWidget:
            event.setAccepted(True)

    def dropEvent(self, event: QDropEvent) -> None:
        node_name = event.source().currentItem().text()
        node_position = event.position()
        node_position.setY(node_position.y() - 230)
        node_position.setX(node_position.x() - 460)
        self.node_handle.handle_node(node_name, node_position)
