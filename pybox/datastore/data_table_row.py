#!/usr/bin/env python
from pybox.helpers.date import to_date, to_datetime

from datetime import datetime, date


class DataTableRow:
    """Auxiliary class of DataTable objects used for rows operations."""

    def __init__(self, instance, row_index):
        self.row_index = row_index
        self.instance = instance

        self.content = {
            column_name: self.instance._data[self.row_index][column_index]
            for column_index, (column_name,
                               _) in enumerate(self.instance._data_map)
        }

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

        if isinstance(value, column_type):
            transformed_value = value
        elif isinstance(column_type, date):
            transformed_value = to_date(value)
        elif isinstance(column_type, datetime):
            transformed_value = to_datetime(value)
        else:
            transformed_value = column_type(value)
        self.instance._data[self.row_index][column_index] = transformed_value

    def __repr__(self):
        return f"DataTableRow({self.content})"
