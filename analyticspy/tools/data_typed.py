#!/usr/bin/env python
import numpy as np
from itertools import zip_longest
from .data import Table


class TypedTable(Table):
    """
    [summary]

    Args:
        Table ([type]): [description]
    """
    __slots__ = ["data"]

    def __init__(self, data=None, types=None):
        """
        [summary]

        Args:
            data ([type], optional): [description]. Defaults to None.
        """
        if data:
            if not types:
                raise AttributeError("There is no types list supplied.")
            self.data = np.array(
                list(zip_longest(*data.values())),
                dtype=types)
        else:
            self.data = np.array([])

    def new_column(self, name, data_type):
        """
        [summary]

        Args:
            name ([type]): [description]
        """
        arrays_list = [list(self.data[name]) for name in self.names]
        arrays_list.append([None] * self.length)
        types = self.data_types + [(name, data_type)]

        self.data = np.array(list(zip_longest(*arrays_list)), dtype=types)
