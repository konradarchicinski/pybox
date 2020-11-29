#!/usr/bin/env python
from pybox.tools.task import Task
from pybox import DataTable

import os
from datetime import datetime


def clean_reuters(inputs):
    """Cleans provided Reuters news data. Removes None values
    and merges multiple input tables into the one.

    Args:
        inputs (list): DataTables containing raw Reuters news data.
    """
    data_columns = ["LastModificationDate", "Headline", "Body"]
    cleaned_reuters = DataTable(
        names=data_columns,
        dtypes=[datetime, str, str])

    for input_data in inputs:
        cleaned_reuters.concatenate(
            input_data, inner_columns=data_columns, outer_columns=data_columns)

    cleaned_reuters.filter(
        lambda row: all(row[column] is not None for column in data_columns))

    cleaned_reuters.sort(["LastModificationDate"])

    return cleaned_reuters


def clean_scraped_data(*args):
    """Cleans provided data. Removes None values and merges multiple
    input tables into the one, containing data ready to analyse.

    Data types implemented in task include: Reuters.
    """
    settings = args[-1]
    inputs = args[:-1]

    data_type = settings["DataType"]

    if data_type == "Reuters":
        return clean_reuters(inputs)
    else:
        raise ValueError(f"{data_type} is not implemented DataType.")


def _dynamic_inputs_creation(dynamic_io_settings):
    """Creates a list of inputs names, supplied to the Task class."""
    inputs_directory = dynamic_io_settings["InputsDirectory"]
    data_type = dynamic_io_settings["TaskSettings"]["DataType"]

    if data_type == "Reuters":
        inputs_list = list()
        for file in os.listdir(inputs_directory):
            if file.startswith("Reuters") and file.endswith(".parquet"):
                inputs_list.append(file.rsplit(".", 1)[0])

        return inputs_list
    else:
        raise ValueError(f"Wrong data type provided: {data_type}")


def _dynamic_outputs_creation(dynamic_io_settings):
    """Creates a list of outputs names, supplied to the Task class."""
    data_type = dynamic_io_settings["TaskSettings"]["DataType"]

    inputs_list = _dynamic_inputs_creation(dynamic_io_settings)

    dates_list = list()
    for input_name in inputs_list:
        dates_string = input_name[
            input_name.find("(")+1:input_name.find(")")
        ]
        dates_list.extend(dates_string.split(","))

    dates_list = sorted(dates_list)
    return [f"Cleaned{data_type}({dates_list[0]},{dates_list[-1]})"]


task = Task(
    task_name="ScrapedDataCleaning",
    task_info="""
    Cleans and prepares scraped data. In particular removes rows
    containing None values, and merge multiple inputs into one
    final dataset.
    """)
task.add_setting(
    name="DataType",
    default_value="Reuters",
    info="""
    Specifies what type of task should be called.
    """)
task.run(
    main_function=clean_scraped_data,
    task_inputs=_dynamic_inputs_creation,
    task_outputs=_dynamic_outputs_creation)
