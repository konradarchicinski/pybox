#!/usr/bin/env python
from pybox.tools.task import Task


def calculate_scores(processed_news_data):
    pass


task = Task(
    task_name="ThematicScores",
    task_info="""
    The task is used for the calculation of standardized scores (z-scores)
    that describe the most influential themes in certain groups of topics.
    """)
task.run(
    main_function=calculate_scores,
    task_inputs=["ProcessedNewsData"],
    task_outputs=["ThematicScores"])
