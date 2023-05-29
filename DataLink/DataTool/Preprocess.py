import pandas as pd
import pyarrow as pa

import re
import sys


def version():
    print('Pandas version: ', pd.__version__)
    print('PyArrow version: ', pa.__version__, '\n')


def read_config(filepath: str) -> pd.DataFrame:
    type_info = {'ColNames': 'string[pyarrow]', 'ColTypes': 'string[pyarrow]', 'NAFill': 'string[pyarrow]'}
    return pd.read_csv(filepath, dtype=type_info, engine='pyarrow', dtype_backend='pyarrow')


def read_validation(filepath: str):
    type_info = {
        'ColNames': 'string[pyarrow]',
        'BoundCheck': 'bool[pyarrow]',
        'LowerBound': 'int64[pyarrow]',
        'UpperBound': 'int64[pyarrow]',
        'ValueCheck': 'bool[pyarrow]',
        'ValuesList': 'string[pyarrow]',
        'NumericCheck': 'bool[pyarrow]',
        'DateFormatCheck': 'bool[pyarrow]',
        'DateFormat': 'string[pyarrow]',
        'RemoveCharacters': 'bool[pyarrow]',
        'Characters': 'string[pyarrow]',
        'RemoveMissing': 'bool[pyarrow]'}
    validation_data = pd.read_csv(filepath, dtype=type_info, engine='pyarrow', dtype_backend='pyarrow')
    return validation_data


def convert_validation(validation_data: pd.DataFrame) -> dict:
    output = {}

    for index, row in validation_data.iterrows():
        output[row['ColNames']] = {
            'Bound Check': [row['LowerBound'], row['UpperBound']] if row['BoundCheck'] else None,
            'Value Check': re.split(',', row['ValuesList']) if row['ValueCheck'] else None,
            'Numeric Check': row['NumericCheck'],
            'Date Format Check': row['DateFormat'] if row['DateFormatCheck'] else None,
            'Remove Characters': re.split(',', row['Characters']) if row['RemoveCharacters'] else None,
            'Remove Missing': row['RemoveMissing']
        }
    return output


def read_data(filepath: str, config: pd.DataFrame, validation: dict = None, logger: object = None) -> pd.DataFrame:
    old_stdout = sys.stdout
    if logger:
        sys.stdout = logger

    dataset = pd.read_csv(filepath, dtype='string[pyarrow]', engine='pyarrow', dtype_backend='pyarrow')
    dataset = dataset.apply(lambda x: x.str.strip())
    dataset = dataset.apply(lambda x: x.replace(r'^\s*$', pd.NA, regex=True))

    if validation:
        dataset = __validate_data(dataset, validation)
    dataset = __fill_missing(dataset, config)

    if logger:
        sys.stdout = old_stdout

    return dataset.astype(__get_type_conversion(config))


def read_csv(filepath: str) -> pd.DataFrame:
    dataset = pd.read_csv(filepath, dtype='string[pyarrow]', engine='pyarrow', dtype_backend='pyarrow')
    dataset = dataset.apply(lambda x: x.str.strip())
    dataset = dataset.apply(lambda x: x.replace(r'^\s*$', pd.NA, regex=True))
    return dataset


def create_schema(columns: list) -> pd.DataFrame:
    type_info = {'ColNames': 'string[pyarrow]', 'ColTypes': 'string[pyarrow]', 'NAFill': 'string[pyarrow]'}
    col_types = ['text'] * len(columns)
    na_fill = ['NA'] * len(columns)
    config = pd.DataFrame({'ColNames': columns, 'ColTypes': col_types, 'NAFill': na_fill}, dtype='string[pyarrow]')
    print(config.dtypes)
    return config.astype(type_info)


"""
Private helper functions
"""


def __get_type_conversion(config: pd.DataFrame) -> dict:
    config.loc[config.ColTypes == 'integer', 'ColTypes'] = 'int64[pyarrow]'
    config.loc[config.ColTypes == 'float', 'ColTypes'] = 'float64[pyarrow]'
    config.loc[config.ColTypes == 'categorical', 'ColTypes'] = 'string[pyarrow]'
    config.loc[config.ColTypes == 'text', 'ColTypes'] = 'string[pyarrow]'
    config.loc[config.ColTypes == 'date', 'ColTypes'] = 'date64[pyarrow]'
    config.loc[config.ColTypes == 'time', 'ColTypes'] = 'time64[us][pyarrow]'
    return pd.Series(config.ColTypes.values, index=config.ColNames).to_dict()


def __fill_missing(dataset: pd.DataFrame, config: pd.DataFrame) -> pd.DataFrame:
    replacement_values = pd.Series(config.NAFill.values, index=config.ColNames).to_dict()

    for key, value in replacement_values.items():
        if value == 'NA':
            dataset.loc[dataset[key].isnull(), key] = pd.NA
        else:
            dataset.loc[dataset[key].isnull(), key] = str(value)

    return dataset


def __validate_data(dataset: pd.DataFrame, validation_instruction: dict) -> pd.DataFrame:
    for key, value in validation_instruction.items():
        if value['Remove Characters']:
            for character in value['Remove Characters']:
                dataset[key] = __remove_character(dataset[key], character)
        if value['Numeric Check']:
            __check_numeric(dataset[key])
            dataset[key] = __enforce_numeric(dataset[key])
        if value['Bound Check']:
            __check_bounds(dataset[key], value['Bound Check'][0], value['Bound Check'][1])
            dataset[key] = __enforce_bounds(dataset[key], value['Bound Check'][0], value['Bound Check'][1])
        if value['Value Check']:
            __check_values(dataset[key], value['Value Check'])
            dataset[key] = __enforce_values(dataset[key], value['Value Check'])
        if value['Date Format Check']:
            __check_date_format(dataset[key], value['Date Format Check'])
            dataset[key] = __enforce_date_format(dataset[key], value['Date Format Check'])
        if value['Remove Missing']:
            dataset = __remove_missing(dataset, key)

    return dataset


def __check_bounds(column: pd.Series, lower_bound: int, upper_bound: int):
    column_copy = pd.to_numeric(column)
    if column[(column_copy < lower_bound) | (column_copy > upper_bound)].shape[0] > 0:
        print('Bounds check for column {0}'.format(column.name))
        data = column[(column_copy < lower_bound) | (column_copy > upper_bound)].value_counts()
        data.columns = ['count']
        print('Distribution:', data.to_string())
        print('Number of rows detected: {0}'.format(((column_copy < lower_bound) | (column_copy > upper_bound)).sum()))


def __check_values(column: pd.Series, values: list):
    selection = pd.Series(False, index=range(column.size), dtype='bool[pyarrow]')
    for value in values:
        selection = selection | (column == value)
    if column.loc[~selection].shape[0] > 0:
        print('Value check for column {0}'.format(column.name))
        data = column.loc[~selection].value_counts()
        data.columns = ['count']
        print('Distribution:', data.to_string())
        print('Number of rows detected: {0}'.format((~selection).sum()))


def __check_numeric(column: pd.Series):
    if column.loc[~column.str.isnumeric()].shape[0] > 0:
        print('Numeric check for column {0}'.format(column.name))
        data = column.loc[~column.str.isnumeric()].value_counts()
        data.columns = ['count']
        print('Distribution:', data.to_string())
        print('Number of rows detected: {0}'.format((~column.str.isnumeric()).sum()))


def __check_date_format(column: pd.Series, date_format: str):
    selection = pd.isnull(pd.to_datetime(column, format=date_format, errors='coerce'))
    if column.loc[selection].shape[0] > 0:
        print('DateTime check for column {0}'.format(column.name))
        data = column.loc[selection].value_counts()
        data.columns = ['count']
        print('Distribution:', data.to_string())
        print('Number of rows detected: {0}'.format(selection.sum()))


def __enforce_bounds(column: pd.Series, lower_bound: int, upper_bound: int) -> pd.Series:
    column_copy = pd.to_numeric(column)
    output = column.copy()
    if column[(column_copy < lower_bound) | (column_copy > upper_bound)].shape[0] > 0:
        print('Enforcing bounds check on column {0}'.format(column.name))
        print('Number of rows converted to NA: {0}'.format(((column_copy < lower_bound) |
                                                            (column_copy > upper_bound)).sum()))
        output = column.copy()
        if ((column_copy < lower_bound) | (column_copy > upper_bound)).sum() > 0:
            output.loc[((column_copy < lower_bound) | (column_copy > upper_bound))] = pd.NA
    return output


def __enforce_values(column: pd.Series, values: list) -> pd.Series:
    selection = pd.Series(False, index=range(column.size), dtype='bool[pyarrow]')
    for value in values:
        selection = selection | (column == value)
    output = column.copy()
    if column.loc[~selection].shape[0] > 0:
        print('Enforcing value check on column {0}'.format(column.name))
        print('Number of rows converted to NA: {0}'.format((~selection).sum()))
        if (~selection).sum() > 0:
            output.loc[~selection] = pd.NA
    return output


def __enforce_numeric(column: pd.Series) -> pd.Series:
    output = column.copy()
    if column.loc[~column.str.isnumeric()].shape[0] > 0:
        print('Enforcing numeric check on column {0}'.format(column.name))
        print('Number of rows converted to NA: {0}'.format((~column.str.isnumeric()).sum()))
        if (~column.str.isnumeric()).sum() > 0:
            output.loc[~column.str.isnumeric()] = pd.NA
    return output


def __enforce_date_format(column: pd.Series, date_format: str) -> pd.Series:
    output = column.copy()
    selection = pd.isnull(pd.to_datetime(column, format=date_format, errors='coerce'))
    if column.loc[selection].shape[0] > 0:
        print('Enforcing DateTime check on column {0}'.format(column.name))
        print('Number of rows converted to NA: {0}'.format(selection.sum()))
        if selection.sum() > 0:
            output.loc[selection] = pd.NA
    return output


def __change_value(column: pd.Series, input_value, output_value) -> pd.Series:
    selection = column == input_value
    output = column.copy()
    if selection.sum() > 0:
        print('Changing entries with value {0} in column {1}'.format(input_value, column.name))
        print('Number of rows converted to {0}: {1}'.format(output_value, selection.sum()))
        output.loc[selection].copy = output_value
    return output


def __remove_character(column: pd.Series, character: str):
    if column.str.contains(character).sum() > 0:
        print('Number of rows converted: {0}'.format(column.str.contains(character).sum()))
    return column.strip(character)


def __remove_missing(dataset: pd.DataFrame, column: str):
    if dataset[column].isnull().sum() > 0:
        print('Removing {0} rows with missing values in column {1}'.format(dataset[column].isnull().sum(), column))
    return dataset.drop(dataset[dataset[column].isnull()].index)
