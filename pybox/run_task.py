#!/usr/bin/env python
from pybox.GLOBALS import BOXES_PATH

import os
import re
import ast
import runpy
import argparse
import logging
import importlib.util


def run_selected_module(supplied_task_name, inputs_directory=None,
                        outputs_directory=None, show_task_info=False,
                        settings=None, settings_path=None):
    """Function used to execute a task distinguished by a specific name.

    Args:
        supplied_task_name (str): name of the task selected for execution.
        inputs_directory (str, optional): directory in which potential input
            data for a given task will be searched. Defaults to None.
        outputs_directory (str, optional): directory in which potential output
            data of a given task will be saved. Defaults to None.
        show_task_info (bool, optional): if true, help for a given task
            is printed. Defaults to False.
        settings (list, optional): list of task arguments stored in strings,
            each string contains the name of the setting and its value, they
            are separated from each other by a colon. Defaults to None.
        settings_path (str, optional):
    """
    if settings_path is not None:
        settings = _read_settings_file(settings_path)

    globals_dict = {"INPUTS_DIRECTORY": inputs_directory,
                    "OUTPUTS_DIRECTORY": outputs_directory,
                    "SHOW_TASK_INFO": show_task_info,
                    "SUPPLIED_TASK_NAME": supplied_task_name,
                    "SETTINGS": settings}

    # Finding all python files which contains application's tasks.
    task_files = list()
    for path, subdirs, files in os.walk(BOXES_PATH):
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

    if task_file_to_run is not None:
        globals_dict = _update_globals(task_file_to_run, globals_dict)
        runpy.run_path(task_file_to_run, init_globals=globals_dict)
    else:
        logging.error(
            f"The task called `{supplied_task_name}` has not been found.")


def _read_settings_file(settings_path):
    """Reads settings from provided python module.

    Mentioned module should consist create_settings function
    which returns dictionary of settings.

    Args:
        settings_path (str): directory of settings module to be read. 
    """
    spec = importlib.util.spec_from_file_location(
        "task_file_settings", settings_path)
    settings_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(settings_module)

    return settings_module.create_settings()


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
    # Splits are performed to separate parameters from task name
    # (if parameters exist). At this stage they should not be relevant.
    supplied_task_name = supplied_task_name.split("(")[0]

    with open(task_file) as task_script:
        node = ast.parse(task_script.read())

        # Only top-level assignments are selected from each module,
        # since this is how Task instances are created.
        assign_objects = [n for n in node.body if isinstance(n, ast.Assign)]
        for assign_object in assign_objects:
            if isinstance(assign_object.value, ast.Call):
                # For each found assignment, it is checked whether
                # the assignedvalue is of the Call type
                # (which is assumed to refer to Task).
                assign_object_keywords = assign_object.value.keywords
                for keyword in assign_object_keywords:
                    # If a suitable assignment is found its arguments are
                    # checked, the task name in Task is found by arg name
                    # which should be `task_name`.
                    if keyword.arg == "task_name":
                        found_task_name = keyword.value.value.split("(")[0]
                        if found_task_name == supplied_task_name:
                            check_value = True
    return check_value


def _update_globals(task_file_to_run, globals_dict):
    """Updates globals dictionary with default data path for provided
    task if Inputs/Outputs directories are equal to None.

    Args:
        task_file_to_run (str): path to the task that will be run. 
        globals_dict (dict): contains global variables for function to run.
    """
    default_data_path = "\\".join(
        [task_file_to_run.split("\\tasks\\")[0], "data"])
    for directory in ["INPUTS_DIRECTORY", "OUTPUTS_DIRECTORY"]:
        if globals_dict[directory] is None:
            globals_dict[directory] = default_data_path

    return globals_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Using one argument instead of the multiple argaprse ones
    # is to minimize the risk of encountering escape characters
    # in one of the arguments provided on the command line.
    parser.add_argument("run_task_parameters", type=str)
    parser_arg = parser.parse_args()

    parameters_list = re.split(
        ''' -(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''',
        parser_arg.run_task_parameters)

    task_name = parameters_list[0]
    del parameters_list[0]

    inputs_outputs_directory = None
    inputs_directory = None
    outputs_directory = None
    task_info = False
    arguments = []
    settings_path = None

    for element in parameters_list:
        if element.startswith("ti") or element.startswith("-task_info"):
            task_info = True
        else:
            arg_type, arg = element.split(" ", 1)
            if arg_type in ["a", "-argument"]:
                arguments.append(arg)
            elif arg_type in ["iodir", "-inputs_outputs_directory"]:
                inputs_outputs_directory = arg
            elif arg_type in ["idir", "-inputs_directory"]:
                inputs_directory = arg
            elif arg_type in ["odir", "-outputs_directory"]:
                outputs_directory = arg
            elif arg_type in ["sp", "-settings_path"]:
                settings_path = arg

    if inputs_outputs_directory is not None:
        inputs_directory = inputs_outputs_directory
        outputs_directory = inputs_outputs_directory

    run_selected_module(task_name, inputs_directory, outputs_directory,
                        task_info, arguments, settings_path)
