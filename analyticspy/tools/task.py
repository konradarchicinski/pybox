#!/usr/bin/env python
import ast
import inspect
from datetime import datetime


class TaskInit:
    """
    Task initiation, it is used to define a unique task name.
    """

    def __init__(self, task_name, task_info):
        """
        Initialization of the TaskInit class, it is used to check if the task name
        supplied by `run_task` script matches the one in the active module.

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
        """
        [summary]

        Args:
            name ([type]): [description]
            value ([type]): [description]
            info ([type]): [description]
        """
        self.task_settings[name] = value
        self.task_settings_info[name] = info

    def _overwrite_setting(self, setting):
        """
        [summary]

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
        """
        [summary]
        """
        help_string = "".join(
            ["\nTask Info:", self.task_info, "\nTask setting arguments:\n"])
        for name, info in self.task_settings_info.items():
            help_string = "".join([help_string, "- ", name, " ",
                                   str(type(self.task_settings[name])),
                                   info, "- default value: ",
                                   str(self.task_settings[name]), "\n"
                                   ])
        print(help_string)

    def run(self, main_function, task_predecessors=None):
        """
        Method used to perform the task if an active task was approved after
        initiation.

        Args:
            main_function (function): name of the main function used in a task.
            task_predecessors (list, optional): input names which are going to be used
                in a task. Defaults to None.
        """
        if self.help_indicator:
            self._print_help()
        else:
            # Printing information about starting of the task.
            print("".join(["-" * 79, "\nTask ",
                           self.task_name, " started on:\t",
                           datetime.now().strftime("%Y/%m/%d, %H:%M:%S"),
                           "\n", "-" * 79
                           ]))
            function_input_list = list()

            if task_predecessors is not None:
                # TODO write code which will run task predecessors.
                # It needs to be solved how to handle data flow in that case.
                function_input_list.extend([])

            if self.task_settings:
                if self.supplied_settings:
                    for setting in self.supplied_settings:
                        self._overwrite_setting(setting)
                function_input_list.append(self.task_settings)

            main_function(*function_input_list)
            # Printing information about ending of the task.
            print("".join(["-" * 79, "\nTask ",
                           self.task_name, " ended on:\t\t",
                           datetime.now().strftime("%Y/%m/%d, %H:%M:%S"),
                           "\n", "-" * 79
                           ]))
