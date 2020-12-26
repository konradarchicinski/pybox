#!/usr/bin/env python
from pybox.GLOBALS import BOXES_PATH
from pybox.helpers.text import camel_to_snake_case

import os
import argparse


_empty_template = ""
_main_init_template = (
    """#!/usr/bin/env python
import os

DATA_PATH = "\\\\".join(
    [os.path.dirname(os.path.abspath(__file__)), "data"])
SETTINGS_PATH = "\\\\".join(
    [os.path.dirname(os.path.abspath(__file__)), "settings"])
""")


def create_box(new_box_name):
    """Creates new Box structure, based on the provided name.

    Args:
        new_box_name (str): name of box to create.
    """
    structures = list()
    box_folder = camel_to_snake_case(new_box_name)
    box_directory = f"{BOXES_PATH}\\{box_folder}"
    data_directory = f"{box_directory}\\data"
    tasks_directory = f"{box_directory}\\tasks"
    settings_directory = f"{box_directory}\\settings"

    init = "__init__.py"
    data_settings = "data_settings.yaml"

    structures.append((box_directory, None))
    structures.append((f"{box_directory}\\{init}", _main_init_template))
    structures.append((data_directory, None))
    structures.append((f"{data_directory}\\{data_settings}", _empty_template))
    structures.append((tasks_directory, None))
    structures.append((f"{tasks_directory}\\{init}", _empty_template))
    structures.append((settings_directory, None))
    structures.append((f"{settings_directory}\\{init}", _empty_template))

    for (name, value) in structures:
        if not os.path.exists(name):
            if value is not None:
                with open(name, 'w') as file:
                    file.write(value)
            else:
                os.makedirs(name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
    Creates new Box structure, based on the provided name.
    """)

    parser.add_argument('-bn', '--box_name', type=str)
    args = parser.parse_args()

    create_box(args.box_name)
