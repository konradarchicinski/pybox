#!/usr/bin/env python
from pybox.tools.date_helpers import to_date, to_datetime

import re
from sys import getsizeof
from itertools import chain
from bisect import bisect_left
from operator import itemgetter
from datetime import datetime, date


def recognize_type(vector):
    """Return recognized type of the data from the supplied list.

    Args:
        vector (list): vector from which type is to be recognized.
    """
    vector_types = {}
    for element in vector:
        try:
            vector_types[type(element)] += 1
        except KeyError:
            vector_types[type(element)] = 0
    recognized_type = max(
        vector_types.items(),
        key=itemgetter(1))[0]
    return recognized_type


def change_type(value, target_type):
    """Return certain value transformed to a given type.

    Args:
        value (any): value that type's going to be changed.
        target_type (type): target type of supplied values.
    """
    if value is None:
        return None
    elif isinstance(value, target_type):
        return value
    elif target_type == date:
        return to_date(value)
    elif target_type == datetime:
        return to_datetime(value)
    else:
        return target_type(value)


def binary_search(lookup_list, lookup_value, low_end=0, high_end=None):
    """Return index of the searched value in the supplied list, or None value
    if one does not occur in it.

    Args:
        lookup_list (list): vector searched.
        lookup_value (any): value searched.
        low_end (int, optional): index defining start of a search. Defaults to 0.
        high_end (int, optional): index defining end of a search. Defaults to None.
    """
    if lookup_value is None:
        return None
    if high_end is None:
        high_end = len(lookup_list)

    position = bisect_left(lookup_list, lookup_value, low_end, high_end)
    if (position != high_end and
        lookup_list[position] == lookup_value and
            type(lookup_list[position]) == type(lookup_value)):
        return position
    else:
        return None


def byte_size(measurable_object):
    """Returns the approximate memory footprint of supplied object.

    Args:
        measurable_object (any): object which size is to be measured.

    Method below is a modification of the code presented in:
    `https://code.activestate.com/recipes/577504/`.
    """
    all_handlers = {tuple: iter, list: iter, set: iter, frozenset: iter,
                    dict: lambda d: chain.from_iterable(d.items())}
    seen = set()
    default_size = getsizeof(0)

    def _sizeof(obj):
        if id(obj) in seen:
            return 0
        seen.add(id(obj))
        size = getsizeof(obj, default_size)
        for typ, handler in all_handlers.items():
            if isinstance(obj, typ):
                size += sum(map(_sizeof, handler(obj)))
                break
        return size
    return _sizeof(measurable_object)


def camel_to_snake_case(string):
    """Transform provided value from CamelCase format to snake_case.

    Args:

        string (str): string to be transformed.
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', string).lower()


def snake_to_camel_case(string):
    """Transform provided value from snake_case format to CamelCase.

    Args:

        string (str): string to be transformed.
    """
    return ''.join(component.title() for component in string.split('_'))
