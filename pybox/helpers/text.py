#!/usr/bin/env python
import re


def camel_to_snake_case(string):
    """Transform provided value from CamelCase format to snake_case.

    Args:

        string (str): string to be transformed.
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', string).lower()


def snake_to_camel_case(string):
    """Transform provided value from snake_case format to CamelCase.

    Args:

        string (str): string to be transformed.
    """
    return ''.join(component.title() for component in string.split('_'))
