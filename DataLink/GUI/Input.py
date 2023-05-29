from PyQt6.QtWidgets import QGraphicsView, QGraphicsItem
from PyQt6.QtCore import Qt, QEvent, QPointF
from PyQt6.QtGui import QMouseEvent

from DataLink.GUI.Enums import State
from DataLink.GUI.Node import NodeView
from DataLink.GUI.Sockets import SocketView
from DataLink.GUI.Edge import Edge


class InputManager:
    def __init__(self, node_editor_view, node_editor):
        self.drag_threshold = 10
        self.last_lmb_press_position = None
        self.start_socket = None
        self.end_socket = None
        self.node_editor = node_editor
        self.node_editor_view = node_editor_view

    def on_left_mouse_button_press(self, graphics_view: QGraphicsView, event: QMouseEvent) -> None:
        deselect_other_items(self.node_editor_view, event)
        handle_socket_creation(self, self.node_editor_view, event)
        enable_drag(self.node_editor_view, graphics_view, event)

    def on_left_mouse_button_release(self, graphics_view: QGraphicsView, event: QMouseEvent) -> None:
        disable_drag(self.node_editor_view, graphics_view, event)
        handle_socket_creation(self, self.node_editor_view, event)

    def on_left_mouse_button_double_click(self) -> None:
        self.node_editor_view.centerOn(self.node_editor_view.center_position)


"""
Input related helper functions 
"""


def get_item_at_click(
        node_editor_view,
        event: QMouseEvent
) -> QGraphicsItem:
    position = event.pos()
    item_at_click = node_editor_view.itemAt(position)
    return item_at_click


def deselect_other_items(
        node_editor_view,
        event: QMouseEvent
) -> None:
    item_at_click = get_item_at_click(node_editor_view, event)
    if item_at_click is not None:
        for item in node_editor_view.items():
            if item == item_at_click:
                item.setSelected(True)
            else:
                item.setSelected(False)


def enable_drag(
        node_editor_view,
        graphics_view: QGraphicsView,
        event: QMouseEvent
) -> None:
    node_editor_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
    drag_start_event = QMouseEvent(
        event.type(),
        event.position(),
        event.globalPosition(),
        Qt.MouseButton.LeftButton,
        event.buttons() | Qt.MouseButton.LeftButton,
        event.modifiers())
    graphics_view.mousePressEvent(drag_start_event)


def disable_drag(
        node_editor_view,
        graphics_view: QGraphicsView,
        event: QMouseEvent
) -> None:
    drag_stop_event = QMouseEvent(
        event.type(),
        event.position(),
        event.globalPosition(),
        Qt.MouseButton.LeftButton,
        event.buttons() | ~Qt.MouseButton.LeftButton,
        event.modifiers())
    graphics_view.mouseReleaseEvent(drag_stop_event)
    node_editor_view.setDragMode(QGraphicsView.DragMode.NoDrag)


def handle_socket_creation(
        input_manager: InputManager,
        node_editor_view,
        event: QMouseEvent
) -> None:
    item = get_item_at_click(node_editor_view, event)
    node_editor = node_editor_view.node_handle

    if event.type() == QEvent.Type.MouseButtonPress:
        if start_socket(input_manager, node_editor, item):
            input_manager.last_lmb_press_position = node_editor_view.mapToScene(event.pos())
            return
        elif end_socket(input_manager, node_editor, item):
            return

    if event.type() == QEvent.Type.MouseButtonRelease:
        new_lmb_press_position = node_editor_view.mapToScene(event.pos())
        if mouse_moved(input_manager.last_lmb_press_position, new_lmb_press_position, input_manager.drag_threshold):
            if end_socket(input_manager, node_editor, item):
                return


def start_socket(input_manager: InputManager, node_editor, item: QGraphicsItem) -> bool:
    if type(item) is SocketView:
        if node_editor.state == State.NO_OPERATION:
            node_editor.state = State.SOCKET_CREATION
            input_manager.start_socket = item.socket
            return True
    return False


def end_socket(input_manager: InputManager, node_editor, item: QGraphicsItem) -> bool:
    if node_editor.state == State.SOCKET_CREATION:
        node_editor.state = State.NO_OPERATION

        if type(item) is SocketView:
            input_manager.end_socket = item.socket
            if (
                    (input_manager.start_socket is not input_manager.end_socket) and
                    (not input_manager.start_socket.connected(input_manager.end_socket)) and
                    (True)
            ):
                node_editor.add_edge(Edge(input_manager.start_socket, input_manager.end_socket))
                input_manager.end_socket.node.on_edge_connect(input_manager.start_socket)
                print('assign end socket')
            return True
    return False


def mouse_moved(start_position: QPointF, end_position: QPointF, threshold: int) -> bool:
    if end_position is not None and start_position is not None:
        vector_distance = end_position - start_position
        scalar_distance = (
                (vector_distance.x() * vector_distance.x()) + (vector_distance.y() * vector_distance.y())
        )
        if scalar_distance > (threshold * threshold):
            return True
        else:
            return False
    return False
