#!/usr/bin/env python
from math import ceil, floor
from random import sample
from IPython.core.display import display, HTML


def show_table(data, data_map, rows_number):
    """Display the contents of the specified array in rendered html format.

    Args:
        data (list): array in the form of a nested list, where
            sublists are understood as columns of the array.
        data_map (list): list of sublists containing sequentially:
            the name of the column (str),
            the index representing the column position in the array (int),
            the data type appearing in the column (type).
        rows_number (int): number of elements to be displeyed.
    """
    html_table_fragment = _create_table_header(data_map)
    html_table_fragment = _create_table_body(
        html_table_fragment, data, data_map, range(ceil(rows_number / 2)))
    html_table_fragment = _add_dotted_row(html_table_fragment, data_map)
    data_length = len(data[0])
    html_table_fragment = _create_table_body(
        html_table_fragment, data, data_map,
        range(data_length - floor(rows_number / 2), data_length))
    html_table_fragment = "".join([html_table_fragment, "</table>"])
    display(HTML(html_table_fragment))


def show_table_random(data, data_map, rows_number):
    """Display a random representation of the specified array contents
    in rendered html format.

    Args:
        data (list): array in the form of a nested list, where
            sublists are understood as columns of the array.
        data_map (list): list of sublists containing sequentially:
            the name of the column (str),
            the index representing the column position in the array (int),
            the data type appearing in the column (type).
        rows_number (int): number of elements to be displeyed.
    """
    html_table_fragment = _create_table_header(data_map)
    html_table_fragment = _create_table_body(
        html_table_fragment, data, data_map,
        sample(range(0, len(data[0])), rows_number))
    html_table_fragment = "".join([html_table_fragment, "</table>"])
    display(HTML(html_table_fragment))


def show_table_head(data, data_map, rows_number):
    """Display the head of the specified array contents in rendered html format.

    Args:
        data (list): array in the form of a nested list, where
            sublists are understood as columns of the array.
        data_map (list): list of sublists containing sequentially:
            the name of the column (str),
            the index representing the column position in the array (int),
            the data type appearing in the column (type).
        rows_number (int): number of elements to be displeyed.
    """
    html_table_fragment = _create_table_header(data_map)
    html_table_fragment = _create_table_body(
        html_table_fragment, data, data_map, range(ceil(rows_number)))
    html_table_fragment = _add_dotted_row(html_table_fragment, data_map)
    html_table_fragment = "".join([html_table_fragment, "</table>"])
    display(HTML(html_table_fragment))


def show_table_tail(data, data_map, rows_number):
    """Display the tail of the specified array contents in rendered html format.

    Args:
        data (list): array in the form of a nested list, where
            sublists are understood as columns of the array.
        data_map (list): list of sublists containing sequentially:
            the name of the column (str),
            the index representing the column position in the array (int),
            the data type appearing in the column (type).
        rows_number (int): number of elements to be displeyed.
    """
    html_table_fragment = _create_table_header(data_map)
    html_table_fragment = _add_dotted_row(html_table_fragment, data_map)

    data_length = len(data[0])
    html_table_fragment = _create_table_body(
        html_table_fragment, data, data_map,
        range(data_length - ceil(rows_number), data_length))
    html_table_fragment = "".join([html_table_fragment, "</table>"])
    display(HTML(html_table_fragment))


def _create_table_header(data_map):
    """Return a string containing the table header in html format.

    Args:
        data_map (list): list of sublists containing sequentially:
            the name of the column (str),
            the index representing the column position in the array (int),
            the data type appearing in the column (type).
    """
    html_table_fragment = "<table>\n<tr>\n<th><br></br><br></br>Index</th>\n"
    for column, _, dtype in data_map:
        html_table_fragment = "".join([
            html_table_fragment, "<th><b><u>", str(column),
            "</u></b><br>DataType:", dtype.__name__, "</br></th>\n"
        ])
    html_table_fragment = "".join([html_table_fragment, "</tr>\n"])
    return html_table_fragment


def _create_table_body(html_table_fragment, data, data_map, iterator):
    """Return a string containing the table body in html format.

    Args:
        html_table_fragment (str): fragment of the html table.
        data (list): array in the form of a nested list, where
            sublists are understood as columns of the array.
        data_map (list): list of sublists containing sequentially:
            the name of the column (str),
            the index representing the column position in the array (int),
            the data type appearing in the column (type).
        iterator (iterable): [description]
    """
    for index in iterator:
        html_table_fragment = "".join(
            [html_table_fragment, "<tr>\n<td>", str(index), "</td>\n"])
        for column, column_index, _ in data_map:
            html_table_fragment = "".join([
                html_table_fragment, "<td>",
                str(data[column_index][index]), "</td>\n"
            ])
        html_table_fragment = "".join([html_table_fragment, "</tr>\n"])
    return html_table_fragment


def _add_dotted_row(html_table_fragment, data_map):
    """Return a string containing the table row in html format with dotted cells.

    Args:
        html_table_fragment (str): fragment of the html table.
        data_map (list): list of sublists containing sequentially:
            the name of the column (str),
            the index representing the column position in the array (int),
            the data type appearing in the column (type).
    """
    html_table_fragment = "".join(
        [html_table_fragment, "<tr>\n<td>...</td>\n"])
    for _ in data_map:
        html_table_fragment = "".join([html_table_fragment, "<td>...</td>\n"])
    html_table_fragment = "".join([html_table_fragment, "</tr>\n"])
    return html_table_fragment
