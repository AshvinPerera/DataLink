"""
Node Module: PyQt6-based Node
-----------------------------
This Python script defines two classes (Node and NodeView) for building the functional and graphical representation of
a node with PyQt6, a popular Python binding of the Qt library.
"""


from PyQt6.QtWidgets import (
    QGraphicsItem, QGraphicsTextItem, QGraphicsPixmapItem, QStyleOptionGraphicsItem, QGraphicsSceneMouseEvent
)
from PyQt6.QtGui import QPainterPath, QPen, QBrush, QColor, QFont, QPainter, QPixmap
from PyQt6.QtCore import Qt, QPointF, QRectF
from typing import Any

from DataLink.GUI.Core.Sockets import SocketType
from DataLink.GUI.Core.NodeProperties import NodeProperties
from DataLink.GUI.Support.Helper import get_absolute_filepath


class Node:
    """
    Description
    -----------
    The Node class serves as a representation of a single node in a node editor. This node may have several properties
    and may be connected with other nodes through input and output sockets.

    Node Attributes
    ---------------
    index: The index position of this node in the node editor.
    node_properties: This node's access to the NodeProperties UI interface that allows it to display its properties to
                     the user.
    node_editor: The parent node editor to which this node belongs.
    title: The title or name of the node (default: "Undefined").
    icon_path: The path to the icon image for the node. The path is processed through the get_absolute_filepath
               function.
    node_view: An instance of NodeView that represents the graphical view of the node in the node editor.
    inputs: A list to hold input sockets for the node.
    outputs: A list to hold output sockets for the node.
    socket_spacing: The distance between each socket on the node (default: 22).

    Node Methods
    ------------
    __init__: Initializes the Node with its properties and graphical view.
    get_socket_position: Returns the x, y position of a socket on the node.
    """
    def __init__(
            self,
            node_editor,
            node: Any,
            index: int,
            node_properties: NodeProperties,
            position: QPointF,
            icon_path: str,
            title: str = 'Undefined',
            width: int = 180,
            height: int = 80
    ):
        self.index = index
        self.node_properties = node_properties
        self.node_editor = node_editor
        self.title = title
        icon_path = get_absolute_filepath(icon_path)
        self.node_view = NodeView(node, position, title, width, height, 10.0, icon_path)
        self.inputs = []
        self.outputs = []
        self.socket_spacing = 22

    def get_socket_position(self, index: int, socket_type: SocketType) -> tuple:
        """
        Description
        -----------
        Returns the x, y position of a socket on the node.

        The vertical distance between 2 sockets is dependent on the socket spacing (22)

        Parameters
        ----------
        index: int
            the index position of the socket of type SocketType in the nodes list of sockets
        socket_type: SocketType
            identifies if the socket is an input socket or an output socket
        """
        x = 6 if socket_type == SocketType.INPUT else (self.node_view.width - 14)
        y = (
                self.node_view.title_height +
                self.node_view.padding +
                self.node_view.edge_size + index *
                self.socket_spacing
        )
        return x, y


class NodeView(QGraphicsItem):
    """
    The NodeView class is a subclass of QGraphicsItem, providing a custom graphics item that represents a node in a
    PyQt6 scene.

    NodeView Attributes
    -------------------
    node: The Node that this NodeView visually represents.
    _title, title_item: The title of the node and the corresponding QGraphicsTextItem.
    _icon, icon_item: The icon of the node and the corresponding QGraphicsPixmapItem.
    _start_position: Used to store the initial position of a node when a mouse drag operation begins.
    width, height, edge_size: The dimensions of the node view and the size of the rounded edges.
    Various QPen, QBrush, QFont, QColor instances: These attributes are used to style the node.

    NodeView Methods
    ----------------
    __init__: Initializes the NodeView and sets its graphical properties.
    setup: Initializes the title and icon of the node.
    boundingRect: Returns the bounding rectangle of the node.
    initialize_title: Initializes the title text item of the node.
    initialize_icon: Initializes the icon pixmap item of the node.
    get_title, set_title: Getter and setter for the title of the node.
    paint: Paints the node item within a QPainter context.
    mousePressEvent, mouseMoveEvent, mouseReleaseEvent: Overrides to handle mouse events, allowing for node selection
                                                        and dragging.
    itemChange: Overrides to handle changes to QGraphicsItem properties, such as selection status.
    update_edges: Updates the position of all edges connected to the node's sockets.
    """
    def __init__(self, node: Node, position: QPointF, title: str, width: int, height: int, size: float, icon_path: str):
        super().__init__()
        self.node = node
        self._title = None
        self.title_item = None
        self._icon = None
        self.icon_item = None
        self._start_position = None

        self._title_color = Qt.GlobalColor.white
        self._title_font = QFont('Ubuntu', 10)
        self.title_height = 24.0
        self.padding = 4.0

        self.width = width
        self.height = height
        self.edge_size = size

        self._pen_default = QPen(QColor("#7F000000"))
        self._pen_selected = QPen(QColor("#FFFFA637"))
        self._brush_title = QBrush(QColor("#FF313131"))
        self._brush_background = QBrush(QColor("#E3212121"))

        self.setup(title, icon_path)
        self.setPos(position)

    def setup(self, title: str, icon_path: str):
        self.initialize_title()
        self.set_title(title)
        if icon_path is not None:
            self.initialize_icon(icon_path)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

    def boundingRect(self):
        return QRectF(
            0,
            0,
            self.width,
            self.height
        ).normalized()

    def initialize_title(self):
        self.title_item = QGraphicsTextItem(self)
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self.padding, 1)
        self.title_item.setTextWidth(self.width - 2 * self.padding)

    def initialize_icon(self, icon_path: str):
        icon_pixmap = QPixmap(icon_path)
        self.icon_item = QGraphicsPixmapItem(icon_pixmap, self)
        self.icon_item.setPos(self.width - 20, 4)

    def get_title(self):
        return self._title

    def set_title(self, value: str):
        self._title = value
        self.title_item.setPlainText(self._title)

    def paint(self, painter: QPainter, style: QStyleOptionGraphicsItem, widget=None):
        # title
        path_title = QPainterPath()
        path_title.setFillRule(Qt.FillRule.WindingFill)
        path_title.addRoundedRect(0, 0, self.width, self.title_height, self.edge_size, self.edge_size)
        path_title.addRect(0, self.title_height - self.edge_size, self.edge_size, self.edge_size)
        path_title.addRect(self.width - self.edge_size, self.title_height - self.edge_size, self.edge_size,
                           self.edge_size)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())

        # content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.FillRule.WindingFill)
        path_content.addRoundedRect(0, self.title_height, self.width, self.height - self.title_height, self.edge_size,
                                    self.edge_size)
        path_content.addRect(0, self.title_height, self.edge_size, self.edge_size)
        path_content.addRect(self.width - self.edge_size, self.title_height, self.edge_size, self.edge_size)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())

        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(0, 0, self.width, self.height, self.edge_size, self.edge_size)
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path_outline.simplified())

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._start_position = event.pos()
            if not self.isSelected():
                self.setSelected(True)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        if self._start_position:
            delta = event.pos() - self._start_position
            self.setPos(self.pos() + delta)
            self.update_edges()
            return
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._start_position = None
        else:
            super().mouseReleaseEvent(event)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            if bool(value) is True:
                self.node.set_property_ui()
            else:
                self.node.remove_property_ui()
        return super(NodeView, self).itemChange(change, value)

    def update_edges(self):
        for socket in self.node.inputs:
            socket.update_edge_position()
        for socket in self.node.outputs:
            socket.update_edge_position()
