#!/usr/bin/env python
from pybox.tools.data.data_helpers import to_date

from datetime import datetime, date


class DataTableRow:
    """Auxiliary class of DataTable objects used for rows operations."""

    def __init__(self, instance, row_index):
        self.row_index = row_index
        self.instance = instance

    def __getitem__(self, key):
        if isinstance(key, str):
            column_index = self.instance.column_index(key)
            return self.instance._data[self.row_index][column_index]
        else:
            return self.instance._data[self.row_index]

    def __setitem__(self, key, value):
        if key not in self.instance.columns:
            self.instance.insert_column(key, [], datatype=type(value))
        column_index = self.instance.column_index(key)

        # Each assign value is transformed to the type of a given column.
        column_type = self.instance._data_map[column_index][1]

        if column_type in [date, datetime]:
            transformed_value = to_date(value, column_type)
        else:
            transformed_value = column_type(value)
        self.instance._data[self.row_index][column_index] = transformed_value

    def __repr__(self):
        row_content = {column_name: self.instance._data[self.row_index][column_index]
                       for column_name, column_index, _ in self.instance._data_map}
        return f"DataTableRow({row_content})"
