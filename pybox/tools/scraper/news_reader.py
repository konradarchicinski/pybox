#!/usr/bin/env python
from pybox.GLOBALS import EXTERNALS_PATH, DATA_PATH
from pybox.tools.data.data_table import DataTable
from pybox.tools.data.data_helpers import to_datetime, camel_to_snake_case

import logging
import os
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
                children = NewsReader.__subclasses__()
                for child in children:
                    if child.__name__ == f"NewsReader{source}":
                        reader_settings = {camel_to_snake_case(key): value
                                           for key, value in reader_settings.items()}
                        return child(**reader_settings)
                    else:
                        raise ValueError((
                            f"Module `{module}` has been inspected but no proper"
                            " implementation of `NewsReader` was found there."))
        raise ValueError(
            f"No suitable NewsReader implementation was found for `{source}`.")

    @abstractproperty
    @emergency_data_protector
    def read_news_headlines(self):
        """Locate a list of news headlines on the provided website, iterate
        over them, selecting only those whose publication date is within
        the specified date range initialized in class settings.
        """
        pass

    @abstractproperty
    def retrieve_story_content(self):
        """Extract the detailed parts of a specific story and saves them
        in the DataTable object named `news_data`.
        """
        pass

    def setup_driver(self, page_address):
        """Setup Selenium WebDriver which drives a browser natively, as a user
        would, either locally or on a remote machine using the Selenium server.

        Args:

            page_address (str): address of the website to open by the driver.
        """
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(
            EXTERNALS_PATH + "/chromedriver.exe", options=options)
        self.driver.get(page_address)

    def accept_cookies(self, acceptance_button):
        """Find on the website banner displayed regarding the use of cookies
        and accept its terms.

        Args:

            accept_button (str): id tag of the cookies acceptance button.
        """
        try:
            sleep(2)
            self.driver.find_element_by_id(acceptance_button).click()
        except Exception:
            pass

    def open_headline_in_new_tab(self, thumbnail):
        """Open provided headline from hyperlink hidden in thumbnail.
        Headline is opened in a new browser tab in the background.

        Args:

            thumbnail (selenium object): page fragment containing story thumbnail.
        """
        thumbnail.find_element_by_tag_name(
            "a").send_keys(Keys.CONTROL + Keys.RETURN)

    def go_to_next_page(self, navigation_button):
        """Move to the next page of the website using the navigation button.

        Args:

            navigation_button (str): name of the class assigned to the
                navigation button that launches the next page.
        """
        self.driver.find_element_by_class_name(navigation_button).click()
        sleep(2)

    def handle_story_exception(self, story_link, story_problems=None):
        """Handle missing items of given story allowing the program to continue
        without interruption.

        Args:

            story_link (str): story web address.
            story_problems (list, optional): list of story items names for which
                problems occurred. Defaults to None.
        """
        if story_problems:
            info_fragment = ", ".join(story_problems)
        else:
            info_fragment = "storage"
        logging.warning(
            f"There has been problem with {info_fragment} of a story:\n\t{story_link}")

    def collect_story(self, story_date, label, headline, story_address, body):
        """Collect items from the story, add them to the DataTable `news_data`
        and display the success log message.

        Args:

            story_date (datetime): date with time of publication of the story.
            label (str): story label.
            headline (str): story headline.
            story_address (str): story web address.
            body (str): main story content.
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
        """Save collected data from `data_news` to a parquet file in the
        given location. The file will be saved under a name:
            `source_indicator(starting_date,ending_date)`.

        Args:

            ending_date (datetime, optional): date of the oldest collected story,
                used only in emergency data storing. Defaults to None.
            data_directory (str, optional): directory under which the file will
                be saved. Defaults to DATA_PATH.
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
        """Switch the browser tab to the nearest open one."""
        self.driver.switch_to.window(self.driver.window_handles[1])

    @property
    def close_new_tab(self):
        """Close the newly opened browser tab with the focus on it."""
        self.driver.close()
        self.driver.switch_to.window(self.main_window)
