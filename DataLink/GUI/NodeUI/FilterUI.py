from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QComboBox, QTextEdit, QDialog, QTableWidget, QTableWidgetItem, QLineEdit, QVBoxLayout, QHBoxLayout)
from PyQt6.QtCore import Qt
from typing import Any

from DataLink.GUI.Support.Helper import horizontal_line
from DataLink.GUI.Support.DataStorage import FilterData, FilterStorage


class ColumnSelector(QDialog):
    def __init__(self, selected_columns: list, dataframe_columns: list):
        super().__init__()
        self.selected_columns = selected_columns
        if dataframe_columns is None:
            self.dataframe_columns = []
        else:
            self.dataframe_columns = dataframe_columns

        self.search_bar = QLineEdit()
        self.table = QTableWidget()
        self.apply_button = QPushButton('Apply')

        self.setup()
        self.setup_table()
        self.setup_search_bar()
        self.apply_button.clicked.connect(self.apply_selection)

    def setup(self):
        layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        layout.addLayout(top_layout)
        top_layout.addWidget(QLabel('Search:'))
        top_layout.addWidget(self.search_bar)
        layout.addWidget(self.table)
        layout.addWidget(self.apply_button)
        self.setLayout(layout)

    def setup_table(self):
        self.table.setRowCount(len(self.dataframe_columns))
        self.table.setColumnCount(1)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setHorizontalHeaderItem(0, QTableWidgetItem("Variable"))

        for index in range(len(self.dataframe_columns)):
            item = QTableWidgetItem(self.dataframe_columns[index])
            item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)

            if self.dataframe_columns[index] in self.selected_columns:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
            self.table.setItem(index, 0, item)

        self.table.itemClicked.connect(self.checkbox_clicked)

    def checkbox_clicked(self, item: QTableWidgetItem):
        if item.checkState() == Qt.CheckState.Checked:
            if item.data(Qt.ItemDataRole.DisplayRole) not in self.selected_columns:
                self.selected_columns.append(item.data(Qt.ItemDataRole.DisplayRole))
        else:
            if item.data(Qt.ItemDataRole.DisplayRole) in self.selected_columns:
                self.selected_columns.remove(item.data(Qt.ItemDataRole.DisplayRole))

    def setup_search_bar(self):  # TODO
        pass

    def apply_selection(self):
        self.close()

    def get_column_list(self) -> list:
        return self.selected_columns


class Filter(QWidget):
    def __init__(self):
        super().__init__()
        self.title = QLabel('Filter:')
        self.filter_text = QLabel('{0} {1} {2}'.format(
            'Column', 'is', 'missing')
        )
        self.column_button = QPushButton('Columns')
        self.comparisons_drop_down = QComboBox()
        self.value1 = QTextEdit()
        self.value2 = QTextEdit()

        self.title.setMaximumHeight(60)
        self.filter_text.setMaximumHeight(60)
        self.column_button.setMaximumWidth(60)
        self.value1.setMaximumSize(50, 28)
        self.value2.setMaximumSize(50, 28)

        self.setup()
        self.setup_drop_down()

    def setup(self):
        filter_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()
        filter_layout.addWidget(horizontal_line())
        filter_layout.addLayout(top_layout)
        filter_layout.addLayout(bottom_layout)
        filter_layout.addWidget(horizontal_line())
        filter_layout.addStretch()

        top_layout.addWidget(self.title)
        top_layout.addWidget(self.filter_text)
        top_layout.addStretch()
        bottom_layout.addWidget(self.column_button)
        bottom_layout.addWidget(self.comparisons_drop_down)
        bottom_layout.addWidget(self.value1)
        bottom_layout.addWidget(self.value2)
        bottom_layout.addStretch()

        self.value2.hide()
        self.setLayout(filter_layout)

    def setup_drop_down(self):
        self.comparisons_drop_down.addItem('is')
        self.comparisons_drop_down.addItem('is not')
        self.comparisons_drop_down.addItem('more than')
        self.comparisons_drop_down.addItem('less than')
        self.comparisons_drop_down.addItem('the same or more than')
        self.comparisons_drop_down.addItem('the same or less than')
        self.comparisons_drop_down.addItem('between')

    def select_columns(self, filter_data: FilterData, dataframe_columns: list = None):
        column_selection_dialog = ColumnSelector(filter_data.selected_columns, dataframe_columns)
        column_selection_dialog.exec()
        filter_data.set_selected_columns(column_selection_dialog.get_column_list())
        self.set_format_string(filter_data)

    def set_comparison(self, filter_data: FilterData):
        text = self.comparisons_drop_down.currentText()

        if text == 'between':
            self.value2.show()
        else:
            self.value2.hide()

        if len(filter_data.selected_columns) > 1:
            if text == 'is':
                filter_data.comparison_string = 'are'
            elif text == 'is not':
                filter_data.comparison_string = 'are not'
            else:
                filter_data.comparison_string = 'are ' + text
        else:
            if text == "is" or text == 'is not':
                filter_data.comparison_string = text
            else:
                filter_data.comparison_string = 'is ' + text
        self.set_format_string(filter_data)

    def text_changed(self, filter_data: FilterData, value_index: int):
        if value_index == 1:
            filter_data.value1_string = self.value1.toPlainText()
        else:
            filter_data.value2_string = self.value2.toPlainText()
        self.set_format_string(filter_data)

    def set_format_string(self, filter_data: FilterData):
        if filter_data.is_between:
            self.filter_text.setText('{0} {1} {2} and {3}'.format(
                filter_data.column_string,
                filter_data.comparison_string,
                filter_data.value1_string,
                filter_data.value2_string)
            )
        else:
            self.filter_text.setText('{0} {1} {2}'.format(
                filter_data.column_string,
                filter_data.comparison_string,
                filter_data.value1_string)
            )

    def set_filter(self, filter_data: FilterData, data: Any = None):
        try:
            self.comparisons_drop_down.activated.disconnect()
            self.value1.textChanged.disconnect()
            self.value2.textChanged.disconnect()
            self.column_button.clicked.disconnect()
        except TypeError:
            pass
        self.comparisons_drop_down.setCurrentIndex(filter_data.comparison_index)
        self.comparisons_drop_down.activated.connect(lambda: self.set_comparison(filter_data))
        self.value1.textChanged.connect(lambda: self.text_changed(filter_data, 1))
        self.value2.textChanged.connect(lambda: self.text_changed(filter_data, 2))
        self.column_button.clicked.connect(lambda: self.select_columns(filter_data, data))
        self.set_format_string(filter_data)

        self.value1.setText(filter_data.value1_string)
        self.value2.setText(filter_data.value2_string)

    def save_filter(self, filter_data: FilterData):
        filter_data.comparison_index = self.comparisons_drop_down.currentIndex()


class FilterUI(QWidget):
    def __init__(self):
        super().__init__()
        self.filter_layout = QVBoxLayout()
        self.filters = [Filter()]
        self.add_filter_button = QPushButton('Add Filter')
        self.setup()

    def setup(self):
        panel_layout = QVBoxLayout()
        panel_layout.addSpacing(20)
        panel_layout.addLayout(self.filter_layout)
        filter_button_layout = QHBoxLayout()
        filter_button_layout.addWidget(self.add_filter_button)
        filter_button_layout.addStretch()
        panel_layout.addLayout(filter_button_layout)
        panel_layout.addStretch()
        self.setLayout(panel_layout)
        self.add_panel(0)

    def add_panel(self, index: int):
        self.filter_layout.addWidget(self.filters[index])

    def remove_panel(self, index: int):
        self.filter_layout.removeWidget(self.filters[index])

    def set_panel(self, filter_storage: FilterStorage, column_list: list = None) -> None:
        try:
            self.add_filter_button.clicked.disconnect()
        except TypeError:
            pass
        self.set_filters(filter_storage, column_list)
        self.add_filter_button.clicked.connect(lambda: self.add_filter(filter_storage, column_list))
        self.update()

    def save_panel(self, filter_storage: FilterStorage, column_list: list = None) -> None:  # TODO: Check if works
        if column_list is not None:
            pass
        for i in range(len(filter_storage.data)):
            self.filters[i].save_filter(filter_storage.data[i])

    def set_filters(self, filter_storage: FilterStorage, column_list: list = None):  # TODO: Broken
        filters = filter_storage.data
        if len(filters) > len(self.filters):
            index = len(self.filters)
            for i in range(len(filters) - len(self.filters)):
                self.filters.append(Filter())
                self.add_panel(index + i)
        elif len(filters) < len(self.filters):
            for i in range(len(self.filters) - len(filters)):
                index = len(self.filters) - 1
                self.remove_panel(index - i)
                self.filters.pop()
        for i in range(len(filters)):
            self.filters[i].set_filter(filters[i], column_list)

    def add_filter(self, filter_storage: FilterStorage, column_list: list = None):
        filter_storage.add_new_filter()
        filters = filter_storage.data
        self.filters.append(Filter())
        self.add_panel(len(self.filters) - 1)
        self.filters[len(self.filters) - 1].set_filter(filters[len(filters) - 1], column_list)
        self.update()
