#!/usr/bin/env python
import ast
import inspect
from analyticspy import logging
from datetime import datetime

from analyticspy.run_task import run_selected_module
from .data_flow import table_to_parquet, table_from_parquet


class TaskInit:
    """Task initiation, it is used to define an unique task name."""

    def __init__(self, task_name, task_info):
        """Initialization of the TaskInit class, it is used to check if the
        task name supplied by `run_task` script matches the one in the active
        module.

        Args:
            task_name (str): task name registered in the active module.
            task_info (str): information on the purpose of the task.
        """
        self.task_name = task_name
        self.task_info = task_info
        self.task_settings = dict()
        self.task_settings_info = dict()

        # Getting variables from caller's globals.
        global_variables = inspect.stack()[1][0].f_globals
        self.supplied_settings = global_variables["SETTINGS"]
        self.show_task_info = global_variables["SHOW_TASK_INFO"]
        self.inputs_directory = global_variables["INPUTS_DIRECTORY"]
        self.outputs_directory = global_variables["OUTPUTS_DIRECTORY"]
        self.supplied_task_name = global_variables["SUPPLIED_TASK_NAME"]

    def add_setting(self, name, value, info):
        """Function used to add a new setting which will be supplied to a given
        task. Setting acts as a parameter in a given task that can often be
        modified to partially change the operation of the task.

        Args:
            name (str): name of a setting.
            value (any): information stored as a setting.
            info (str): brief mention of the advisability of using a given setting.
        """
        self.task_settings[name] = value
        self.task_settings_info[name] = info

    def _overwrite_setting(self, setting):
        """Auxiliary method that overwrites default settings with new values
        supplied by user from command line interface.

        Args:
            setting (str): string that contains the name of the setting and
                its value, they are separated from each other by a colon.

        Raises:
            ValueError: If the given setting name is not present in default
                settings, an error is returned, as there is nothing to be
                overwrite with the new settings value.
        """
        setting_name, setting_value = setting.split(":", 1)
        if setting_name in self.task_settings:
            self.task_settings[setting_name] = ast.literal_eval(setting_value)
        else:
            raise ValueError(
                f"`{setting_name}` has not been found in task settings.")

    def _print_task_info(self):
        """Auxiliary method that displays basic information about called task."""
        help_string = "".join(["\nTask Info:", self.task_info])

        for name, info in self.task_settings_info.items():
            help_string = "".join(
                [help_string, "\nTask setting arguments:\n- ",
                 name, " ", str(type(self.task_settings[name])),
                 info, "- default value: ",
                 str(self.task_settings[name]), "\n"]
            )
        print(help_string)

    def run(self, main_function, task_inputs=None, task_outputs=None):
        """Method used to perform the task if an active task was approved
        after initiation.

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

            # Solving out task's inputs.
            function_input_list = list()
            if task_inputs:
                inputs = list()
                for name in task_inputs:
                    try:
                        inputs.append(
                            table_from_parquet(
                                file_name=name,
                                directory=self.inputs_directory))
                    except FileNotFoundError:
                        logging.info(
                            f"\tInput file called `{name}` was not found.")
                        logging.info(
                            "\tSearching the task with a given name initiated...")

                        run_selected_module(
                            supplied_task_name=name,
                            inputs_directory=self.inputs_directory,
                            outputs_directory=self.outputs_directory)
                        inputs.append(
                            table_from_parquet(
                                file_name=name,
                                directory=self.inputs_directory))
                function_input_list.extend(inputs)

            # Solving out task's settings.
            if self.task_settings:
                # Overwriting default settings if there are new ones
                # supplied from the command line interface.
                if self.supplied_settings:
                    for setting in self.supplied_settings:
                        self._overwrite_setting(setting)
                function_input_list.append(self.task_settings)

            # Solving out task's outputs.
            if task_outputs:
                outputs = main_function(*function_input_list)
                if not isinstance(outputs, tuple):
                    outputs = tuple([outputs])
                for output, name in zip(outputs, task_outputs):
                    table_to_parquet(
                        table=output,
                        file_name=name,
                        directory=self.outputs_directory)
            else:
                main_function(*function_input_list)

            logging.info(f"Task {self.task_name} ended.")
