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
    """Decorator used to secure the collected data in a given function.

    While scraping the website, many unexpected exceptions can appear,
    the encountered error stops the program and contributes to the loss
    of previously scraped information.

    This decorator wraps a given function by a try statement, which,
    when an error is encountered before the program exits, saves
    the data previously collected into the drive.
    """

    def wrapper(self, *args, **kwargs):
        try:
            function(self, *args, **kwargs)
        except Exception:
            exception_traceback = traceback.format_exc()
            self.news_to_parquet(ending_date=self.last_story_date)
            logging.error(
                "Occurred error, collected stories were saved in data folder.")
            print(exception_traceback)
            sys.exit()
    return wrapper


class NewsReader(ABC):
    """Abstract class used for news scraping from several different sites.

    Currently implemented news services are: 

        - Reuters

    To initialize a class of a suitable service, one need use the `initiate`
    staticmethod and pass the name of the service as an source argument.
    """

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
        """Return a class instance of a reader implementation for a supplied
        news site source.

        This staticmethod is used to initiate the specific news site implementation
        of the `NewsReader` class. To specify the functionality of a reader,
        a function can be provided with a series of settings supported by the
        selected implementation. The settings should be passed in a dictionary
        as in the example below:

            NewsReader.initiate('Reuters', {'PageType': 'marketsnews'})

        Args:

            source (str): name of the news site whose implementation
                is to be instantiated.
            reader_settings (dict, optional): implementation settings,
                which allow to control reader actions. Defaults to None.
        """
        if not reader_settings:
            reader_settings = dict()
        for module in os.listdir(os.path.dirname(__file__)):
            if module == f"news_reader_{source.lower()}.py":
                import_module(f".{module[:-3]}", __package__)
                child_classes = NewsReader.__subclasses__()
                # TODO rather check name standard = `NewsReader{Source}`.
                if len(child_classes) > 1:
                    raise ValueError((
                        f"Module `{module}` has been inspected"
                        "there was more than one class inside it,"
                        "therefore, it is wrongly constructed."))
                # Transforming all camel case keys to snake case, which enables
                # a function to understand keys as arguments.
                reader_settings = {
                    re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower(): value
                    for key, value in reader_settings.items()
                }
                return child_classes[0](**reader_settings)

    @abstractproperty
    @emergency_data_protector
    def read_news_headlines(self):
        """Class property, which locates a list of news headlines on the provided
        website, iterates over them, selecting only those whose publication
        date is within the specified date range initialized in class settings.
        """
        pass

    @abstractproperty
    def retrieve_story_content(self):
        """Class property which extracts the detailed parts of a specific
        story and saves them in a DataTable object named `news_data`.
        """
        pass

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

    def collect_story(self, story_date, label, headline, story_address, body):
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

    def news_to_parquet(self, ending_date=None, data_directory=DATA_PATH):
        """[summary]

        Args:
            ending_date ([type], optional): [description]. Defaults to None.
            data_directory ([type], optional): [description]. Defaults to DATA_PATH.
        """
        if not ending_date:
            ending_date = self.oldest_news_date
        file_name = "".join([
            self.source_indicator, "(",
            self.newest_news_date.strftime("%Y_%m_%d_%H_%M"), ",",
            ending_date.strftime("%Y_%m_%d_%H_%M"), ")"
        ])
        self.news_data.to_parquet(file_name, data_directory)

    @property
    def switch_to_new_tab(self):
        """[summary]"""
        self.driver.switch_to.window(self.driver.window_handles[1])

    @property
    def close_new_tab(self):
        """[summary]"""
        self.driver.close()
        self.driver.switch_to.window(self.main_window)
