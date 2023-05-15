import pandas as pd

from PyQt6.QtGui import QPainter, QIcon
from PyQt6.QtCore import Qt, QAbstractTableModel, QAbstractItemModel, QVariant, QModelIndex
from PyQt6.QtWidgets import (
    QLabel, QPushButton, QFrame, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit, QFileDialog, QTextEdit,
    QWidget, QStyledItemDelegate, QStyleOptionViewItem, QComboBox, QApplication, QStyle, QSizePolicy
)

from io import TextIOBase
from pathlib import Path
from typing import Callable, Any


"""
Additional data structures
"""


class Logger(TextIOBase):
    def __init__(self):
        self.log = QTextEdit()
        self.log.setReadOnly(True)

    def write(self, string):
        self.log.append(string)


class PandasModel(QAbstractTableModel):
    def __init__(self, data: pd.DataFrame, custom_header: list = None):
        super().__init__()
        self._data = data
        if custom_header:
            self.header = custom_header
        else:
            self.header = list(data.columns)

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                return QVariant(str(self._data.iloc[index.row()][index.column()]))
        return QVariant()

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.header[section]
            else:
                return section + 1

    def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        if role == Qt.ItemDataRole.EditRole:
            self._data.iloc[index.row(), index.column()] = value
            return True
        return False

    def flags(self, index):
        flags = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
        if index.column() == 0:
            flags = Qt.ItemFlag.NoItemFlags
        return flags


class ComboBoxSelection(QStyledItemDelegate):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.items = []

    def set_items(self, items: list):
        self.items = items

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QWidget:
        type_dropdown = QComboBox(parent)
        type_dropdown.addItems(self.items)
        return type_dropdown

    def setEditorData(self, editor: QWidget, index: QModelIndex) -> None:
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        if value:
            editor.setCurrentText(value.value())

    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex) -> None:
        model.setData(index, editor.currentText(), Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        editor.setGeometry(option.rect)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        option.text = index.data(Qt.ItemDataRole.DisplayRole)
        QApplication.style().drawControl(QStyle.ControlElement.CE_ItemViewItem, option, painter)


class DTypeEnforcer(QStyledItemDelegate):
    def __init__(self, d_type: type, parent: QWidget = None):
        super().__init__(parent)
        self.d_type = d_type

    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex) -> None:
        value = editor.text()
        if value == 'NA' or value == '<NA>':
            value = pd.NA
        elif self.d_type == bool:
            if value == 'True':
                value = True
            elif value == 'False':
                value = False
            elif value.isdigit():
                value = bool(int(value))
            else:
                return
        else:
            value = self.d_type(value)
        model.setData(index, value, Qt.ItemDataRole.EditRole)


"""
Widget creation helper functions
"""


def horizontal_line() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    return line


def error_dialog(message: str) -> QDialog:
    dialog = QDialog()
    layout = QVBoxLayout()

    dialog.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    dialog.setLayout(layout)

    label = QLabel(message, dialog)
    layout.addWidget(label)
    layout.setContentsMargins(10, 10, 10, 0)
    dialog.setWindowTitle('Error!')
    dialog.setWindowIcon(QIcon("icon.jpg"))
    return dialog


def create_file_dialog(title: str, file_path: dict) -> QDialog:
    dialog = QDialog()
    layout = QGridLayout()

    dialog.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    dialog.setLayout(layout)

    label_filename = QLabel('File name:')
    input_name = QLineEdit()
    label_directory = QLabel('File path:')
    input_path = QLineEdit()
    search_button = directory_search_button()
    search_button.clicked.connect(lambda: directory_search(input_path))
    create_file = create_file_button(dialog, input_name, input_path, file_path)

    layout.addWidget(label_filename, 0, 0)
    layout.addWidget(input_name, 0, 1)
    layout.addWidget(label_directory, 1, 0)
    layout.addWidget(input_path, 1, 1)
    layout.addWidget(search_button, 1, 2)
    layout.addWidget(create_file, 2, 0)

    dialog.setWindowTitle(title)
    dialog.setWindowIcon(QIcon("icon.jpg"))

    return dialog


def directory_search_button() -> QPushButton:
    search_button = QPushButton()
    search_button.setText('...')
    search_button.setMaximumSize(30, 100)
    return search_button


def edit_button() -> QPushButton:
    edit = QPushButton()
    edit.setText('Edit')
    edit.setMaximumSize(40, 100)
    return edit


def create_button() -> QPushButton:
    create = QPushButton()
    create.setText('Create New')
    create.setMaximumSize(90, 100)
    return create


def save_data_button(filename: str, dataset: pd.DataFrame, ) -> QPushButton:
    save_button = QPushButton('Apply')
    save_button.clicked.connect(lambda: save_data(filename, dataset))
    return save_button


def create_file_button(dialog: QDialog, input_name: QLineEdit, input_path: QLineEdit, filepath: dict) -> QPushButton:
    button = QPushButton('Create')
    button.clicked.connect(lambda: set_file_path(dialog, input_name, input_path, filepath))
    return button


def creator_options(edit, create) -> QWidget:
    creator_widget = QWidget()
    layout = QHBoxLayout()
    layout.addWidget(edit)
    layout.addWidget(QLabel('or'))
    layout.addWidget(create)
    layout.addStretch()
    creator_widget.setLayout(layout)
    return creator_widget


"""
Action implementation helper functions
"""


def csv_search(input_field: QLineEdit) -> None:
    file_name = QFileDialog.getOpenFileName(None, 'Open CSV', '../', 'CSV Files (*.csv)')
    input_field.setText(file_name[0])


def directory_search(input_field: QLineEdit) -> None:
    file_name = QFileDialog.getExistingDirectory(None, 'Open Directory', '../',  QFileDialog.Option.ShowDirsOnly)
    file_name += '/'
    input_field.setText(file_name)


def get_absolute_filepath(filepath) -> str:
    current_directory = str(Path(__file__).parent.absolute())
    path = current_directory + filepath
    return path


def save_data(filename: str, dataset: pd.DataFrame) -> None:
    dataset.to_csv(filename, index=False)


def set_file_path(dialog: QDialog, input_name: QLineEdit, input_path: QLineEdit, filepath: dict) -> None:
    if input_path.text() == '':
        error_dialog('Please add a file name\n').exec()
        return None

    if input_name.text() == '':
        error_dialog('Please add a file path\n').exec()
        return None

    filepath['path'] = input_path.text()
    filepath['name'] = (input_name.text() + '.csv')
    dialog.close()
