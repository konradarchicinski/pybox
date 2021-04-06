#!/usr/bin/env python
from pybox.helpers.text import camel_to_snake_case

from abc import ABC, abstractmethod
from numdifftools import Gradient
from importlib import import_module
import os


class Optimizer(ABC):

    def __init__(self):
        self.Nfevel = 1

    @staticmethod
    def create(method=None):
        if method is None:
            method = "BFGS"
        for module in os.listdir(os.path.dirname(__file__)):
            if module in [
                    f"{method.lower()}.py", f"{camel_to_snake_case(method)}.py"
            ]:
                import_module(f".{module[:-3]}", __package__)
                children = Optimizer.__subclasses__()
                for child in children:
                    if child.__name__ == method:
                        optimizer = child()
                        return optimizer
                raise ValueError(
                    (f"Module `{module}` has been inspected but no proper"
                     " implementation of `Optimizer` was found there."))
        raise ValueError(
            f"No suitable Optimizer implementation was found for `{method}`.")

    @staticmethod
    def gradient(function, coordinates=None):
        if coordinates is None:
            return Gradient(function)
        else:
            return Gradient(function)(coordinates)

    @abstractmethod
    def minimize():
        pass

    def print_info(self, iteration, xs, value):
        len_xs = len(xs)
        print((f'\tITERATION NUMBER: {iteration}\n'
               f'Parameters: {xs}\n'
               f'Function Value: {value}'))

    @property
    def minimum_value(self):
        try:
            return self.summary.fun
        except AttributeError:
            raise AttributeError(
                "The minimization process has not been performed.")

    @property
    def minimum_coordinates(self):
        try:
            return self.summary.x
        except AttributeError:
            raise AttributeError(
                "The minimization process has not been performed.")
