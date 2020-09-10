#!/usr/bin/env python
from analyticspy.tools.task import TaskInit


def ingest_data():
    pass


task = TaskInit(
    task_name="DataIngest(ReutersNews)",
    task_info="""
    """)
task.run(main_function=ingest_data)
