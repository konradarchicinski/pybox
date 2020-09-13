#!/usr/bin/env python
from analyticspy import DATASTORE_PATH
from .data import Table
from .database import create_connection

import pyarrow.parquet as pq
import numpy as np


def read_sql(table, database, database_directory=None):
    """
    [summary]

    Args:
        table ([type]): [description]
        database ([type]): [description]
        database_directory ([type], optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """

    if database_directory:
        conn = create_connection(database, database_directory)
    else:
        conn = create_connection(database)

    c = conn.cursor()
    c.execute(f"SELECT * FROM '{table}'")
    data = c.fetchall()

    c.execute(f"PRAGMA TABLE_INFO('{table}')")
    info = c.fetchall()

    c.close()

    numpy_type_map = {"TEXT": "a25", "REAL": "f4", "INTEGER": "i4"}

    data_types = [(column[1], numpy_type_map[column[2]]) for column in info]

    table = Table()
    table.data = np.array(data, dtype=data_types)

    return table


def table_to_parquet(table, file_name, directory=DATASTORE_PATH):
    """
    Function saves selected `Table` or `TypedTable` object into parquet file.
    It works based on the `PyArrow` module, firstly transforming `Table` into
    arrow object and afterwards writing it as a parquet file.

    Args:
        table (Table): Table object that will be saved.
        file_name (str): name under which Table will be saved.
        directory (str, optional): string containing directory in which Table
            is going to be saved. Defaults to DATASTORE_PATH.
    """
    file_path = f"{directory}{file_name}.parquet"
    arrow_table = table.to_arrow
    pq.write_table(arrow_table, file_path)


def table_from_parquet(file_name, directory=DATASTORE_PATH):
    """
    Function loads particular parquet file as a Table object. It works based
    on the `PyArrow` module, firstly reading file and storing it as an Arrow
    object and afterwards transforming it into `Table`.

    Args:
        file_name (str): name of parquet file which will be load.
        directory (str, optional): string containing directory in which parquet
            file is stored. Defaults to DATASTORE_PATH.

    Returns:
        Table: Table object.
    """
    file_path = f"{directory}{file_name}.parquet"
    arrow_table = pq.read_table(file_path)
    data_types = [(data_type.name, "O") for data_type in arrow_table.schema]
    table = Table(arrow_table.to_pydict(), data_types)

    return table
