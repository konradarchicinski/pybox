#!/usr/bin/env python
from analyticspy import DATASTORE_PATH
from .data_table import DataTable
from .database import create_connection

import pyarrow.parquet as pq
import numpy as np


def table_from_sqlite(table_name, database, database_directory=None):
    """Load SQLite table and return it as the `DataTable` object.

    Args:
        table_name (str): name of the SQLite table which will be loaded.
        database (str): name of the SQLite database which will be used.
        database_directory (str, optional): directory in which used SQLite
            database is stored. Defaults to None.
    """
    if database_directory:
        conn = create_connection(database, database_directory)
    else:
        conn = create_connection(database)
    with conn:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM '{table_name}'")
        data = cur.fetchall()
        cur.execute(f"PRAGMA TABLE_INFO('{table_name}')")
        info = cur.fetchall()

    data_columns = [column[1] for column in info]

    return DataTable(np.array(data), names=data_columns)


def table_to_parquet(table, file_name, directory=DATASTORE_PATH):
    """Store selected `DataTable` object in the parquet format file. Function
    works based on the `PyArrow` module, firstly transforming `DataTable` into
    Arrow object and afterwards writing it as a parquet file.

    Args:
        table (DataTable): data structure that will be saved.
        file_name (str): name under which data structure will be saved.
        directory (str, optional): string containing directory in which
            DataTable is going to be saved. Defaults to DATASTORE_PATH.
    """
    file_path = f"{directory}{file_name}.parquet"
    arrow_table = table.to_arrow_table
    pq.write_table(arrow_table, file_path)


def table_from_parquet(file_name, directory=DATASTORE_PATH):
    """Load parquet format file as the `DataTable` object. Function works based
    on the `PyArrow` module, firstly reading file and storing it as an Arrow
    object and afterwards transforming it into `DataTable`.

    Args:
        file_name (str): name of parquet file which will be loaded.
        directory (str, optional): string containing directory in which parquet
            file is stored. Defaults to DATASTORE_PATH.

    Returns:
        DataTable: loaded data in a form of DataTable object.
    """
    file_path = f"{directory}{file_name}.parquet"
    arrow_table = pq.read_table(file_path)
    table = DataTable(arrow_table.to_pydict())

    return table
