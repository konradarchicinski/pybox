#!/usr/bin/env python
from pybox.GLOBALS import APP_PATH

from abc import ABC, abstractmethod, abstractproperty
import subprocess


class PyBoxTest(ABC):
    """Abstract class defining PyBox test structure."""

    @staticmethod
    def register(test_type):
        """Registers PyBox test.

        Args:
            test_type (str): type of test, should be one of: `C++`, `Python`
        """
        if test_type == 'C++':
            return PyBoxTestCpp()
        else:
            return PyBoxTestPython()

    @abstractmethod
    def create(self):
        """Creates PyBox test from provided arguments."""
        pass

    @abstractproperty
    def run(self):
        """Runs tests from created PyBox test object."""
        pass


class PyBoxTestCpp(PyBoxTest):
    """PyBox tests implementation for C++ modules."""

    def create(self, test_file, source_files):
        """Creates PyBox test from provided names of C++ files.

        Args:
            test_file (str): C++ file name that contains testing code
            source_files (list): list of all C++ source file names used in test
        """
        cpp_sources = ' '.join([test_file] + source_files)
        self.exe_file = test_file.rsplit('.', 1)[0]
        self.command = f'g++ -I {APP_PATH} {cpp_sources} -o {self.exe_file}'

    @property
    def run(self):
        """Runs tests from created PyBox test object,
        compliling and executing it.
        """
        output = subprocess.getoutput(self.command)
        if output == "":
            subprocess.run(self.exe_file)
        else:
            print(output)


# TODO create class to run standard Python tests
class PyBoxTestPython(PyBoxTest):
    """PyBox tests implementation for Python modules."""

    def run(self):
        """Runs tests from created PyBox test object."""
        pass
