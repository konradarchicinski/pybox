#!/usr/bin/env python
from pybox.GLOBALS import EXTERNALS_PATH, GLOBAL_DATA_PATH
from pybox.datastore.data_table import DataTable
from pybox.helpers.text import camel_to_snake_case
from pybox.helpers.date import to_datetime

import logging
import os
import traceback
import sys
import time
from abc import ABC, abstractproperty
from datetime import datetime, date
from importlib import import_module
from selenium.webdriver import Chrome, ChromeOptions, Firefox, FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from msedge.selenium_tools import Edge, EdgeOptions


def emergency_data_protector(function):
    """Decorator used to secure the collected data in a given function.

    While scraping the website, many unexpected exceptions can appear,
    the encountered error stops the program and contributes to the loss
    of previously scraped information.

    This decorator wraps a given function by a try statement, which,
    when an error is encountered before the program exits, saves
    the previously collected data into the drive.
    """

    def wrapper(self, *args, **kwargs):
        try:
            function(self, *args, **kwargs)
        except Exception:
            exception_traceback = traceback.format_exc()
            self.news_to_parquet(self.data_path)
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

    def __init__(self, driver_type="Chrome", oldest_news_date=None, 
                 newest_news_date=None):
        if not newest_news_date:
            self.newest_news_date = datetime.combine(
                date.today(), datetime.max.time())
        else:
            self.newest_news_date = to_datetime(newest_news_date)
        if not oldest_news_date:
            self.oldest_news_date = to_datetime(date.today())
        else:
            self.oldest_news_date = to_datetime(oldest_news_date)

        self.driver_type = driver_type
        self.news_data = DataTable(
            names=["PageAddress", "LastModificationDate",
                   "PublishingDate", "Label", "Headline", "Body"],
            dtypes=[str, datetime, datetime, str, str, str])

    @staticmethod
    def initiate(source, reader_settings=None, data_path=GLOBAL_DATA_PATH):
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
            data_path (str): place to store news data. Defaults to GLOBAL_DATA_PATH.
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
                        scraper = child(**reader_settings)
                        scraper.source = source
                        scraper.data_path = data_path
                        return scraper
                raise ValueError((
                    f"Module `{module}` has been inspected but no proper"
                    " implementation of `NewsReader` was found there."))
        raise ValueError(
            f"No suitable NewsReader implementation was found for `{source}`.")

    @abstractproperty
    @emergency_data_protector
    def read_news(self):
        """Locate a list of news headlines on the provided website and store them
        in GLOBAL_DATA_PATH folder. Function iterates over found healines list, selecting
        only those whose publication date is within the specified date range
        initialized in class settings.
        """
        pass

    @abstractproperty
    @emergency_data_protector
    def read_archival_news(self):
        """Locate a list of news headlines from the xml sitemap data of provided
        webpage source and store them in GLOBAL_DATA_PATH folder. Only those articles
        whose last modification date is within the specified date range,
        initialized in class settings, are stored.
        """
        pass

    @abstractproperty
    def retrieve_news_content(self):
        """Extract the detailed parts of a specific news and saves them
        in the DataTable object named `news_data`.
        """
        pass

    def setup_driver(self, main_page):
        """Setup Selenium WebDriver which drives a browser natively, as a user
        would, either locally or on a remote machine using the Selenium server.

        Args:

            main_page(str): main page address.
        """
        if sys.platform in ["win32", "win64"]:
            driver_suffix = "_win.exe"
        elif sys.platform.startswith("linux"):
            driver_suffix = "_linux"

        if self.driver_type == "Edge":
            options = EdgeOptions()
            options.use_chromium = True
            options.add_experimental_option("excludeSwitches",
                                            ["enable-logging"])
            self.driver = Edge(
                executable_path=f"{EXTERNALS_PATH}/msedgedriver{driver_suffix}",
                options=options)
        elif self.driver_type == "Chrome":
            options = ChromeOptions()
            options.use_chromium = True
            options.add_experimental_option('excludeSwitches',
                                            ['enable-logging'])
            self.driver = Chrome(
                executable_path=f"{EXTERNALS_PATH}/chromedriver{driver_suffix}",
                options=options)
        elif self.driver_type == "Firefox":
            options = FirefoxOptions()
            self.driver = Firefox(
                executable_path=f"{EXTERNALS_PATH}/geckodriver{driver_suffix}",
                options=options)       
        else:
            raise ValueError(
                f"Not known type of the provided driver: {self.driver_type}")
        self.driver.get(main_page)

    def accept_consent_form(self, button_id):
        """Clicks on the acceptance button of consent form agreement
        showing up on the certain webpage.

        Args:

            button_id (str): identificator of the acceptance button.
        """
        time.sleep(15)
        try:
            accept_button = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.ID, button_id)))
            accept_button.click()
        except BaseException:
            pass

    def handle_news_exception(self, news_link, news_problems=None):
        """Handle missing items of given news allowing the program to continue
        without interruption.

        Args:

            news_link (str): news web address.
            news_problems (list, optional): list of news items names for which
                problems occurred. Defaults to None.
        """
        if news_problems:
            info_fragment = ", ".join(news_problems)
        else:
            info_fragment = "storage"
        logging.warning(
            f"There has been problem with {info_fragment} of a news:\n\t{news_link}")

    def store_news(self, page_address, last_modification_date=None,
                   publishing_date=None, label=None, headline=None, body=None):
        """Store items from the news, add them to the DataTable `news_data`
        and display the success log message.

        Args:

            page_address (str): web address of the news.
            last_modification_date (datetime, optional): date of the news last
                modification. Defaults to None.
            publishing_date (datetime, optional): date of the news publication.
                Defaults to None.
            label (str, optional): internal label from the article source page.
                Defaults to None.
            headline (str, optional): headline of the news. Defaults to None.
            body (str, optional): main news content, containing all news
                paragraphs. Defaults to None.
        """
        self.news_data.insert_row(
            [page_address, last_modification_date,
             publishing_date, label, headline, body])

        if headline is None:
            headline = "ARTICLE_WITHOUT_HEADLINE"

        if len(headline) > 50:
            truncated_headline = f"{headline[:50]}.."
        else:
            truncated_headline = headline + " "*(52-len(headline))
        logging.info(
            (f"{truncated_headline} from "
             f"{last_modification_date.strftime('%Y-%m-%d %H:%M')} stored"))

    def news_to_parquet(self, data_directory=GLOBAL_DATA_PATH):
        """Save collected data from `data_news` to a parquet file in the
        given location. The file will be saved under a name:
            `source(oldest_date,newest_date)`.

        Args:

            data_directory (str, optional): directory under which the file will
                be saved. Defaults to GLOBAL_DATA_PATH.
        """
        oldest_date = self.news_data['LastModificationDate', -1]
        newest_date = self.news_data['LastModificationDate', 0]

        file_name = "".join(
            [self.source, "(",
             oldest_date.strftime("%Y_%m_%d_%H_%M"), ",",
             newest_date.strftime("%Y_%m_%d_%H_%M"), ")"])
        self.news_data.to_parquet(file_name, data_directory)
