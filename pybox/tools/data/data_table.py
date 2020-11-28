#!/usr/bin/env python
import re
import pybox.tools.data.data_helpers as btddh
import pybox.tools.data.data_to_html as btddth
import pybox.tools.data.data_table_row as btddtr

from copy import deepcopy
from datetime import date, datetime


DATA_TYPES = [int, float, complex, bool, str, type(None), date, datetime]


class DataTable:
    """Data structure with typed columns and mutable entities."""

    __slots__ = ["_data", "_data_map"]

    def __init__(self, data=None, names=None, dtypes=None):
        self._data = list()
        self._data_map = list()

        if isinstance(data, dict):
            self._data = list(map(list, zip(*data.values())))
            if not names:
                names = list(data.keys())
        elif type(data).__module__ == "numpy":
            self._data = data.tolist()

        if self.length == 0 or data is None:
            if names and dtypes:
                for name, dtype in zip(names, dtypes):
                    self._data_map.append([name, dtype])
            else:
                raise ValueError(
                    "If data not supplied, both `names` and `dtypes` must not be none.")
        else:
            for column_idx in range(len(self._data[0])):
                self._data_map.append([
                    names[column_idx],
                    btddh.recognize_type((
                        self._data[row_idx][column_idx]
                        for row_idx in range(len(self._data))
                    ))
                ])

    def __getitem__(self, key):
        if isinstance(key, tuple):
            name, index = key
            return self._data[index][self.column_index(name)]
        elif isinstance(key, str):
            return [self._data[index][self.column_index(key)]
                    for index in range(self.length)]

    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            name, idx = key
            if name not in self.columns:
                self.insert_column(name, [None] * self.length, type(value))
            try:
                self._data[idx][self.column_index(name)] = value
            except IndexError:
                self.remove_columns([name])
                raise IndexError("List assignment index out of range.")
        elif isinstance(key, str):
            if key not in self.columns:
                self.insert_column(key, [None] * self.length, type(value))

            if isinstance(value, list) or isinstance(value, tuple):
                datatype = btddh.recognize_type(value)
                for index, element in enumerate(value):
                    self._data[index][self.column_index(key)] = (
                        btddh.change_type(element, datatype)
                    )
            else:
                self._data[0][self.column_index(key)] = value
                for idx in range(1, self.length):
                    self._data[idx][self.column_index(key)] = None
                self._data_map[self.column_index(key)][1] = object
        else:
            raise ValueError(
                "The wrong key type was supplied, it should be `str`",
                "representing name of the column or \npair of `str` ",
                "representing a column and `int` representing certain ",
                "row splitted by comma. ")

    def __iter__(self):
        return (btddtr.DataTableRow(self, row) for row in range(self.length))

    def __str__(self):
        return self.info

    def __repr__(self):
        return f"DataTable({self.width}x{self.length})"

    @property
    def copy(self):
        """Return deepcopy of the DataTable."""
        return deepcopy(self)

    @property
    def length(self):
        """Return length of the DataTable, in other words number of rows in it."""
        return len(self._data)

    @property
    def width(self):
        """Return width of the DataTable, in other words number of columns in it."""
        return len(self._data_map)

    @property
    def columns(self):
        """Return a list of column names."""
        return [column_name for column_name, _ in self._data_map]

    @property
    def datatypes(self):
        """Return a dictionary of column names and their data types."""
        return {column_name: dtype for column_name, dtype in self._data_map}

    @property
    def bytesize(self):
        """Returns the approximate memory DataTable footprint."""
        return btddh.byte_size(self._data) + btddh.byte_size(self._data_map)

    @property
    def info(self):
        """Return information about shape and bytesize of the DataTable."""
        info = (
            "DataTable"
            f"(shape={self.width}x{self.length},"
            f"bytesize={self.bytesize})"
        )
        for name, dtype in self.datatypes.items():
            info = "".join([info, "\n", name, ": ", dtype.__name__])
        return info

    @property
    def to_numpy_array(self):
        """Return numpy structured array object created from the DataTable."""
        from numpy import array

        types_list = list(self.datatypes.items())
        numpy_array = array(self._data, dtype=types_list)
        return numpy_array

    @property
    def to_arrow_table(self):
        """Return arrow table object created from the DataTable."""
        from pyarrow import Table, array

        arrow_table = Table.from_arrays(
            [array(column) for column in list(map(list, zip(*self._data)))],
            names=self.columns
        )
        return arrow_table

    def to_parquet(self, file_name, directory):
        """Store `DataTable` in the parquet format file.

        Args:
            file_name (str): name under which data structure will be saved.
            directory (str): folder structure in which DataTable is to be saved.
        """
        from pybox.tools.data.data_flow import table_to_parquet
        table_to_parquet(self, file_name, directory)

    def display(self, rows_number=10, display_type=None):
        """Display the contents of the current DataTable in rendered html format.

        Args:
            rows_number (int, optional): number of rows/observations
                to be displeyed. Defaults to 10.
            display_type (str, optional): type of displayed DataTable form.
                If `random` display a random representation.
                If `head` display heading elements.
                If `tail` display tail elements.
                Otherwise display entire or first heading and tail elements.
                Defaults to None.
        """
        if not display_type:
            btddth.show_table(self._data, self._data_map, rows_number)
        elif display_type.lower() == "random":
            btddth.show_table_random(self._data, self._data_map, rows_number)
        elif display_type.lower() == "head":
            btddth.show_table_head(self._data, self._data_map, rows_number)
        elif display_type.lower() == "tail":
            btddth.show_table_tail(self._data, self._data_map, rows_number)

    def column_index(self, column_name):
        """Return the index number of the specified column.

        Args:
            column_name (str): name of the specified column.
        """
        for column_index, element in enumerate(self._data_map):
            if element[0] == column_name:
                return column_index
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

    def insert_column(self, column_name, column_values,
                      datatype=None, column_index=None):
        """Create a new column in the DataTable.

        Args:
            column_name (str): name of the newly created column.
            column_value (any): value of the newly created column.
            datatype (type, optional): data type of supplied data. Defaults to None.
        """
        if column_name in self.columns:
            raise NameError("Supplied column name already exists.")

        length_difference = self.length - len(column_values)
        if length_difference > 0:
            column_values.extend([None] * length_difference)
        elif length_difference < 0:
            for _ in range(abs(length_difference)):
                self._data.append([None] * self.width)

        if not datatype:
            datatype = btddh.recognize_type(column_values)
            if datatype not in DATA_TYPES and datatype.__module__ != "numpy":
                raise ValueError(
                    "Wrong type of data supplied, it must be one of: ",
                    f"{','.join([str(dtype) for dtype in DATA_TYPES])} or numpy.array.")

        if column_index is None:
            column_index = self.length
        for idx in range(self.length):
            self._data[idx].insert(
                column_index,
                btddh.change_type(column_values[idx], datatype))

        self._data_map.insert(column_index, [column_name, datatype])

    def separate_columns(self, column_names):
        """Create copy of a DataTable only with supplied columns.

        Args:
            column_names (list): column names to be separated.
        """
        data_copy = self.copy
        columns_to_remove = [
            col for col in self.columns if col not in column_names]
        data_copy.remove_columns(columns_to_remove)
        return data_copy

    def remove_columns(self, column_names):
        """Remove selected columns from the DataTable.

        Args:
            column_names (list): column names to be removed.
        """
        for column_name in column_names:
            for idx, column_map in enumerate(self._data_map):
                if column_map[0] == column_name:
                    self._data_map.remove(column_map)
                    for row_idx in range(self.length):
                        del self._data[row_idx][idx]
                    break

    def insert_row(self, row_values, row_index=None):
        """Insert a row into the DataTable object.

        Args:
            row_values (array-like): list of values to be inserted.
            row_index (int, optional): number of row. Defaults to length of DateTable.
        """
        if len(row_values) != self.width:
            raise ValueError(
                "Supplied row needs to be the same width as DataTable",
                f", which is {self.width}.")
        for idx, value in enumerate(row_values):
            row_values[idx] = btddh.change_type(value, self._data_map[idx][1])

        if row_index is None:
            row_index = self.length
        self._data.insert(row_index, row_values)

    def rename_columns(self, old_names, new_names):
        """Rename selected column names.

        Args:
            old_names (list): column names to be renamed.
            new_names (list): new column names.
        """
        columns_dict = dict(zip(old_names, new_names))
        for column_map in self._data_map:
            if column_map[0] in columns_dict.keys():
                column_map[0] = columns_dict[column_map[0]]

    def sort(self, column_names, reverse_order=False, sort_function=None):
        """Sort in place the DataTable based on the supplied column name values.

        Args:
            column_names (list): strings representing column names based on
                which values performed will be sorting.
            reverse_order (bool, optional): value that indicates whether the
                sort should be performed in reverse order. Defaults to False.
            sort_function (function, optional): function that allows to pass
                additional commands to the sorter. Defaults to None.
        """
        other_columns = [column for column, _ in self._data_map
                         if column not in column_names]
        data_to_sort = []
        new_data_map = []
        for column in column_names + other_columns:
            data_to_sort.append([self._data[index][self.column_index(column)]
                                 for index in range(self.length)])
            new_data_map.append([column, self.datatypes[column]])

        data_to_sort = list(map(list, zip(*data_to_sort)))
        self._data_map = new_data_map
        self._data = sorted(
            data_to_sort,
            key=sort_function,
            reverse=reverse_order)

    def filter(self, filtering_function):
        """Filter in place the DataTable rows. Filtering is performed on rows
        which meet the condition set in the filtering function.

        Args:
            filtering_function (function): used to select rows meeting the
                condition set in the function.
        """
        for index, row in reversed(list(enumerate(self))):
            if not filtering_function(row):
                del self._data[index]

    def create_dummies(self, column_name, remove_in_place=True):
        """Convert specified column containing categorical variables into
        several binarized ones.

        Args:
            column_name (str): name of the specified column.
            remove_in_place (bool, optional): if True after creating new dummy
                columns original column is deleted. Defaults to True.
        """
        levels = set(self[column_name])
        levels.discard(None)
        levels = sorted(levels, reverse=True)
        main_column_index = self.column_index(column_name)

        for level in levels:
            level_column_name = "".join([column_name, str(level)])
            self.insert_column(
                level_column_name,
                [None] * self.length,
                datatype=int,
                column_index=main_column_index + 1)
            for idx in self.rows_range():
                if self._data[idx][main_column_index] is None:
                    continue
                elif self._data[idx][main_column_index] == level:
                    self._data[idx][self.column_index(level_column_name)] = 1
                else:
                    self._data[idx][self.column_index(level_column_name)] = 0
        if remove_in_place:
            self.remove_columns([column_name])

    def concatenate(self, outer_data, inner_columns=None, outer_columns=None):
        """Concatenate the DataTable with an external one.

        Args:
            outer_data (DataTable): external DataTable to be concatenated.
            inner_columns (list, optional): strings representing inner columns
                to which new data is to be concatenated. Defaults to None.
            outer_columns (list, optional): strings representing outer columns
                that are to be concatenated. Defaults to None.
        """
        if inner_columns is None:
            inner_columns = self.columns
        if outer_columns is None:
            outer_columns = outer_data.columns

        columns_dict = dict(zip(inner_columns, outer_columns))
        for row in outer_data:
            row_to_append = []
            for column in self.columns:
                if column in columns_dict.keys():
                    row_to_append.append(row[columns_dict[column]])
                else:
                    row_to_append.append(None)
            self._data.append(row_to_append)

    def join(self, outer_data, inner_column, outer_column):
        """Join the DataTable with an external one.

        Args:
            outer_data (DataTable): external DataTable to be join with.
            inner_column (str): name of the column in the inner DataTable,
                based on which join is to be performed
            outer_column (str): name of the column in the outer DataTable,
                based on which join is to be performed
        """
        outer_data_copy = outer_data.copy
        outer_data_copy.rename_columns([outer_column], ["OuterMainColumn"])
        outer_data_copy.sort(["OuterMainColumn"])
        outer_data_width = outer_data_copy.width
        self._data_map.extend(outer_data_copy._data_map)

        for idx in self.rows_range():
            position = btddh.binary_search(
                outer_data_copy["OuterMainColumn"], self[inner_column, idx])
            if position is None:
                self._data[idx].extend([None] * outer_data_width)
            else:
                self._data[idx].extend(outer_data_copy._data[position])
        self.remove_columns(["OuterMainColumn"])

    def apply(self, column_name, function):
        """Apply supplied transformation on all values in the selected column.

        Args:
            column_name (str): name of the column on which the transformation
                is to be performed.
            function (function): describes the transformations that are to be
                performed on the selected column.
        """
        column_index = self.column_index(column_name)
        for index in self.rows_range():
            self._data[index][column_index] = function(
                self._data[index][column_index])
