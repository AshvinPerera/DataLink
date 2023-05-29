import pandas as pd
import pyarrow as pa

from DataLink.DataTool.Filter import filter_data, FilterInstruction


def replace_value(
        dataframe: pd.DataFrame,
        main_filter: FilterInstruction,
        replace_with: Any,
        additional_filter: list = None
) -> pd.DataFrame:
    if additional_filter is None:
        selection = filter_data(dataframe, [main_filter])
    else:
        additional_filter.append(main_filter)
        selection = filter_data(dataframe, additional_filter)
    dataframe.loc[selection, columns] = replace_with
    return dataframe
