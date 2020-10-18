#!/usr/bin/env python
from pybox.GLOBALS import EXTERNALS_PATH, DATA_PATH
from pybox.tools.data.data_table import DataTable
from pybox.tools.data.data_helpers import to_datetime

import logging
import os
import re
import sys
import traceback
from abc import ABC, abstractproperty
from datetime import datetime, date
from importlib import import_module
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep


def emergency_data_protector(function):
    """[summary]

    Args:
        function ([type]): [description]
    """

    def wrapper(self, *args, **kwargs):
        try:
            function(self, *args, **kwargs)
        except Exception:
            exception_traceback = traceback.format_exc()
            self._news_to_parquet(self.last_story_date)
            logging.error(
                "Occurred error, collected stories were saved in data folder.")
            print(exception_traceback)
            sys.exit()
    return wrapper


class NewsReader(ABC):
    """[summary]"""

    def __init__(self, web_page, oldest_news_date=None, newest_news_date=None):
        self.web_page = web_page
        if not newest_news_date:
            self.newest_news_date = datetime.combine(
                date.today(), datetime.max.time())
        else:
            self.newest_news_date = to_datetime(newest_news_date)
        if not oldest_news_date:
            self.oldest_news_date = to_datetime(date.today())
        else:
            self.oldest_news_date = to_datetime(oldest_news_date)

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

                # Transforming all camel case keys to snake case.
                reader_settings = {
                    re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower(): value
                    for key, value in reader_settings.items()
                }
                return child_classes[0](**reader_settings)

    @abstractproperty
    @emergency_data_protector
    def read_news_headlines(self):
        """[summary]"""
        pass

    @abstractproperty
    def retrieve_story_content(self):
        """Class property which extracts the detailed parts of a specific
        story and saves them in a DataTable object named `news_data`.
        """
        pass

    def save_story(self, story_date, label, headline, story_address, body):
        """[summary]

        Args:
            story_date ([type]): [description]
            label ([type]): [description]
            headline ([type]): [description]
            story_address ([type]): [description]
            body ([type]): [description]
        """
        self.news_data.insert_row(
            [story_date, label, headline, story_address, body])

        if len(headline) > 50:
            truncated_headline = f"{headline[:50]}.."
        else:
            truncated_headline = headline + " "*(52-len(headline))
        logging.info(
            f"{truncated_headline} from {story_date.strftime('%Y-%m-%d %H:%M')} stored")

    def news_to_parquet(self, directory):
        """[summary]

        Args:
            directory ([type], optional): [description]. Defaults to DATA_PATH.
        """
        self._news_to_parquet(
            self,
            self.oldest_news_date,
            directory)

    def _news_to_parquet(self, ending_date, directory=DATA_PATH):
        file_name = "".join([
            self.source_indicator, "(",
            self.newest_news_date.strftime("%Y_%m_%d_%H_%M"), ",",
            ending_date.strftime("%Y_%m_%d_%H_%M"), ")"
        ])
        self.news_data.to_parquet(file_name, directory)

    def setup_driver(self, page_address):
        """[summary]

        Args:
            page_address (str): [description]
        """
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(
            EXTERNALS_PATH + "/chromedriver.exe", options=options)
        self.driver.get(page_address)

    def accept_cookies(self, accept_button):
        """[summary]

        Args:
            accept_button ([type]): [description]
        """
        try:
            sleep(2)
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
        sleep(2)

    def handle_story_exception(self, story_link):
        """[summary]

        Args:
            story_link ([type]): [description]
        """
        logging.warning(
            f"There has been problem with storage of story:\n\t{story_link}")

    @property
    def switch_to_new_tab(self):
        """[summary]"""
        self.driver.switch_to.window(self.driver.window_handles[1])

    @property
    def close_new_tab(self):
        """[summary]"""
        self.driver.close()
        self.driver.switch_to.window(self.main_window)
