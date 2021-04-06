#!/usr/bin/env python


def create_datatable_header(data_map):
    """Returns a string containing the table header in html format.

    Args:
        data_map (list): list of sublists containing sequentially:
            the name of the column (str),
            the index representing the column position in the array (int),
            the data type appearing in the column (type).
    """
    cell_template = ("<th scope='col'>\n"
                     "<b><u>{}</u></b>\n"
                     "<br>DataType:{}</br>\n"
                     "</th>\n")
    cells_list = list()
    for column, dtype in data_map:
        cells_list.append(cell_template.format(str(column), dtype.__name__))
    return ("<thead>\n"
            "<tr>\n"
            "<th scope='col' style='text-align:center;'>#</th>\n"
            f"{''.join(cells_list)}"
            "</tr>\n"
            "</thead>\n")
