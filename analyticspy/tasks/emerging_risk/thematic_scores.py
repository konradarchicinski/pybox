#!/usr/bin/env python
from analyticspy.tools.task import TaskInit


def calculate_daily_scores(processed_daily_news):
    pass


task = TaskInit(
    task_name="ThematicDailyScores",
    task_info="""
    The task is used for the calculation of standardized scores (z-scores)
    that describe the most influential themes in certain groups of topics.
    """)
task.run(
    main_function=calculate_daily_scores,
    task_inputs=["ProcessedDailyNews"],
    task_outputs=["ThematicDailyScores"])
