#!/usr/bin/env python
from boxes.emerging_risk import SETTINGS_PATH
from pybox.task import Task


def word_importance(settings):
    pass


task = Task(
    task_name="WordImportance",
    task_info="""
    """)
task.external_settings(
    file_name="word_importance.yaml",
    file_directory=SETTINGS_PATH)
task.run(main_function=word_importance)
