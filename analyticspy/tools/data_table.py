#!/usr/bin/env python
import operator
import numpy as np
import pyarrow as pa
from sys import getsizeof

from .array_to_html import (
    show_table, show_table_head, show_table_tail, show_table_random)


DATA_TYPES = [int, float, complex, bool, str, type(None)]


class DataTable:
    """Homogeneous, size-mutable, typed data structure."""

    __slots__ = ["_data", "_data_map"]

    def __init__(self, data=None, names=None):
        self._data = list()
        self._data_map = list()

        if isinstance(data, np.ndarray):
            data = array_to_dict(data)

        if not names:
            names = data.keys()
        for key, value in zip(names, data.values()):
            self.add_column(key, value)

    def __getitem__(self, key):
        if isinstance(key, tuple):
            name, index = key
            return self._data[self.column_index(name)][index]
        elif isinstance(key, str):
            return self._data[self.column_index(key)]

    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            name, index = key
            if name not in self.columns:
                self.add_column(name, [None] * self.length, type(value))
            try:
                self._data[self.column_index(name)][index] = value
            except IndexError:
                self.remove_column(name)
                raise IndexError("list assignment index out of range.")
        elif isinstance(key, str):
            value = self._align_length(value)
            if key not in self.columns:
                self.add_column(key, value)
            else:
                self._data[self.column_index(key)] = value

    def __str__(self):
        return self.info

    def __repr__(self):
        return "DataTable"

    def _recognize_type(self, column):
        """Return recognized type of the data from supplied column.

        Args:
            column (list): data stored in a form of list.
        """
        column_types = {}
        for cell in column:
            try:
                column_types[type(cell)] += 1
            except KeyError:
                column_types[type(cell)] = 0
        recognized_type = max(
            column_types.items(),
            key=operator.itemgetter(1))[0]

        return recognized_type

    def _align_length(self, value):
        """Align lenght of columns in entire DataTable.

        Args:
            value (list): list containg values of newly added column.
        """
        if not isinstance(value, list):
            value = [value]

        length_difference = len(value) - self.length
        if length_difference > 0:
            for column_idx in range(self.width):
                self._data[column_idx] += [None] * length_difference
            return value
        elif length_difference < 0:
            value += [None] * abs(length_difference)
            return value

    @property
    def columns(self):
        """Return a list of column names."""
        return [column_name for column_name, _, _ in self._data_map]

    @property
    def length(self):
        """Return length of a DataTable, in other words number of rows in it."""
        if self._data:
            return len(self._data[0])
        else:
            return 0

    @property
    def width(self):
        """Return width of a DataTable, in other words number of columns in it."""
        return len(self.columns)

    @property
    def info(self):
        """Return information about shape and bytesize of the DataTable."""
        info = (
            "DataTable"
            f"(shape={self.width}x{self.length},"
            f"bytesize={getsizeof(self._data) + getsizeof(self._data_map)})"
        )
        for name, dtype in self.datatypes.items():
            info = "".join([info, "\n", name, ": ", dtype.__name__])
        return info

    @property
    def datatypes(self):
        """Return a dictionary of column names and their data types."""
        return {column_name: dtype for column_name, _, dtype in self._data_map}

    @property
    def to_numpy_array(self):
        """Return numpy structured array object created from DataTable."""
        types_list = list(self.datatypes.items())
        numpy_array = np.array(self._data, dtype=types_list)
        return numpy_array

    @property
    def to_arrow_table(self):
        """Return arrow table object created from DataTable."""
        arrow_table = pa.Table.from_arrays(
            [pa.array(column) for column in self._data],
            names=self.columns
        )
        return arrow_table

    def display(self, rows_number=10):
        """Display the contents of the current DataTable in rendered html format.

        Args:
            rows_number (int, optional): number of rows/observations
                to be displeyed. Defaults to 10.
        """
        show_table(self._data, self._data_map, rows_number)

    def display_random(self, rows_number=10):
        """Display a random representation of the current DataTable contents
        in rendered html format.

        Args:
            rows_number (int, optional): number of rows/observations
                to be displeyed. Defaults to 10.
        """
        show_table_random(self._data, self._data_map, rows_number)

    def display_head(self, rows_number=10):
        """Display the head of the current DataTable contents in rendered html format.

        Args:
            rows_number (int, optional): number of rows/observations
                to be displeyed. Defaults to 10.
        """
        show_table_head(self._data, self._data_map, rows_number)

    def display_tail(self, rows_number=10):
        """Display the tail of the current DataTable contents in rendered html format.

        Args:
            rows_number (int, optional): number of rows/observations
                to be displeyed. Defaults to 10.
        """
        show_table_tail(self._data, self._data_map, rows_number)

    def column_index(self, column_name):
        """Return the index number of the specified column.

        Args:
            column_name (str): name of the specified column.
        """
        for element in self._data_map:
            if element[0] == column_name:
                return element[1]
        raise IndexError(
            f"A column called `{column_name}` has not been found in DataTable.")

    def rows_range(self, start=None, stop=None, step=None):
        """Return an iterator containing the range of DataTable indices.

        Args:
            start (int, optional): start of the range, included in the
                iteration. Defaults to None.
            stop (int, optional): end of the range, excluded from the
                iteration. Defaults to None.
            step (int, optional): steps between range elements. Defaults to None.
        """
        if not start:
            start = 0
        if not stop:
            stop = self.length
        if not step:
            step = 1
        return range(start, stop, step)

    def create_dummies(self, column_name):
        """Convert specified column containing categorical variables into
        several binarized ones.

        Args:
            column_name (str): name of the specified column.
        """
        levels = set(self._data[self.column_index(column_name)])
        for level in levels:
            level_column_name = "".join([column_name, str(level)])
            self.add_column(level_column_name, [None] * self.length, int)
            for idx in self.rows_range():
                if self._data[self.column_index(column_name)][idx] is None:
                    continue
                elif self._data[self.column_index(column_name)][idx] == level:
                    self._data[self.column_index(level_column_name)][idx] = 1
                else:
                    self._data[self.column_index(level_column_name)][idx] = 0

    def add_column(self, column_name, column_value, datatype=None):
        """Create a new column in the DataTable.

        Args:
            column_name (str): name of the newly created column.
            column_value (any): value of the newly created column.
            datatype (type, optional): data type of supplied data. Defaults to None.
        """
        if not datatype:
            datatype = self._recognize_type(column_value)
            if datatype not in DATA_TYPES and datatype.__module__ != "numpy":
                datatype = object
        self._data.append(column_value)
        self._data_map.append([column_name, len(self._data) - 1, datatype])

    def remove_column(self, column_name):
        """Remove a column from the DataTable.

        Args:
            column_name (str): name of the column to be removed.
        """
        for column_map in self._data_map:
            if column_map[0] == column_name:
                column_index = column_map[1]
                self._data_map.remove(column_map)
                break
        for column_map in self._data_map:
            if column_map[1] > column_index:
                column_map[1] -= 1

        del self._data[column_index]


def array_to_dict(array):
    """Return python dictionary created from an array. Array can be numpy.array
    object or a nested list with its subelements as rows.

    Args:
        array (list or numpy.array): array that will be transformed in dictionary.
    """
    data_dict = {
        column_name: column_value
        for column_name, column_value
        in zip(
            [f"Column{i}" for i in range(len(array[0]))],
            list(map(list, zip(*array)))
        )
    }
    return data_dict
