#!/usr/bin/env python
from pybox.tools.scraper.news_reader import NewsReader

import datetime


class ReutersNewsReader(NewsReader):

    def __init__(self, start_date):
        super().__init__()
        try:
            self.start_date = datetime.datetime.strptime(
                start_date, '%Y-%m-%d %H:%M')
        except ValueError:
            self.start_date = datetime.datetime.strptime(
                start_date, '%Y-%m-%d')

    def separate_news_section(self):
        pass

    def read_news(self):
        pass
