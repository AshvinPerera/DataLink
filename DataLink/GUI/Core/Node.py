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

    def get_socket_position(self, index: int, socket_type: SocketType):
        x = 6 if socket_type == SocketType.INPUT else (self.node_view.width - 14)
        y = (
                self.node_view.title_height +
                self.node_view.padding +
                self.node_view.edge_size + index *
                self.socket_spacing
        )
        return x, y


class NodeView(QGraphicsItem):
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
