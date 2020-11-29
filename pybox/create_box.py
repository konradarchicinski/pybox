#!/usr/bin/env python
from pybox.GLOBALS import BOXES_PATH
from pybox.tools.data.data_helpers import camel_to_snake_case

import os
import argparse


def create_box(new_box_name):
    """Creates new Box structure, based on the provided name.

    Args:
        new_box_name (str): name of box to create.
    """
    structures = list()
    box_folder = camel_to_snake_case(new_box_name)
    box_directory = f"{BOXES_PATH}\\{box_folder}"

    init = "__init__.py"
    data_settings = "data_settings.yaml"

    structures.append(
        (box_directory, f"{box_directory}\\{init}"))
    structures.append(
        (f"{box_directory}\\data", f"{box_directory}\\data\\{data_settings}"))
    structures.append(
        (f"{box_directory}\\tasks", f"{box_directory}\\tasks\\{init}"))

    for structure in structures:
        for element in structure:
            if not os.path.exists(element):
                if "." in element:
                    with open(element, 'w') as f:
                        pass
                else:
                    os.makedirs(element)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
    Creates new Box structure, based on the provided name.
    """)

    parser.add_argument('-bn', '--box_name', type=str)
    args = parser.parse_args()

    create_box(args.box_name)
