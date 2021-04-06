#!/usr/bin/env python
from pybox.helpers.text import camel_to_snake_case

from abc import ABC
from importlib import import_module
import os


class Distribution(ABC):

    @staticmethod
    def create(settings, source=None):
        if source is None:
            source = 'ScipyDistribution'
        for module in os.listdir(os.path.dirname(__file__)):
            if module in [f"{source.lower()}.py",
                          f"{camel_to_snake_case(source)}.py"]:
                import_module(f".{module[:-3]}", __package__)
                children = Distribution.__subclasses__()
                for child in children:
                    if child.__name__ == source:
                        distribution = child(settings)
                        return distribution
                raise ValueError((
                    f"Module `{module}` has been inspected but no proper"
                    " implementation of `Distribution` was found there."))
        raise ValueError((
            "No suitable Distribution implementation was found"
            f" for `{source}`."))
