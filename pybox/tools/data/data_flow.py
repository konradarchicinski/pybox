#!/usr/bin/env python
from pybox.GLOBALS import GLOBAL_DATA_PATH
import pybox.tools.data.data_table as btddt
import pybox.tools.database as btdb

import pyarrow.parquet as pq
import numpy as np
import requests
import xmltodict


def table_from_sqlite(table_name, database, database_directory=None):
    """Load SQLite table and return it as the `DataTable` object.

    Args:

        table_name (str): name of the SQLite table which will be loaded.
        database (str): name of the SQLite database which will be used.
        database_directory (str, optional): directory in which used SQLite
            database is stored. Defaults to None.
    """
    if database_directory:
        conn = btdb.create_connection(database, database_directory)
    else:
        conn = btdb.create_connection(database)
    with conn:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM '{table_name}'")
        data = cur.fetchall()
        cur.execute(f"PRAGMA TABLE_INFO('{table_name}')")
        info = cur.fetchall()

    data_columns = [column[1] for column in info]

    return btddt.DataTable(np.array(data), names=data_columns)


def table_to_parquet(table, file_name, directory=GLOBAL_DATA_PATH):
    """Store selected `DataTable` object in the parquet format file. Function
    works based on the `PyArrow` module, firstly transforming `DataTable` into
    Arrow object and afterwards writing it as a parquet file.

    Args:

        table (DataTable): data structure that will be saved.
        file_name (str): name under which data structure will be saved.
        directory (str, optional): string containing directory in which
            DataTable is going to be saved. Defaults to GLOBAL_DATA_PATH.
    """
    file_path = f"{directory}\\{file_name}.parquet"
    arrow_table = table.to_arrow_table
    pq.write_table(arrow_table, file_path)


def table_from_parquet(file_name, directory=GLOBAL_DATA_PATH):
    """Load parquet format file as the `DataTable` object. Function works based
    on the `PyArrow` module, firstly reading file and storing it as an Arrow
    object and afterwards transforming it into `DataTable`.

    Args:

        file_name (str): name of parquet file which will be loaded.
        directory (str, optional): string containing directory in which parquet
            file is stored. Defaults to GLOBAL_DATA_PATH.

    Returns:
        DataTable: loaded data in a form of DataTable object.
    """
    file_path = f"{directory}\\{file_name}.parquet"
    arrow_table = pq.read_table(file_path)
    return btddt.DataTable(arrow_table.to_pydict())


def dict_from_xml(file_name, branch=None):
    """Return dictionary from the provided xml file.

    Args:

        file_name (str): name of the local xml file or web it's web address.
        branch (str, optional): path to the dict element which should be returned.
            The path should be given in an XPath-based form that looks like:

                 `/dict_key/child_of_dict_key/child_of_child_of_dict_key/...` 
    """
    text = read_text(file_name)
    xml_dict = xmltodict.parse(text)

    if branch is not None:
        dict_keys = branch.split("/")[1:]
        for key in dict_keys:
            xml_dict = xml_dict[key]
    return xml_dict


def read_text(file_name, decoding="utf-8"):
    """Return the string obtained from the read text file. Provided
    file name can be a local path or an web address.

    Args:
        file_name (str): localization of the file to be read.
        decoding (str, optional): decoding type. Defaults to "utf-8".
    """
    try:
        text = requests.get(file_name).content.decode(decoding)
    except ValueError:
        with open(file_name, "r") as file:
            text = file.read()
    return text
