#!/usr/bin/env python
import os
import yaml
import logging
import logging.config
from pathlib import Path


APP_PATH = str(Path(os.path.realpath(__file__)).parents[1])

DATASTORE_PATH = "".join([APP_PATH, "\\datastore\\"])
DATALAKE_PATH = "".join([APP_PATH, "\\datalake\\"])
TASKS_PATH = "".join([APP_PATH, "\\pybox\\tasks\\"])

LOGGING_CONFIG = "".join([APP_PATH, "\\config.yml"])


with open(LOGGING_CONFIG, 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)
logging.config.dictConfig(config)
