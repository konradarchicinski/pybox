#!/usr/bin/env python
import os
from pathlib import Path

APP_PATH = str(Path(os.path.realpath(__file__)).parents[1])

DATASTORE_PATH = "".join([APP_PATH, "\\datastore\\"])
DATALAKE_PATH = "".join([APP_PATH, "\\datalake\\"])
TASKS_PATH = "".join([APP_PATH, "\\analyticspy\\tasks\\"])
