#!/usr/bin/env python
import numpy as np
from typing import List, Union
from itertools import zip_longest
from .data import Table


class TypedTable(Table):
    """Homogeneous, size-mutable, typed data structure."""

    __slots__ = ["data"]

    def __init__(self, data: dict = None, types: List[tuple] = None):
        if data:
            if not types:
                raise AttributeError("There is no types list supplied.")
            if isinstance(data, dict):
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

    def new_column(self, name: str, data_type: Union[type, str]):
        """Create a new table column of supplied data type.

        Args:
            name (str): name of the newly created table column.
            data_type (type, str): type of the newly created table column.
        """
        arrays_list = [list(self.data[name]) for name in self.names]
        arrays_list.append([None] * self.length)
        types = self.data_types + [(name, data_type)]

        self.data = np.array(list(zip_longest(*arrays_list)), dtype=types)
