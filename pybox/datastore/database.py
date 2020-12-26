#!/usr/bin/env python
from pybox.GLOBALS import GLOBAL_DATA_PATH

import sqlite3
import logging


def create_connection(database_name, database_directory=GLOBAL_DATA_PATH):
    """Creates a SQLite database connection.

    Args:
        database_name (string): database name without file extension.
        database_directory (string, optional): directory in which database
            is/would be stored. Defaults to GLOBAL_DATA_PATH.
    """
    database = "".join([database_directory, "\\", database_name, ".db"])

    connection = None
    try:
        connection = sqlite3.connect(database)
        logging.info(
            f"Connection with {database_name} database created successfully.")
    except sqlite3.Error as error:
        logging.error(error)

    return connection


def check_if_table_exists(table_name, database_name,
                          database_directory=GLOBAL_DATA_PATH):

    # Check if in a given SQLite database exists certain table.
    conn = create_connection(database_name)
    with conn:
        cur = conn.cursor()
        cur.execute(f"""
            SELECT count(name)
            FROM sqlite_master
            WHERE type='table'
            AND name='{table_name}'
        """)
        check_result = cur.fetchone()[0]

    if check_result == 1:
        return True
    else:
        return False
