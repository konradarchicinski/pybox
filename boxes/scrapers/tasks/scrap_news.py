#!/usr/bin/env python
from boxes.scrapers import DATA_PATH
from pybox.tools.task import Task
from pybox.tools.scraper.news_reader import NewsReader

from datetime import date, timedelta, datetime


def update_reader_settings(iteration, reader_settings):
    """Auxiliar function, returns the settings passed to the reader
    with updated dates. Updated dates are shifted always by the same
    interval defined by the difference between NewestNewsDate and
    the OldestNewsDate.

    Args:

        iteration (int): number of current iteration.
        reader_settings (dict): contains reader settings to be updated.
    """
    if iteration > 0:
        newest_news_date = datetime.strptime(
            reader_settings["NewestNewsDate"], "%Y-%m-%d")
        oldest_news_date = datetime.strptime(
            reader_settings["OldestNewsDate"], "%Y-%m-%d")
        delta = newest_news_date - oldest_news_date

        reader_settings["OldestNewsDate"] = str(
            (oldest_news_date - delta).date())
        reader_settings["NewestNewsDate"] = str(
            (newest_news_date - delta).date())

    return reader_settings


def scrap_news(settings):
    """Main task function. It creates `NewsReader` instance which
    is used to scrap and store stories from webpage supplied
    in the settings.

    Args:

        settings (dict): contains settings of this task.
    """
    source = settings["Source"]
    additional_interval = settings["AdditionalInterval"]
    reader_settings = {key: settings[key]
                       for key in settings
                       if key not in ["Source", "AdditionalInterval"]}

    for iteration in range(1 + additional_interval):
        reader_settings = update_reader_settings(iteration, reader_settings)

        reader = NewsReader.initiate(source, reader_settings, DATA_PATH)
        reader.read_archival_news
        reader.news_to_parquet(DATA_PATH)


task = Task(
    task_name="NewsScrap",
    task_info="""
    Task scraps and stores news/stories from supplied webpage.
    """)
task.add_setting(
    name="Source",
    default_value="Reuters",
    info="""
    The name of the source webpage such as `Reuters` or `Bloomberg`.
    """)
task.add_setting(
    name="NewestNewsDate",
    default_value=str(date.today()),
    info="""
    Date representing newest news that can be stored.
    """)
task.add_setting(
    name="OldestNewsDate",
    default_value=str(date.today() - timedelta(days=1)),
    info="""
    Date representing oldest news that can be stored.
    """)
task.add_setting(
    name="AdditionalInterval",
    default_value=0,
    info="""
    Number of additional intervals. It provides functionality
    to scrap data from older dates (shifted with the same interval
    as one between dates provided in initial settings).
    """)
task.run(main_function=scrap_news)
