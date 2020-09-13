#!/usr/bin/env python
import numpy as np
import pyarrow as pa
from sys import getsizeof
from tabulate import tabulate
from itertools import zip_longest
from IPython.core.display import display, HTML


class Table:
    """[summary]

    Returns:
        [type]: [description]
    """
    __slots__ = ["data"]

    def __init__(self, data=None):
        """[summary]

        Args:
            data ([type], optional): [description]. Defaults to None.
        """
        if data:
            types = [(name, "O") for name in data.keys()]
            self.data = np.array(
                list(zip_longest(*data.values())),
                dtype=types)
        else:
            self.data = np.array([])

    def __str__(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        print(self.info, "\n")
        return tabulate(
            self.data,
            headers="keys",
            showindex="always",
            tablefmt="github",
            disable_numparse=True
        )

    def __repr__(self):
        """[summary]

        Returns:
            [type]: [description]
        """
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

    def __getitem__(self, selector):
        """[summary]

        Args:
            selector ([type]): [description]

        Returns:
            [type]: [description]
        """
        if isinstance(selector, tuple):
            # TODO write code for handling slices, itnegers strings and more.
            name, index = selector
            return self.data[name][index]
        elif isinstance(selector, str):
            return self.data[selector]

    def __setitem__(self, selector, value):
        """[summary]

        Args:
            selector ([type]): [description]
            value ([type]): [description]
        """
        if isinstance(selector, tuple):
            # TODO write code for handling slices, itnegers strings and more.
            name, index = selector
            if name not in self.names:
                self.new_column(name)
            self.data[name][index] = value
        elif isinstance(selector, str):
            if selector not in self.names:
                self.new_column(selector)
            value = self.value_to_list(value)
            self.align_length(value)
            self.data[selector] = value

    @property
    def data_types(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        if self.data.size == 0:
            return list()
        else:
            return self.data.dtype.descr

    @property
    def length(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return len(self.data)

    @property
    def width(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return len(self.data_types)

    @property
    def names(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        if self.data.size == 0:
            return list()
        else:
            return list(self.data.dtype.names)

    @property
    def to_arrow(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        arrow_table = pa.Table.from_arrays(
            [pa.array(self.data[name]) for name in self.names],
            names=self.names
        )
        return arrow_table

    @property
    def info(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        info = (
            "Table("
            f"shape=({self.width}x{self.length}),"
            f"bytesize={getsizeof(self.data)}"
            ")"
        )
        return info

    def rows(self, start=None, stop=None):
        """[summary]

        Args:
            start ([type], optional): [description]. Defaults to None.
            stop ([type], optional): [description]. Defaults to None.

        Returns:
            [type]: [description]
        """
        if not start:
            start = 0
        if not stop:
            stop = self.length
        return (row for row in self.data[start:stop])

    def indices(self, start=None, stop=None, step=None):
        """[summary]

        Args:
            start ([type], optional): [description]. Defaults to None.
            stop ([type], optional): [description]. Defaults to None.
            step ([type], optional): [description]. Defaults to None.

        Returns:
            [type]: [description]
        """
        if not start:
            start = 0
        if not stop:
            stop = self.length
        if not step:
            step = 1
        return range(start, stop, step)

    def value_to_list(self, value):
        """[summary]

        Args:
            value ([type]): [description]

        Returns:
            [type]: [description]
        """
        if not isinstance(value, list):
            value = [value]
        return value

    def align_length(self, value):
        """[summary]

        Args:
            value ([type]): [description]
        """
        length_difference = len(value) - self.length
        if length_difference > 0:
            for _ in range(1, length_difference + 1):
                self.data.resize(self.length + 1)
                self.data[-1] = tuple([None] * self.width)

    def new_column(self, name):
        """[summary]

        Args:
            name ([type]): [description]
        """
        arrays_list = [list(self.data[name]) for name in self.names]
        arrays_list.append([None] * self.length)
        types = self.data_types + [(name, "O")]

        self.data = np.array(list(zip_longest(*arrays_list)), dtype=types)
