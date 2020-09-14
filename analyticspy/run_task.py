#!/usr/bin/env python
from analyticspy import TASKS_PATH

import os
import ast
import runpy
import argparse


def run_selected_module(
        supplied_task_name, help_indicator=False, settings=list()):
    """
    Function used to execute a task distinguished by a specific name.

    Args:
        supplied_task_name (string): name of the task selected for execution.
        help_indicator (bool): if true, help for a given task is printed.
        settings (list): list of task arguments
    """
    globals_dict = {
        "HELP_INDICATOR": help_indicator,
        "SETTINGS": settings,
    }

    # Finding all python files which contains AnalyticsPy tasks.
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
        print(f"- No task has been found with `{supplied_task_name}` name.")


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

        # TODO Write why next steps work in this way.
        assign_objects = [n for n in node.body if isinstance(n, ast.Assign)]
        for assign_object in assign_objects:
            if isinstance(assign_object.value, ast.Call):
                assign_object_keywords = assign_object.value.keywords
                for keyword in assign_object_keywords:
                    if isinstance(keyword.value, ast.Constant):
                        if keyword.value.value == supplied_task_name:
                            check_value = True
    return check_value


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("task_name", type=str)
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="0.1")
    parser.add_argument(
        "-ti",
        "--task_info",
        action="store_const",
        const=True,
        default=False)
    parser.add_argument(
        "-a",
        dest="arguments",
        type=str,
        action='append')

    arguments = parser.parse_args()

    run_selected_module(
        arguments.task_name,
        arguments.task_info,
        arguments.arguments)
