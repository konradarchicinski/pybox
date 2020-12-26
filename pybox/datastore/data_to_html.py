#!/usr/bin/env python
from math import ceil, floor
from random import sample
from IPython.core.display import display, HTML


def show_table(data, data_map, rows_number, string_length=255):
    """Display the contents of the specified array in rendered html format.

    Args:
        data (list): array in the form of a nested list, where
            sublists are understood as columns of the array.
        data_map (list): list of sublists containing sequentially:
            the name of the column (str),
            the index representing the column position in the array (int),
            the data type appearing in the column (type).
        rows_number (int): number of elements to be displeyed.
        string_length (int, optional): maximal length of returned string, 
            if None entire string is printed. Defaults to 255.
    """
    data_length = len(data)

    html_table_fragment = _create_table_header(data_map)
    if data_length > rows_number:
        html_table_fragment = _create_table_body(
            html_table_fragment, data, data_map,
            range(ceil(rows_number / 2)), string_length)
        html_table_fragment = _add_dotted_row(html_table_fragment, data_map)
        html_table_fragment = _create_table_body(
            html_table_fragment, data, data_map,
            range(data_length - floor(rows_number / 2), data_length), string_length)
    else:
        html_table_fragment = _create_table_body(
            html_table_fragment, data, data_map, range(data_length), string_length)

    html_table_fragment = "".join([html_table_fragment, "</table>"])
    display(HTML(html_table_fragment))


def show_table_random(data, data_map, rows_number, string_length=255):
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
        string_length (int, optional): maximal length of returned string, 
            if None entire string is printed. Defaults to 255.
    """
    data_length = len(data)

    html_table_fragment = _create_table_header(data_map)
    if data_length > rows_number:
        html_table_fragment = _create_table_body(
            html_table_fragment, data, data_map,
            sample(range(0, data_length), rows_number), string_length)
    else:
        html_table_fragment = _create_table_body(
            html_table_fragment, data, data_map, range(data_length), string_length)

    html_table_fragment = "".join([html_table_fragment, "</table>"])
    display(HTML(html_table_fragment))


def show_table_head(data, data_map, rows_number, string_length=255):
    """Display the head of the specified array contents in rendered html format.

    Args:
        data (list): array in the form of a nested list, where
            sublists are understood as columns of the array.
        data_map (list): list of sublists containing sequentially:
            the name of the column (str),
            the index representing the column position in the array (int),
            the data type appearing in the column (type).
        rows_number (int): number of elements to be displeyed.
        string_length (int, optional): maximal length of returned string, 
            if None entire string is printed. Defaults to 255.
    """
    data_length = len(data)

    html_table_fragment = _create_table_header(data_map)
    if data_length > rows_number:
        html_table_fragment = _create_table_body(
            html_table_fragment, data, data_map, range(ceil(rows_number)), string_length)
        html_table_fragment = _add_dotted_row(html_table_fragment, data_map)
    else:
        html_table_fragment = _create_table_body(
            html_table_fragment, data, data_map, range(data_length), string_length)

    html_table_fragment = "".join([html_table_fragment, "</table>"])
    display(HTML(html_table_fragment))


def show_table_tail(data, data_map, rows_number, string_length=255):
    """Display the tail of the specified array contents in rendered html format.

    Args:
        data (list): array in the form of a nested list, where
            sublists are understood as columns of the array.
        data_map (list): list of sublists containing sequentially:
            the name of the column (str),
            the index representing the column position in the array (int),
            the data type appearing in the column (type).
        rows_number (int): number of elements to be displeyed.
        string_length (int, optional): maximal length of returned string, 
            if None entire string is printed. Defaults to 255.
    """
    data_length = len(data)

    html_table_fragment = _create_table_header(data_map)
    if data_length > rows_number:
        html_table_fragment = _add_dotted_row(html_table_fragment, data_map)
        html_table_fragment = _create_table_body(
            html_table_fragment, data, data_map,
            range(data_length - ceil(rows_number), data_length), string_length)
    else:
        html_table_fragment = _create_table_body(
            html_table_fragment, data, data_map, range(data_length), string_length)

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
    for column, dtype in data_map:
        html_table_fragment = "".join([
            html_table_fragment, "<th style='text-align:left;'><b><u>",
            str(column), "</u></b><br>DataType:", dtype.__name__, "</br></th>\n"
        ])
    html_table_fragment = "".join([html_table_fragment, "</tr>\n"])
    return html_table_fragment


def _create_table_body(html_table_fragment, data, data_map, iterator, string_length):
    """Returns a string containing the table body in html format.

    Args:
        html_table_fragment (str): fragment of the html table.
        data (list): array in the form of a nested list, where
            sublists are understood as columns of the array.
        data_map (list): list of sublists containing sequentially:
            the name of the column (str),
            the index representing the column position in the array (int),
            the data type appearing in the column (type).
        iterator (iterable): range based on which body will be created.
        string_length (int, optional): maximal length of returned string.
            Defaults to 255.
    """

    for index in iterator:
        html_table_fragment = "".join(
            [html_table_fragment, "<tr>\n<td>", str(index), "</td>\n"])
        for column_index, _ in enumerate(data_map):
            html_table_fragment = "".join([
                html_table_fragment, "<td style='text-align:left;'>",
                _cell_interior(data[index][column_index],
                               string_length), "</td>\n"
            ])
        html_table_fragment = "".join([html_table_fragment, "</tr>\n"])
    return html_table_fragment


def _cell_interior(raw_value, string_length):
    """Returns cell interior which is the provided data element,
    cut and transformed to proper form of a string.

    Args:
        raw_value (any): values of certain data element.
        string_length (int): maximal length of returned string.
    """
    cell_string = str(raw_value)
    if string_length is None or len(cell_string) <= string_length:
        return cell_string
    else:
        return f"{cell_string[:string_length]}..."


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
        html_table_fragment = "".join(
            [html_table_fragment, "<td style='text-align:left;'>...</td>\n"])
    html_table_fragment = "".join([html_table_fragment, "</tr>\n"])
    return html_table_fragment
