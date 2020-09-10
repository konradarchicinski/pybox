from tabulate import tabulate
from itertools import zip_longest
import numpy as np


class Table:
    """
    [summary]

    Returns:
        [type]: [description]
    """
    __slots__ = ["data"]

    def __init__(self, data=None, types=None):
        """
        [summary]

        Args:
            data ([type], optional): [description]. Defaults to None.
            types ([type], optional): [description]. Defaults to None.
        """
        if data:
            self.data = np.array(
                list(
                    zip_longest(
                        *data.values())),
                dtype=types)
        else:
            self.data = np.array([])

    @property
    def data_types(self):
        """
        [summary]

        Returns:
            [type]: [description]
        """
        return self.data.dtype.descr

    @property
    def length(self):
        """
        [summary]

        Returns:
            [type]: [description]
        """
        return len(self.data)

    @property
    def width(self):
        """
        [summary]

        Returns:
            [type]: [description]
        """
        return len(self.data_types)

    @property
    def names(self):
        """
        [summary]

        Returns:
            [type]: [description]
        """
        return list(self.data.dtype.names)

    @property
    def rows_range(self):
        """
        [summary]

        Returns:
            [type]: [description]
        """
        return range(self.length)

    def __getitem__(self, selector):
        """
        [summary]

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
        """
        [summary]

        Args:
            selector ([type]): [description]
            value ([type]): [description]
        """
        if isinstance(selector, tuple):
            # TODO write code for handling slices, itnegers strings and more.
            name, index = selector
            if name not in self.names:
                self._new_column(name)
            self.data[name][index] = value
        elif isinstance(selector, str):
            if selector not in self.names:
                self._new_column(selector)
            self._align_length(value)
            self.data[selector] = value

    def __str__(self):
        """
        [summary]

        Returns:
            [type]: [description]
        """
        return tabulate(
            self.data,
            headers="keys",
            showindex="always",
            tablefmt="github",
            disable_numparse=True
        )

    def _align_length(self, value):
        """e
        [summary]

        Args:
            value ([type]): [description]
        """
        length_difference = len(value) - self.length
        if length_difference > 0:
            for _ in range(1, length_difference + 1):
                self.data.resize(self.length + 1)
                self.data[-1] = tuple([None] * self.width)

    def _new_column(self, name, data_type="O"):
        """
        [summary]

        Args:
            name ([type]): [description]
            data_type (str, optional): [description]. Defaults to "O".
        """
        arrays_list = [list(self.data[name]) for name in self.names]
        arrays_list.append([None] * self.length)
        types = self.data_types + [(name, data_type)]

        self.data = np.array(list(zip_longest(*arrays_list)), dtype=types)
