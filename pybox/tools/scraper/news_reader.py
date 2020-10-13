#!/usr/bin/env python
from pybox.GLOBALS import APP_PATH
from pybox.tools.data.data_table import DataTable
from pybox.tools.data.data_helpers import to_datetime

import os
from abc import ABC, abstractproperty
from datetime import datetime, date
from importlib import import_module
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep


class NewsReader(ABC):
    """[summary]"""

    def __init__(self, main_web_page, min_news_date=None, max_news_date=None):
        self.main_web_page = main_web_page
        if not max_news_date:
            self.max_news_date = datetime.max
        else:
            self.max_news_date = to_datetime(max_news_date)
        if not min_news_date:
            self.min_news_date = to_datetime(date.today())
        else:
            self.min_news_date = to_datetime(min_news_date)

        self.main_window = None

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

    def accept_cookies(self, accept_button):
        """[summary]

        Args:
            accept_button ([type]): [description]
        """
        try:
            sleep(3)
            self.driver.find_element_by_id(accept_button).click()
        except Exception:
            pass

    def open_headline_in_new_tab(self, instance_to_open):
        """[summary]

        Args:
            instance_to_open ([type]): [description]
        """
        instance_to_open.send_keys(Keys.CONTROL + Keys.RETURN)

    def move_to_next_page(self, navigation_button):
        """[summary]

        Args:
            navigation_button ([type]): [description]
        """
        self.driver.find_element_by_class_name(navigation_button).click()

    @property
    def switch_to_new_tab(self):
        """[summary]"""
        self.driver.switch_to.window(self.driver.window_handles[1])

    @property
    def close_new_tab(self):
        """[summary]"""
        self.driver.close()
        self.driver.switch_to.window(self.main_window)

    @ abstractproperty
    def read_news_headlines(self):
        """[summary]"""
        pass

    @ abstractproperty
    def retrieve_story_content(self):
        """[summary]"""
        pass
