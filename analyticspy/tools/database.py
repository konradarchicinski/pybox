#!/usr/bin/env python
from analyticspy import DATASTORE_PATH

import sqlite3


def create_connection(database_name, database_directory=DATASTORE_PATH):
    """
    Function creates a database connection to a SQLite database. If no database with
    the given name exists, it will be created.

    Args:
        database_name (string): database name without file extension.
        database_directory (string, optional): directory in which database is/would
        be stored. Defaults to DATA_PATH.

    Returns:
        [type]: fucntion returns sqlite database connection.
    """
    database = "".join([database_directory, database_name, ".db"])

    connection = None
    try:
        connection = sqlite3.connect(database)
        print(
            f"Connection with {database_name} database created successfully.")
    except sqlite3.Error as error:
        print(error)

    return connection


def check_if_table_exists(connection, table_name):
    """
    [summary]

    Args:
        connection ([type]): [description]
        table_name ([type]): [description]
    """
    c = connection.cursor()
    c.execute(f"""
        SELECT count(name)
        FROM sqlite_master
        WHERE type='table'
        AND name='{table_name}'
    """)

    if c.fetchone()[0] == 1:
        c.close()
        return True

    c.close()
    return False
