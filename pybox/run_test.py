#!/usr/bin/env python
from pybox.GLOBALS import EXTERN_PATH, TESTS_PATH
from pybox.helpers.text import camel_to_snake_case

import os
import runpy
import argparse


def run_test(test_name, test_type):
    """Runs tests depanding on provided test_name and test_type

    Args:
        test_name (str): name of test, should be written in CamelCase
        test_type (str): type of test, should be one of: `C++`, `Python`
    """
    test_name = camel_to_snake_case(test_name) + '_test'

    if test_type == 'C++':
        tests_source = EXTERN_PATH + '/src'
        tests_path = tests_source + '/__tests__'
    else:
        tests_source = tests_path = EXTERN_PATH

    for module in os.listdir(tests_path):
        if module.endswith('.py') and module.rsplit('.', 1)[0] == test_name:
            runpy.run_path(tests_path + '/' + module)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--test_name', '-tn',
                        action='store', type=str, required=True)
    parser.add_argument('--test_type', '-tt', action='store',
                        type=str, default="Python")
    args = parser.parse_args()

    run_test(args.test_name, args.test_type)
