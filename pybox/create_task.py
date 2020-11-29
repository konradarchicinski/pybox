#!/usr/bin/env python
from pybox.GLOBALS import BOXES_PATH
from pybox.tools.data.data_helpers import camel_to_snake_case

import os
import argparse

new_task_template = """
#!/usr/bin/env python
from pybox.tools.task import Task


def {}():
    pass


task = Task(
    task_name=\"{}\",
    task_info=\"\"\"
    \"\"\")
task.run(main_function={})

"""


def create_task(task_name, box_name):
    """Creates new Task module, based on the provided task and box names

    Args:
        task_name (str): name of the task to create.
        box_name (str): name of the box to put new task.
    """

    box_folder = camel_to_snake_case(box_name)
    box_tasks_directory = f"{BOXES_PATH}\\{box_folder}\\tasks"

    if os.path.exists(box_tasks_directory):
        function_name = camel_to_snake_case(task_name)
        file_path = f"{box_tasks_directory}\\{function_name}.py"

        with open(file_path, "w") as task_file:
            print(new_task_template.format(function_name, task_name, function_name),
                  file=task_file)
    else:
        raise ValueError(
            f"{box_folder} does not have tasks folder, first create it.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
    Creates new Task module, based on the provided task and box names.
    """)

    parser.add_argument('-tn', '--task_name', type=str)
    parser.add_argument('-bn', '--box_name', type=str)
    args = parser.parse_args()

    create_task(args.task_name, args.box_name)
