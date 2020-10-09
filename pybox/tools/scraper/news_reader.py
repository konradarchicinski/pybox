#!/usr/bin/env python
import os
import importlib
import datetime
from abc import ABC, abstractmethod

import pybox.tools.data.data_table as btddt


class NewsReader(ABC):

    def __init__(self):
        self.news_data = btddt.DataTable(names=["Date", "Header", "Body"],
                                         dtypes=[datetime.date, str, str])

    def save_news(self):
        # TODO

    def store_page_source(self, page):
        # TODO

    @abstractmethod
    def separate_news_section(self):
        pass

    @abstractmethod
    def read_news(self):
        pass

    @ staticmethod
    def initiate(source, reader_settings=None):
        if not reader_settings:
            reader_settings = dict()
        for module in os.listdir(os.path.dirname(__file__)):
            if module == f"news_reader_{source.lower()}.py":
                importlib.import_module(f".{module[:-3]}", __package__)
                child_classes = NewsReader.__subclasses__()
                if len(child_classes) > 1:
                    raise ValueError(
                        f"Module `{module}` has been inspected",
                        "there was more than one class inside it,",
                        "therefore, it is wrongly constructed."
                    )
                return child_classes[0](**reader_settings)
