#!/usr/bin/env python
from pybox.scraper.news_reader import NewsReader, emergency_data_protector
from pybox.helpers.date import to_datetime, create_dates_list
from pybox.datastore.data_flow import dict_from_xml

import time


class NewsReaderReuters(NewsReader):
    """The class is a `NewsReader` implementation for the Reuters website.

    It is used to collect and save news from particular Reuters page.
    The class can be provided with a set of settings specifying its action.
    However, it is an optional functionality.

    Acceptable setting:

        - OldestNewsDate (str, date): date specifying the date of the last
            accepted news.
        - NewestNewsDate (str, date): date specifying the date of the most
            recent acceptable news.
    """

    @property
    @emergency_data_protector
    def read_news(self):
        """Locate a list of news headlines on the provided website and store them
        in DATA_PATH folder. Function iterates over found healines list, selecting
        only those whose publication date is within the specified date range
        initialized in class settings.
        """
        # TODO create functionality.
        return "Functionality has not been implemented yet."

    @property
    @emergency_data_protector
    def read_archival_news(self):
        """Locate a list of news headlines from the xml sitemap data of provided
        webpage source and store them in DATA_PATH folder. Only those articles
        whose last modification date is within the specified date range,
        initialized in class settings, are stored.
        """
        self.setup_driver(main_page="https://www.reuters.com/")
        self.accept_consent_form("accept-recommended-btn-handler")

        for web_address in self.xml_web_addresses:
            news_info_list = dict_from_xml(web_address, branch="/urlset/url")

            for news_info in news_info_list:
                self.news_content = dict()
                self.news_content["page_address"] = news_info["loc"]
                self.news_content["last_modification_date"] = to_datetime(
                    news_info["lastmod"])
                self.driver.get(self.news_content["page_address"])
                self.retrieve_news_content
                self.store_news(**self.news_content)

        self.driver.quit()

    @property
    def retrieve_news_content(self):
        """Extract the detailed parts of a specific news and saves them
        in the DataTable object named `news_data`.

        The collected content of a specific article may be: page_address,
        last_modification_date, publishing_date, label, headline and body.
        """
        time.sleep(0.25)
        try:
            news_info_bar = self.driver.find_element_by_css_selector(
                "div[class*='ArticleHeader']")
            # Usually there are three `time` tags in this part of page.
            # The first is a date, the second is a time and the third
            # determines the time since the last update. By default,
            # only first two are interesting.
            time_tags = news_info_bar.find_elements_by_tag_name('time')[:2]
            self.news_content["publishing_date"] = to_datetime(" ".join(
                [time.text for time in time_tags]))

            # In some articles the label can be found under the `a` tag,
            # in others it is under the `p` tag. Determining it as follows
            # worked in both cases. In the info bar, the label is separated
            # by the `\n` sign, therefore dividing the entire bar with its
            # help enables a simple and universal selection of the label.
            self.news_content["label"] = news_info_bar.text.split("\n", 1)[0]
            self.news_content[
                "headline"] = self.driver.find_element_by_css_selector(
                    "h1[class^='Headline']").text

            body_wrapper = self.driver.find_element_by_css_selector(
                "div[class*='ArticleBodyWrapper']")
            # In most cases, article texts are stored either in paragraphs
            # or in preformatted text, table-like tags.
            paragraphs = body_wrapper.find_elements_by_css_selector(
                "p[class^='Paragraph']")
            preformatteds = body_wrapper.find_elements_by_tag_name("pre")
            self.news_content["body"] = "\n".join(
                [p.text for p in paragraphs + preformatteds])

            news_problems = [
                key for key, value in self.news_content.items() if not value
            ]
            if news_problems:
                self.handle_news_exception(self.news_content["page_address"],
                                           news_problems)

        except Exception:
            self.handle_news_exception(self.news_content["page_address"])

    @property
    def xml_web_addresses(self):
        """Return a list of xml web addresses from Reuters archives.

        The content of each xml file located at a given address is a basic
        information about all articles published on a given day.

        E.g. mentioned link with the information about all articles posted
        on Reuters on 2020-01-01 looks like:

            `https://www.reuters.com/sitemap_20200101-20200102.xml`
        """
        dates_list = create_dates_list(self.newest_news_date,
                                       self.oldest_news_date)

        addresses = list()
        for idx in range(len(dates_list) - 1):
            xml_web_address = ("https://www.reuters.com/sitemap_"
                               f"{dates_list[idx+1].strftime('%Y%m%d')}-"
                               f"{dates_list[idx].strftime('%Y%m%d')}.xml")
            addresses.append(xml_web_address)
        return addresses
