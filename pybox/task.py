#!/usr/bin/env python
import ast
import inspect
import logging
import yaml

import pybox.run_task as pbrt
import pybox.datastore.data_flow as pbddf
from pybox.helpers.text import snake_to_camel_case


class Task:
    """Task class, it is used to define an unique task name."""

    def __init__(self, task_name, task_info):
        """Initialization of the Task class, it is used to check if the
        task name supplied by `run_task` script matches the one in the active
        module.

        Args:
            task_name (str): task name registered in the active module.
            task_info (str): information on the purpose of the task.
        """
        # Getting variables from caller's globals.
        global_variables = inspect.stack()[1][0].f_globals
        self.supplied_settings = global_variables["SETTINGS"]
        self.show_task_info = global_variables["SHOW_TASK_INFO"]
        self.inputs_directory = global_variables["INPUTS_DIRECTORY"]
        self.outputs_directory = global_variables["OUTPUTS_DIRECTORY"]
        self.supplied_task_name = global_variables["SUPPLIED_TASK_NAME"]

        self.task_settings = dict()
        self.task_settings_info = dict()
        self.task_info = task_info
        self._construct_name_and_parameters(task_name)

    def external_settings(self, file_name, file_directory):
        """Reads external settings from YAML file and stores them as task settings.

        Args:
            file_name (str): name of the file to read.
            file_directory (str): directory of the file to read.
        """
        with open(f"{file_directory}\\{file_name}", "r") as settings:
            raw_settings = yaml.load(settings, Loader=yaml.FullLoader)
        for name, value in raw_settings.items():
            # Adjustments of the info string to prepare long string for printing.
            indentation = "\n" + " " * 4
            value["info"] = "".join([indentation, value['info'], indentation])
            for i in range(1, len(value["info"])):
                if i % 70 == 0:
                    break_line_index = value["info"].find(" ", i)
                    value["info"] = indentation.join([
                        value["info"][:break_line_index],
                        value["info"][break_line_index + 1:]
                    ])

            self.task_settings[name] = value["value"]
            self.task_settings_info[name] = value["info"]

    def add_setting(self, name, default_value, info, task_parameters=None):
        """Adds a new setting which will be supplied to a given task.
        Setting acts as a parameter in a given task that can often be
        modified to partially change the operation of the task.

        Args:
            name (str): name of a setting.
            default_value (any): default value stored of a setting.
            info (str): brief mention of the advisability of using a given setting.
            task_parameters (list, optional): define which task type
                the setting applies to. Default None.
        """
        if task_parameters is None:
            task_parameters = self.parameters
        if (any(parameter in task_parameters for parameter in self.parameters)
                or not self.parameters):
            self.task_settings[name] = default_value
            self.task_settings_info[name] = info

    def run(self, main_function, task_inputs=None, task_outputs=None):
        """Performs the task if an active task was approved after initiation.

        Args:
            main_function (function): name of the main function used in a task.
            task_inputs (list, optional): input names which are going to be used
                in the task. Defaults to None.
            task_outputs (list, optional): output names which are going to be
                used in the task. Defaults to None.
        """
        if self.show_task_info:
            self._print_task_info()
        elif self.supplied_task_name == self.task_name:
            logging.info(f"Task {self.task_name} started.")
            function_input_list = list()

            # Sorting out task's settings.
            if self.task_settings:
                # Overwriting default settings if there are new ones
                # supplied from the command line interface.
                if self.supplied_settings:
                    self._overwrite_settings

            # Sorting out task's inputs.
            inputs = list()
            if task_inputs:
                task_inputs = self._prepare_io_list(task_inputs, "inputs")
                for name in task_inputs:
                    try:
                        inputs.append(
                            pbddf.table_from_parquet(
                                file_name=name,
                                directory=self.inputs_directory))
                    except FileNotFoundError:
                        logging.info(
                            f"\tInput file called `{name}` was not found.")
                        logging.info(
                            "\tSearching the task with a given name initiated..."
                        )

                        pbrt.run_selected_module(
                            supplied_task_name=name,
                            inputs_directory=self.inputs_directory,
                            outputs_directory=self.outputs_directory)
                        inputs.append(
                            pbddf.table_from_parquet(
                                file_name=name,
                                directory=self.inputs_directory))

            # Merging inputs, settings into one list.
            if inputs:
                function_input_list.extend(inputs)
            if self.task_settings or self.parameters:
                function_input_list.append(self.task_settings)

            # Sorting out task's outputs.
            if task_outputs:
                task_outputs = self._prepare_io_list(task_outputs, "outputs")
                outputs = main_function(*function_input_list)
                if not isinstance(outputs, tuple):
                    outputs = tuple([outputs])
                for output, name in zip(outputs, task_outputs):
                    pbddf.table_to_parquet(table=output,
                                           file_name=name,
                                           directory=self.outputs_directory)
            else:
                main_function(*function_input_list)

            logging.info(f"Task {self.task_name} ended.")

    def _construct_name_and_parameters(self, task_name):
        """Constructs task name and parameters objects from supplied task name.

        Args:
            task_name (str): task name registered in the active module.

        Raises:
            ValueError:  If found parameters from first name does not match
            the length of parameters from the other one.
        """
        task_parameters = retrieve_parameters(task_name)
        supplied_parameters = retrieve_parameters(self.supplied_task_name)

        if len(task_parameters) == len(supplied_parameters):
            self.parameters = supplied_parameters
            self.task_name = task_name
            if self.parameters:
                self.task_settings["Parameters"] = dict()
                for parameter, supplied_parameter in zip(
                        task_parameters, supplied_parameters):
                    self.task_settings["Parameters"][snake_to_camel_case(
                        parameter.strip("?"))] = supplied_parameter
                    self.task_name = self.task_name.replace(
                        parameter, supplied_parameter)
        else:
            raise ValueError(
                (f"Provided parameters {supplied_parameters} do not"
                 f" match the expected ones {task_parameters}."))

    def _print_task_info(self):
        """Displays basic information about called task."""
        help_string = "".join(["\nTask Info:", self.task_info])

        for name, info in self.task_settings_info.items():
            help_string = "".join([
                help_string, "\nTask setting arguments:\n- ", name, " ",
                str(type(self.task_settings[name])), info, "- default value: ",
                str(self.task_settings[name]), "\n"
            ])
        print(help_string)

    def _prepare_io_list(self, task_io, io_type):
        """Checks if provided task Inputs/Outputs(IO) are of list or function type.

        List type sugests fixed list of IO, so it returns task IO without change.
        Function type sugests dynamic Inputs/Outputs list creation, to handle it
        method calls task_io as a function and using it produces right IO list.

        Args:

            task_io (list, function): provided task inputs/outputs list
                or function to create them.
            io_type (str): type of a call `inputs` or `outputs`.

        Raises:
            ValueError: If the given task_io is neither `function` nor `list` type.
        """
        if isinstance(task_io, list):
            return task_io
        elif hasattr(task_io, "__call__"):
            logging.info(f"\tCreating dynamic {io_type}.")
            dynamic_io_settings = {
                "TaskName": self.task_name,
                "TaskSettings": self.task_settings,
                "InputsDirectory": self.inputs_directory,
                "OutputsDirectory": self.outputs_directory
            }
            dynamic_task_io = task_io(dynamic_io_settings)
            return dynamic_task_io
        else:
            raise ValueError(f"Wrong type of task inputs/outputs: {task_io}")

    @property
    def _overwrite_settings(self):
        """Overwrites default settings with new values supplied by user
        from the command line interface.
        """
        if isinstance(self.supplied_settings, dict):
            self.task_settings.update(self.supplied_settings)
        else:
            for setting in self.supplied_settings:
                setting_name, setting_value = setting.split(":", 1)
                setting_value = setting_value.strip("\'")

                if isinstance(self.task_settings[setting_name], str):
                    self.task_settings[setting_name] = setting_value
                else:
                    self.task_settings[setting_name] = ast.literal_eval(
                        setting_value)


def retrieve_parameters(task_name):
    """Retrieves parameters from provided task name. If task has not
    any parameter returns empty list.

    Args:
        task_name (str): name in which parameters will be searched.
    """
    start = task_name.find("(")
    end = task_name.find(")")

    if -1 not in [start, end]:
        return task_name[start + 1:end].split(",")
    else:
        return list()
