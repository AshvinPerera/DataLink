from PyQt6.QtWidgets import (
    QWidget, QGraphicsPathItem, QStyleOptionGraphicsItem, QGraphicsItem,
    QGraphicsSceneDragDropEvent, QGraphicsSceneMouseEvent
)
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath
from PyQt6.QtCore import Qt, QPointF
from typing import Optional

from ReportBuilder.GUI.Enums import SocketType


class Edge:
    def __init__(self, start_socket, end_socket):
        self.start_socket = start_socket
        self.end_socket = end_socket
        self.edge_view = EdgeView(self)
        self.setup()

    def setup(self):
        self.start_socket.set_connected_edge(self, SocketType.OUTPUT)
        self.end_socket.set_connected_edge(self, SocketType.INPUT)

    def remove_from_sockets(self):
        if self.start_socket is not None:
            self.start_socket.edge = None
        if self.end_socket is not None:
            self.end_socket.edge = None
        self.start_socket = None
        self.end_socket = None

    def remove(self):
        self.remove_from_sockets()
        self.edge_view = None


class EdgeView(QGraphicsPathItem):
    def __init__(self, edge: Edge):
        super().__init__()
        self.edge = edge
        self.source_position = None
        self.destination_position = None
        self.set_source(
            edge.start_socket.socket_view.scenePos().x(),
            edge.start_socket.socket_view.scenePos().y()
        )
        self.set_destination(
            edge.end_socket.socket_view.scenePos().x(),
            edge.end_socket.socket_view.scenePos().y()
        )
        self._colour_default = QColor('#001000')
        self._colour_selected = QColor('#00FF00')
        self._pen_default = QPen(self._colour_default)
        self._pen_selected = QPen(self._colour_selected)
        self._pen_default.setWidthF(2.0)
        self._pen_selected.setWidthF(2.0)

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        self.update_path()
        if self.isSelected():
            painter.setPen(self._pen_selected)
        else:
            painter.setPen(self._pen_default)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path())

    def update_path(self):
        distance = (
            (self.destination_position[0] - self.source_position[0]) * 0.5
            if self.source_position[0] > self.destination_position[0]
            else (self.source_position[0] - self.destination_position[0]) * 0.5
        )
        path = QPainterPath(QPointF(self.source_position[0] + 5, self.source_position[1] + 5))
        path.cubicTo(
             self.source_position[0] - distance,
             self.source_position[1],
             self.destination_position[0] + distance,
             self.destination_position[1],
             self.destination_position[0] + 5,
             self.destination_position[1] + 5
         )
        self.setPath(path)

    def set_source(self, x, y):
        self.source_position = [x, y]

    def set_destination(self, x, y):
        self.destination_position = [x, y]
