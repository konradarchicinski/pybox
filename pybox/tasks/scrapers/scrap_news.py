#!/usr/bin/env python
from pybox.GLOBALS import DATA_PATH
from pybox.tools.task import TaskInit
from pybox.tools.scraper.news_reader import NewsReader

from datetime import date, timedelta


def scrap_news(settings):
    """Main task function. It creates `NewsReader` instance which
    is used to scrap and store stories from webpage supplied
    in the settings.

    Args:

        settings (dict): contains settings of this task.
    """
    source = settings["Source"]
    reader_settings = {key: settings[key]
                       for key in settings if key != "Source"}

    reader = NewsReader.initiate(source, reader_settings)
    reader.read_news_headlines
    reader.news_to_parquet(data_directory=DATA_PATH)


task = TaskInit(
    task_name="NewsScrap",
    task_info="""
    Task scraps and stores news/stories from supplied webpage.
    """)
task.add_setting(
    name="Source",
    value="Reuters",
    info="""
    The name of the source webpage such as `Reuters` or `Bloomberg`.
    """)
task.add_setting(
    name="WebPage",
    value="",
    info="""
    Main webpage of source that is going to be scraped.
    """)
task.add_setting(
    name="PageType",
    value="businessnews",
    info="""
    Subpage of source webpage which can wider range of topics.
    """)
task.add_setting(
    name="NewestNewsDate",
    value=str(date.today()),
    info="""
    Date representing newest news that can be stored.
    """)
task.add_setting(
    name="OldestNewsDate",
    value=str(date.today() - timedelta(days=1)),
    info="""
    Date representing oldest news that can be stored.
    """)
task.run(main_function=scrap_news)
