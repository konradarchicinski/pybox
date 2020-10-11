#!/usr/bin/env python
from pybox.tools.scraper.news_reader import NewsReader
from pybox.tools.data.data_helpers import to_date

from time import sleep
from selenium.webdriver.common.keys import Keys


class NewsReaderReuters(NewsReader):
    """[summary]"""

    def __init__(self, start_date, reuters_page=None):
        super().__init__()
        self.start_date = to_date(start_date, "datetime")
        if not reuters_page:
            self.reuters_page = "https://www.reuters.com/theWire"

    @property
    def read_news_headlines(self):
        """[summary]"""
        self.setup_driver(self.reuters_page)
        self.accept_cookies

        main_window = self.driver.current_window_handle

        stories = self.driver.find_elements_by_tag_name("article")
        for story in stories:

            story.find_element_by_tag_name("a").send_keys(
                Keys.CONTROL + Keys.RETURN)

            self.driver.switch_to.window(self.driver.window_handles[1])
            self.retrive_headline_content

            self.driver.close()
            self.driver.switch_to.window(main_window)

        self.driver.close()
        # TODO finish collecting articles:
        #   - add switching to the next (archive) pages of headlines
        #     until the scraper reaches the start date.

    @property
    def retrive_headline_content(self):
        """[summary]"""
        info_bar = self.driver.find_element_by_css_selector(
            "div[class^='ArticleHeader']")

        time_tags = info_bar.find_elements_by_tag_name('time')[:2]
        story_date = to_date(
            " ".join([time.text for time in time_tags]), "datetime")
        # TODO validate the date transformation.
        if story_date > self.start_date:
            label = info_bar.find_element_by_tag_name('a').text

            headline = self.driver.find_element_by_css_selector(
                "h1[class^='Headline']").text

            story_address = self.driver.current_url

            paragraphs = self.driver.find_elements_by_css_selector(
                "p[class^='Paragraph']")
            body = "\n".join([p.text for p in paragraphs])

            self.news_data.insert_row(
                [story_date, label, headline, story_address, body])

    @property
    def accept_cookies(self):
        """Accepts page cookies usage."""
        try:
            sleep(3)
            self.driver.find_element_by_id(
                "_evidon-banner-acceptbutton").click()
        except Exception:
            pass
