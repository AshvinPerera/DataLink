import pandas as pd

from typing import Any
from dataclasses import dataclass

from DataLink.DataTool.Filter import FilterInstruction, filter_data_by


class DataStorage:
    def __init__(self):
        self.data = None


class PandasStorage(DataStorage):
    def __init__(self):
        super().__init__()

    def set_data(self, data: pd.DataFrame) -> None:
        self.data = data

    def get_columns(self) -> list:
        if self.data is not None:
            return list(data.columns)
        return []


@dataclass
class FilterData:
    column_string: str
    comparison_string: str
    comparison_index: int
    value1_string: str
    value2_string: str
    is_between: bool
    selected_columns: list

    def set_selected_columns(self, column_list: list) -> None:
        self.selected_columns = column_list

        if len(column_list) == 0:
            self.column_string = 'Column'
        elif len(column_list) == 1:
            self.column_string = column_list[0]
        else:
            self.column_string = ', and ' + column_list[-1]
            for i in range(2, len(column_list) - 1):
                self.column_string = ', ' + column_list[-i] + self.column_string
            self.column_string = column_list[0] + self.column_string


class FilterStorage(DataStorage):
    def __init__(self):
        super().__init__()
        self.data = []

    def add_new_filter(self):
        self.data.append(FilterData('Column', 'is', 0, 'missing', '', False, []))

    def remove_filter(self, filter_data: FilterData):
        self.data.remove(filter_data)
