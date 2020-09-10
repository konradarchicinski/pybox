#!/usr/bin/env python
from analyticspy import DATALAKE_PATH

import analyticspy.tools.data as atd
import analyticspy.tools.database as atdb
import pandas as pd


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
        conn = atdb.create_connection(database, database_directory)
    else:
        conn = atdb.create_connection(database)

    c = conn.cursor()
    c.execute(f"SELECT * FROM '{table}'")
    data = c.fetchall()

    c.execute(f"PRAGMA TABLE_INFO('{table}')")
    info = c.fetchall()

    c.close()

    numpy_type_map = {"TEXT": "a25", "REAL": "f4", "INTEGER": "i4"}

    data_types = [(column[1], numpy_type_map[column[2]]) for column in info]

    table = atd.Table()
    table.data = atd.np.array(data, dtype=data_types)

    return table


def read_file(file_name, extension):
    """
    Function uses `Pandas` read family funtions to load particular file
    as a DataFrame object.

    Args:
        file_name (string): name of the file to be searched for in Data folder.
        extension (string): extension of a file that will be loaded.
    Returns:
        DataFrame: loaded from csv, parquet, "xls", "xlsx" or "xlsm" format.
    """

    if extension == "csv":
        return pd.read_csv(
            DATALAKE_PATH + f"{file_name}.{extension}"
        )
    elif extension == "parquet":
        return pd.read_parquet(
            DATALAKE_PATH + f"{file_name}.{extension}"
        )
    elif extension in ["xls", "xlsx", "xlsm"]:
        return pd.read_excel(
            DATALAKE_PATH + f"{file_name}.{extension}"
        )


def save_file(data_frame, file_name, extension):
    """
    Function uses `Pandas` DataFrame.to family functions to save particular
    DataFrame objext as file in csv, parquet, "xls", "xlsx" or "xlsm" format.

    Args:
        data_frame (DataFrame): Dataframe object that will be saved.
        file_name (string): name under which DataFrame will be saved.
        extension (string): extension of a file that will be saved.
    """

    if extension == "csv":
        data_frame.to_csv(
            DATALAKE_PATH + f"{file_name}.{extension}"
        )
    elif extension == "parquet":
        data_frame.to_parquet(
            DATALAKE_PATH + f"{file_name}.{extension}"
        )
    elif extension in ["xls", "xlsx", "xlsm"]:
        data_frame.to_excel(
            DATALAKE_PATH + f"{file_name}.{extension}", sheet_name=file_name
        )
