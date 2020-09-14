#!/usr/bin/env python
import ast
import inspect
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
        self.supplied_settings = inspect.stack()[1][0].f_globals["SETTINGS"]
        self.help_indicator = inspect.stack()[1][0].f_globals["HELP_INDICATOR"]

    def add_setting(self, name, value, info):
        """[summary]

        Args:
            name ([type]): [description]
            value ([type]): [description]
            info ([type]): [description]
        """
        self.task_settings[name] = value
        self.task_settings_info[name] = info

    def _overwrite_setting(self, setting):
        """[summary]

        Args:
            setting ([type]): [description]

        Raises:
            ValueError: [description]
        """
        setting_name, setting_value = setting.split(":", 1)
        if setting_name in self.task_settings:
            self.task_settings[setting_name] = ast.literal_eval(setting_value)
        else:
            raise ValueError(
                f"`{setting_name}` has not been found in task settings.")

    def _print_help(self):
        """[summary]"""
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
        if self.help_indicator:
            self._print_help()
        else:
            # Printing information about starting of the task.
            print("".join(
                ["-" * 79, "\n", datetime.now().strftime("%Y/%m/%d, %H:%M:%S"),
                 "\tTask ", self.task_name, " started.\n", "-" * 79]
            ))
            function_input_list = list()

            if task_inputs:
                # TODO write code which will run task inputs automatically.
                # It needs to be solved how to handle data flow in that case.
                inputs = list()
                for name in task_inputs:
                    try:
                        inputs.append(table_from_parquet(name))
                    except FileNotFoundError:
                        run_selected_module(name)
                        inputs.append(table_from_parquet(name))
                function_input_list.extend(inputs)

            if self.task_settings:
                if self.supplied_settings:
                    for setting in self.supplied_settings:
                        self._overwrite_setting(setting)
                function_input_list.append(self.task_settings)

            if task_outputs:
                outputs = main_function(*function_input_list)
                if not isinstance(outputs, tuple):
                    outputs = tuple([outputs])
                for output, name in zip(outputs, task_outputs):
                    table_to_parquet(output, name)
            else:
                main_function(*function_input_list)

            # Printing information about ending of the task.
            print("".join(
                ["-" * 79, "\n", datetime.now().strftime("%Y/%m/%d, %H:%M:%S"),
                 "\tTask ", self.task_name, " ended.\n", "-" * 79]
            ))
