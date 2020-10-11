#!/usr/bin/env python
from pybox.GLOBALS import APP_PATH
from pybox.tools.data.data_table import DataTable

import os
from datetime import datetime
from selenium import webdriver
from importlib import import_module
from abc import ABC, abstractproperty


class NewsReader(ABC):
    """[summary]"""

    def __init__(self):
        self.news_data = DataTable(
            names=["Date", "Label", "Headline", "StoryAddress", "Body"],
            dtypes=[datetime, str, str, str, str])

    @staticmethod
    def initiate(source, reader_settings=None):
        """[summary]

        Args:
            source ([type]): [description]
            reader_settings ([type], optional): [description]. Defaults to None.
        """
        if not reader_settings:
            reader_settings = dict()
        for module in os.listdir(os.path.dirname(__file__)):
            if module == f"news_reader_{source.lower()}.py":
                import_module(f".{module[:-3]}", __package__)
                child_classes = NewsReader.__subclasses__()
                # TODO rather check name standard = `NewsReader{Source}`.
                if len(child_classes) > 1:
                    raise ValueError(
                        f"Module `{module}` has been inspected",
                        "there was more than one class inside it,",
                        "therefore, it is wrongly constructed."
                    )
                return child_classes[0](**reader_settings)

    def setup_driver(self, page_address):
        """[summary]

        Args:
            page_address (str): [description]
        """
        self.driver = webdriver.Chrome(APP_PATH + "/chromedriver.exe")
        self.driver.get(page_address)

    @abstractproperty
    def read_news_headlines(self):
        """[summary]"""
        pass

    @abstractproperty
    def retrive_headline_content(self):
        """[summary]"""
        pass
