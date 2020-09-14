#!/usr/bin/env python
import numpy as np
import pyarrow as pa
from sys import getsizeof
from tabulate import tabulate
from itertools import zip_longest
from IPython.core.display import display, HTML
from typing import List, Union, Any, Iterator, NewType

ArrowTable = NewType("ArrowTable", pa.Table)


class Table:
    """Heterogeneous, size-mutable data structure."""

    __slots__ = ["data"]

    def __init__(self, data: dict = None):
        # TODO add table creation also from different types than dict.
        if data:
            if isinstance(data, dict):
                types = [(name, "O") for name in data.keys()]
                self.data = np.array(
                    list(zip_longest(*data.values())),
                    dtype=types)
            else:
                raise TypeError(
                    f"{type(data)}"
                    "is an unsupported type for creating a Table object."
                )
        else:
            self.data = np.array([])

    def __str__(self) -> str:
        """Display a string representation for a particular Table."""
        print(self.info, "\n")
        return tabulate(
            self.data,
            headers="keys",
            showindex="always",
            tablefmt="github",
            disable_numparse=True
        )

    def __repr__(self) -> str:
        """Display a html string representation for a particular Table."""
        html = "<table>\n<tr>\n<th></th>\n"

        for column, type_value in self.data.dtype.fields.items():
            html = (
                f"{html}<th>{str(column)}<br>{str(type_value[0])}</br></th>\n"
            )
        html = "".join([html, "</tr>\n"])

        for idx, row in enumerate(self.data):
            html = "".join([html, "<tr>\n<td>", str(idx), "</td>\n"])
            for elem in row:
                html = f"{html}<td>{str(elem)}</td>\n"
            html = "".join([html, "</tr>\n"])
        html = "".join([html, "</table>"])

        display(HTML(html))
        return self.info

    def __getitem__(self, selector: Union[tuple, str]):
        if isinstance(selector, tuple):
            # TODO write code for handling slices, itnegers strings and more.
            name, index = selector
            return self.data[name][index]
        elif isinstance(selector, str):
            return self.data[selector]

    def __setitem__(self, selector: Union[tuple, str], value: Any):
        if isinstance(selector, tuple):
            # TODO write code for handling slices, itnegers strings and more.
            name, index = selector
            if name not in self.names:
                self.new_column(name)
            self.data[name][index] = value
        elif isinstance(selector, str):
            if selector not in self.names:
                self.new_column(selector)
            value = self._value_to_list(value)
            self._align_length(value)
            self.data[selector] = value

    def _value_to_list(self, value: list) -> list:
        """Return a list values of supplied column in a list type.

        Args:
            value (list): list containg values of newly added column.
        """
        if not isinstance(value, list):
            value = [value]
        return value

    def _align_length(self, value: list):
        """Align lenght of columns in entire table.

        Args:
            value (list): list containg values of newly added column.
        """
        length_difference = len(value) - self.length
        if length_difference > 0:
            for _ in range(1, length_difference + 1):
                self.data.resize(self.length + 1)
                self.data[-1] = tuple([None] * self.width)

    @property
    def data_types(self) -> List[tuple]:
        """Return list of column names wiht their data types."""
        if self.data.size == 0:
            return list()
        else:
            return self.data.dtype.descr

    @property
    def length(self) -> int:
        """Return length of a Table, in other words number of rows in it."""
        return len(self.data)

    @property
    def width(self) -> int:
        """Return width of a Table, in other words number of columns in it."""
        return len(self.data_types)

    @property
    def names(self) -> List[str]:
        """Return list of column names."""
        if self.data.size == 0:
            return list()
        else:
            return list(self.data.dtype.names)

    @property
    def to_arrow(self) -> ArrowTable:
        """Return arrow table object from Table."""
        arrow_table = pa.Table.from_arrays(
            [pa.array(self.data[name]) for name in self.names],
            names=self.names
        )
        return arrow_table

    @property
    def info(self) -> str:
        """Return information about shape and bytesize of the Table"""
        info = (
            "Table("
            f"shape=({self.width}x{self.length}),"
            f"bytesize={getsizeof(self.data)}"
            ")"
        )
        return info

    def rows(self, start: int = None, stop: int = None) -> Iterator[tuple]:
        """Return an iterator containing the range of Table rows in tuples.

        Args:
            start (int, optional): first row of the range, included in the
                iteration. Defaults to None.
            stop (int, optional): last row of the range, excluded from  the
                iteration. Defaults to None.
        """
        if not start:
            start = 0
        if not stop:
            stop = self.length
        return (row for row in self.data[start:stop])

    def indices(self, start: int = None, stop: int = None,
                step: int = None) -> Iterator[int]:
        """Return an iterator containing the range of Table indices.

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

    def new_column(self, name: str):
        """Create a new table column.

        Args:
            name (str): name of the newly created table column.
        """
        arrays_list = [list(self.data[name]) for name in self.names]
        arrays_list.append([None] * self.length)
        types = self.data_types + [(name, "O")]

        self.data = np.array(list(zip_longest(*arrays_list)), dtype=types)
