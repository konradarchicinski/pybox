#!/usr/bin/env python
from pybox.tools.scraper.news_reader import NewsReader, emergency_data_protector
from pybox.tools.data.data_helpers import to_datetime


class NewsReaderReuters(NewsReader):
    """The class is `NewsReader` implementation for the Reuters website.

    It is used to collect and save news from particular Reuters subpages.
    The class can be provided with a set of settings specifying its action.
    However, it is an optional functionality.

    Acceptable setting:

        - WebPage (str): full link of the page from which the collection
            of the news will be started.
        - PageType (str): type that helps identify Reuters subpage without
            using the full link. The proven page types are: `businessnews`,
            `marketsnews`, `worldnews`, `technologynews`, `lifestylemolt`.
        - OldestNewsDate (str, date): date specifying the date of the last
            accepted article.
        - NewestNewsDate (str, date): date specifying the date of the most
            recent acceptable article.
    """

    def __init__(self, page_type=None, web_page=None,
                 oldest_news_date=None, newest_news_date=None):
        if not page_type:
            page_type = ""
        if not web_page:
            web_page = f"https://uk.reuters.com/news/archive/{page_type}"

        self.source_indicator = f"Reuters{page_type.title()}"

        super().__init__(web_page, oldest_news_date, newest_news_date)

    @property
    @emergency_data_protector
    def read_news_headlines(self):
        """Class property, which locates a list of news headlines on the
        provided website, iterates over them, looking at those whose publication
        date is within the specified date range initialized in class settings.
        """
        self.setup_driver(self.web_page)
        self.accept_cookies(accept_button="_evidon-banner-acceptbutton")

        # The variable is initially assigned the value of the boundary
        # of the considered date range of articles. In the further part
        # of the code it will be overwritten multiple times.
        last_viewed_story_date = self.newest_news_date

        while last_viewed_story_date >= self.oldest_news_date:
            self.main_window = self.driver.current_window_handle
            # Links to articles may appear in different places of the page,
            # but from the perspective of this class, only one from the
            # headlines list are interesting. Therefore, first a list of
            # headlines is searched and only from it individual articles
            # are selected.
            stories_list = self.driver.find_element_by_class_name(
                "news-headline-list").find_elements_by_tag_name("article")
            for story in stories_list:
                last_viewed_story_date = to_datetime(
                    story.find_element_by_tag_name("time").text)
                # Each article is pre-checked for publication date before opening.
                # If date is outside the class's date range, the article is skipped.
                if self.newest_news_date > last_viewed_story_date >= self.oldest_news_date:
                    self.open_headline_in_new_tab(
                        instance_to_open=story.find_element_by_tag_name("a"))
                    self.switch_to_new_tab
                    self.retrieve_story_content
                    self.close_new_tab
            self.move_to_next_page(navigation_button="control-nav-next")

        self.driver.close()

    @property
    def retrieve_story_content(self):
        """Class property which extracts the detailed parts of a specific
        story and saves them in a DataTable object named `news_data`.

        Its scope is to find story elements on the webpage such as:
        datetime, label, headline, page address and text body.
        """
        story_address = self.driver.current_url
        try:
            story_info_bar = self.driver.find_element_by_css_selector(
                "div[class*='ArticleHeader']")
            # Usually there are three `time` tags in this part of page.
            # The first is a date, the second is a time and the third
            # determines the time since the last update. By default,
            # only first two are interesting.
            time_tags = story_info_bar.find_elements_by_tag_name('time')[:2]
            self.last_story_date = to_datetime(
                " ".join([time.text for time in time_tags]))

            if self.newest_news_date > self.last_story_date >= self.oldest_news_date:
                # In some articles the label can be found under the `a` tag,
                # in others it is under the `p` tag. Determining it as follows
                # worked in both cases. In the info bar, the label is separated
                # by the `\n` sign, therefore dividing the entire bar with its
                # help enables a simple and universal selection of the label.
                label = story_info_bar.text.split("\n", 1)[0]
                headline = self.driver.find_element_by_css_selector(
                    "h1[class^='Headline']").text
                paragraphs = self.driver.find_elements_by_css_selector(
                    "p[class^='Paragraph']")
                body = "\n".join([p.text for p in paragraphs])

                self.save_story(self.last_story_date, label,
                                headline, story_address, body)
        except Exception:
            self.handle_story_exception(story_address)
