#!/usr/bin/env python
from pybox.tools.scraper.news_reader import NewsReader
from pybox.tools.data.data_helpers import to_datetime


class NewsReaderReuters(NewsReader):
    """[summary]"""

    def __init__(self, main_web_page=None, min_news_date=None, max_news_date=None):
        if not main_web_page:
            main_web_page = "https://uk.reuters.com/news/archive"
        super().__init__(main_web_page, min_news_date, max_news_date)

    @property
    def read_news_headlines(self):
        """[summary]"""
        self.setup_driver(self.main_web_page)
        self.accept_cookies(accept_button="_evidon-banner-acceptbutton")
        self.main_window = self.driver.current_window_handle

        self.last_story_date = self.max_news_date
        while self.last_story_date >= self.min_news_date:
            stories = self.driver.find_elements_by_tag_name("article")
            for story in stories:
                story_update_date = to_datetime(
                    story.find_element_by_tag_name("time").text)
                if self.max_news_date >= story_update_date:
                    self.open_headline_in_new_tab(
                        instance_to_open=story.find_element_by_tag_name("a"))
                    self.switch_to_new_tab
                    self.retrieve_story_content
                    self.close_new_tab
            self.move_to_next_page(navigation_button="control-nav-next")

        self.driver.close()

    @property
    def retrieve_story_content(self):
        """[summary]"""
        story_info_bar = self.driver.find_element_by_css_selector(
            "div[class^='ArticleHeader']")
        # TODO write an explanation.
        time_tags = story_info_bar.find_elements_by_tag_name('time')[:2]
        self.last_story_date = to_datetime(
            " ".join([time.text for time in time_tags]))

        if self.last_story_date >= self.min_news_date:
            label = story_info_bar.find_element_by_tag_name('a').text
            headline = self.driver.find_element_by_css_selector(
                "h1[class^='Headline']").text
            story_address = self.driver.current_url
            paragraphs = self.driver.find_elements_by_css_selector(
                "p[class^='Paragraph']")
            body = "\n".join([p.text for p in paragraphs])

            self.news_data.insert_row(
                [self.last_story_date, label, headline, story_address, body])
