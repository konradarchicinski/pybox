#!/usr/bin/env python
import operator
import numpy as np
import pyarrow as pa
from sys import getsizeof
from IPython.core.display import display, HTML


DATA_TYPES = [int, float, complex, bool, str, type(None)]


class DataTable:
    """Homogeneous, size-mutable, typed data structure."""

    __slots__ = ["_data", "_columns"]

    def __init__(self, data=None, names=None):
        self._data = list()
        self._columns = dict()

        if isinstance(data, np.ndarray):
            data = array_to_dict(data)

        if not names:
            names = data.keys()
        for key, value in zip(names, data.values()):
            self.add_column(key, value)

    def __getitem__(self, key):
        if isinstance(key, tuple):
            name, index = key
            return self._data[self._columns[name][0]][index]
        elif isinstance(key, str):
            return self._data[self._columns[key][0]]

    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            name, index = key
            if name not in self._columns.keys():
                self.add_column(name, [None] * self.length, type(value))
            try:
                self._data[self._columns[name][0]][index] = value
            except IndexError:
                self.remove_column(name)
                raise IndexError("list assignment index out of range")
        elif isinstance(key, str):
            value = self._align_length(value)
            if key not in self._columns.keys():
                self.add_column(key, value)
            else:
                self._data[self._columns[key][0]] = value

    def __str__(self):
        """Display a string representation for a particular Table."""
        return "".join([self.info, "\n"])

    def __repr__(self):
        """Display a html string representation for a particular Table."""
        html = "<table>\n<tr>\n<th></th>\n"

        for column, (_, datatype) in self._columns.items():
            html = f"{html}<th>{str(column)}<br>{datatype.__name__}</br></th>\n"
        html = "".join([html, "</tr>\n"])

        for idx in range(self.length):
            html = "".join([html, "<tr>\n<td>", str(idx), "</td>\n"])
            for column_idx, _ in self._columns.values():
                html = f"{html}<td>{str(self._data[column_idx][idx])}</td>\n"
            html = "".join([html, "</tr>\n"])
        html = "".join([html, "</table>"])

        display(HTML(html))
        return ""

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
        return list(self._columns.keys())

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
            "DataTable\n"
            f"(shape=({self.width}x{self.length}),"
            f"bytesize={getsizeof(self._data) + getsizeof(self._columns)})"
        )
        for name, dtype in self.datatypes.items():
            info = "".join([info, "\n", name, ": ", dtype.__name__])
        return info

    @property
    def datatypes(self):
        """Return dictionary of column names and their data types."""
        return {key: value[1] for key, value in self._columns.items()}

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
        self._columns[column_name] = (len(self._data) - 1, datatype)

    def remove_column(self, column_name):
        """Remove a column from the DataTable.

        Args:
            column_name (str): name of the column to be removed.
        """
        column_index = self._columns[column_name][0]
        del self._columns[column_name]
        del self._data[column_index]

        for column, (index, _) in self._columns.items():
            if index > column_index:
                self._columns[column][0] -= 1


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
