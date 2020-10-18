#!/usr/bin/env python
from pybox.GLOBALS import TASKS_PATH, DATASTORE_PATH

import os
import ast
import runpy
import argparse
import logging


def run_selected_module(supplied_task_name, inputs_directory=DATASTORE_PATH,
                        outputs_directory=DATASTORE_PATH, show_task_info=False,
                        settings=None):
    """Function used to execute a task distinguished by a specific name.

    Args:
        supplied_task_name (str): name of the task selected for execution.
        inputs_directory (str, optional): directory in which potential input
            data for a given task will be searched. Defaults to DATASTORE_PATH.
        outputs_directory (str, optional): directory in which potential output
            data of a given task will be saved. Defaults to DATASTORE_PATH.
        show_task_info (bool, optional): if true, help for a given task
            is printed. Defaults to False.
        settings (list, optional): list of task arguments stored in strings,
            each string contains the name of the setting and its value, they
            are separated from each other by a colon. Defaults to None.
    """

    globals_dict = {
        "INPUTS_DIRECTORY": inputs_directory,
        "OUTPUTS_DIRECTORY": outputs_directory,
        "SHOW_TASK_INFO": show_task_info,
        "SUPPLIED_TASK_NAME": supplied_task_name,
        "SETTINGS": settings,
    }

    # Finding all python files which contains application's tasks.
    task_files = list()
    for path, subdirs, files in os.walk(TASKS_PATH):
        for name in files:
            if name.endswith(".py") and name != "__init__.py":
                task_files.append(os.path.join(path, name))

    task_file_to_run = None
    for task_file in task_files:
        if task_file_to_run is None:
            if _task_name_registered_in_file(task_file, supplied_task_name):
                task_file_to_run = task_file
        else:
            break

    if task_file_to_run:
        runpy.run_path(task_file_to_run, init_globals=globals_dict)
    else:
        logging.error(
            f"The task called `{supplied_task_name}` has not been found.")


def _task_name_registered_in_file(task_file, supplied_task_name):
    """
    Auxiliary function to check if a given file containing AnalyticPy task,
    has been registered under name supplied from command line.

    Args:
        task_file (string): complete path and name of a task file to check.
        supplied_task_name (string): name of the task selected for execution.

    Returns:
        bool: True if `supplied_task_name` in `task_file`, otherwise False.
    """
    check_value = False

    with open(task_file) as task_script:
        node = ast.parse(task_script.read())

        # Only top-level assignments are selected from each module,
        # since this is how TaskInit instances are created.
        assign_objects = [n for n in node.body if isinstance(n, ast.Assign)]
        for assign_object in assign_objects:
            if isinstance(assign_object.value, ast.Call):
                # For each found assignment, it is checked whether
                # the assignedvalue is of the Call type
                # (which is assumed to refer to TaskInit).
                assign_object_keywords = assign_object.value.keywords
                for keyword in assign_object_keywords:
                    # If a suitable assignment is found its arguments are
                    # checked, the task name in TaskInit should be stored
                    # as Const.
                    if isinstance(keyword.value, ast.Constant):
                        if keyword.value.value == supplied_task_name:
                            check_value = True
    return check_value


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # TODO write about change - cmd removed special charcters like &
    parser.add_argument("run_task_parameters", type=str)
    parser_arg = parser.parse_args()
    parameters_list = parser_arg.run_task_parameters.split(" -")

    task_name = parameters_list[0]
    del parameters_list[0]
    inputs_directory = DATASTORE_PATH
    outputs_directory = DATASTORE_PATH
    task_info = False
    arguments = []

    for element in parameters_list:
        arg_type, arg = element.split(" ")
        if arg_type == "a":
            arguments.append(arg)
        elif arg_type == "ti":
            task_info = True
        elif arg_type == "idir":
            inputs_directory = arg
        elif arg_type == "odir":
            outputs_directory = arg

    run_selected_module(task_name, inputs_directory,
                        outputs_directory, task_info, arguments)
