from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem
from PyQt6.QtGui import QColor, QPen, QBrush, QPainterPath
from PyQt6.QtCore import QRectF

from DataLink.GUI.Core.Edge import Edge
from DataLink.GUI.Support.Enums import SocketType


class Socket:
    def __init__(self, node, index: int, socket_type: SocketType = SocketType.OUTPUT):
        self.socket_view = SocketView(self)
        self.index = index
        self.node = node
        self.edge_list = []
        self.socket_type = socket_type
        self.socket_view.setParentItem(self.node.node_view)
        self.socket_view.setPos(*self.node.get_socket_position(index, socket_type))

    def set_connected_edge(self, edge: Edge, socket_type: SocketType):
        self.edge_list.append({'Edge': edge, 'Type': socket_type})

    def update_edge_position(self):
        for edge_info in self.edge_list:
            if edge_info['Type'] == SocketType.INPUT:
                edge_info['Edge'].edge_view.set_destination(
                    self.socket_view.scenePos().x(),
                    self.socket_view.scenePos().y()
                )
            else:
                edge_info['Edge'].edge_view.set_source(
                    self.socket_view.scenePos().x(),
                    self.socket_view.scenePos().y()
                )

    def connected(self, end_socket):
        for edge_info in self.edge_list:
            if edge_info['Type'] == SocketType.OUTPUT:
                if edge_info['Edge'].end_socket == end_socket:
                    return True
                else:
                    return False


class SocketView(QGraphicsItem):
    def __init__(self, socket: Socket):
        super().__init__()
        self.socket = socket
        self.length = 8.0
        self.radius = 6.0
        self.outline_width = 1.0
        self._color_background = QColor('#E3212121')
        self._color_outline_default = QColor('#E0E0E0')
        self._color_outline_selected = QColor('#FFFFA637')
        self._pen_default = QPen(self._color_outline_default)
        self._pen_selected = QPen(self._color_outline_selected)
        self._brush = QBrush(self._color_background)
        self.setup()

    def setup(self):
        self._pen_default.setWidthF(self.outline_width)
        self._pen_selected.setWidthF(self.outline_width)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

    def paint(self, painter, style: QStyleOptionGraphicsItem, widget=None):
        painter.setBrush(self._brush)

        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        socket_path = QPainterPath()
        socket_path.addRoundedRect(0.0, 0.0, self.length, self.length, self.radius, self.radius)
        painter.drawPath(socket_path.simplified())

    def boundingRect(self):
        return QRectF(
            - self.radius - self.outline_width,
            - self.radius - self.outline_width,
            2 * (self.radius + self.outline_width),
            2 * (self.radius + self.outline_width),
        )
