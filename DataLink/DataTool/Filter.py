import pandas as pd
import pyarrow as pa

from enum import IntEnum
from typing import Any
from dataclasses import dataclass


class ComparisonFlag(IntEnum):
    SAME = 1
    LESS = 2
    MORE = 4
    BETWEEN = 5


@dataclass
class FilterInstruction:
    columns: list
    flag: int
    value: Any

    def __init__(self, columns: list, flags: list, value: Any):
        self.columns = columns
        self.flag = 0
        for flag in flags:
            self.flag = self.flag + int(flag)
        self.value = value


def filter_data_by(dataframe: pd.DataFrame, filter_instructions: list) -> pd.Series:
    output = pd.Series([False] * len(dataframe.axes[0]))
    for instruction in filter_instructions:
        output = output | filter_by(dataframe, instruction)
    return output


def filter_by(dataframe: pd.DataFrame, instruction: FilterInstruction) -> pd.Series:
    output = pd.Series([False] * len(dataframe.axes[0]))

    for column_name in instruction.columns:
        column = pd.Series(dataframe[column_name])
        value = instruction.value
        if instruction.flag == int(ComparisonFlag.SAME):
            output = output | is_the_same(column, value)
        elif instruction.flag == int(ComparisonFlag.MORE):
            output = output | is_more(column, value)
        elif instruction.flag == int(ComparisonFlag.LESS):
            output = output | is_less(column, value)
        elif instruction.flag == int(ComparisonFlag.SAME + ComparisonFlag.MORE):
            output = output | is_the_same_or_more(column, value)
        elif instruction.flag == int(ComparisonFlag.SAME + ComparisonFlag.LESS):
            output = output | is_the_same_or_less(column, value)
        elif instruction.flag == int(ComparisonFlag.BETWEEN):
            output = output | (is_the_same_or_more(column, value[0]) & is_the_same_or_less(column, value[1]))
        else:
            pass
    return output


def is_the_same(column: pd.Series, value: Any) -> pd.Series:
    if value is pd.NA:
        return column.isna().convert_dtypes(dtype_backend='pyarrow')
    output = column == value
    output.replace(pd.NA, False, inplace=True)
    return output


def is_more(column: pd.Series, value: Any) -> pd.Series:
    output = column > value
    output.replace(pd.NA, False, inplace=True)
    return output


def is_less(column: pd.Series, value: Any) -> pd.Series:
    output = column < value
    output.replace(pd.NA, False, inplace=True)
    return output


def is_the_same_or_more(column: pd.Series, value: Any) -> pd.Series:
    return is_the_same(column, value) | is_more(column, value)


def is_the_same_or_less(column: pd.Series, value: Any) -> pd.Series:
    return is_the_same(column, value) | is_less(column, value)
