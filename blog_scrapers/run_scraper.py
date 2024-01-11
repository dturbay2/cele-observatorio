"""
Scrapers for Policy Blogs
"""
from BlogScraper import *


class GoogleScraper(BlogScraper):

    NAME = 'google'
    RESULT_ID = 'feed-article'
    URL_ID = 'feed-article__overlay'
    TITLE_ID = 'feed-article__title'
    DATE_ID = 'uni-timesince'
    CAT1_ID = 'eyebrow__tag'
    BLOGPOST_CONTENT_ID = 'article-container__wrapper'
    URL = 'https://blog.google/outreach-initiatives/public-policy'
    LOCAL_HTML_PATH = 'source_html/google_blog_src.html'
    HEADER = ['date', 'title', 'category', 'url', 'post_text']


    def parse_result(self, result):
        """parses result from blog page into list of fields"""
        category = self.get_content(result, 'a', self.CAT1_ID, get_text=True)
        title = self.get_content(result, 'h3', self.TITLE_ID, get_text=True)
        date = self.get_content(result, 'time', self.DATE_ID, get_text=False)['datetime']
        url = self.get_content(result, 'a', self.URL_ID)['href']
        post_text = self.get_blog_context(url, self.BLOGPOST_CONTENT_ID) if DETAILED_VERSION else ''
        return [date, title, category, url, post_text]


class FacebookScraper(BlogScraper):

    NAME = 'fb'
    RESULT_ID = '_9vxg _9w4f'
    TITLE_ID = '_9vxq'
    URL_ID = '_9vxl'
    CAT1_ID = '_9vxp'
    CAT2_ID = '_9wia _9wlj'
    DATE_ID = '_9vxs'
    BLOGPOST_CONTENT_ID = '_93-i _93-p'
    URL = 'https://www.facebook.com/formedia/blog'
    LOCAL_HTML_PATH = 'source_html/fb_blog_src.html'
    HEADER = ['date', 'title', 'cat1', 'cat2', 'url', 'post_text']


    def parse_result(self, result):
        """parses result from blog page into list of fields"""
        date = self.get_content(result, 'div', self.DATE_ID, get_text=True)
        title = self.get_content(result, 'div', self.TITLE_ID, get_text=True)
        cat1 = self.get_content(result, 'div', self.CAT1_ID, get_text=True)
        cat2 = self.get_content(result, 'a', self.CAT2_ID, get_text=True)
        url = self.get_content(result, 'a', self.URL_ID, get_text=False)['href']
        post_text = self.get_blog_context(url, self.BLOGPOST_CONTENT_ID) if DETAILED_VERSION else ''
        return [date, title, cat1, cat2, url, post_text]


class TwitterScraper(BlogScraper):

    NAME = 'twitter'
    RESULT_ID = 'result'
    URL_ID = None
    TITLE_ID = 'result__title'
    DATE_ID = None
    CAT1_ID = 'result__topic'
    AUTHOR_ID = 'bl14__author'
    BLOGPOST_CONTENT_ID = 'bl13-rich-text-editor'
    URL = 'https://blog.twitter.com'
    LOCAL_HTML_PATH = 'source_html/twitter_blog_src.html'
    HEADER = ['date', 'title', 'topic', 'author', 'path', 'post_text']


    def parse_result(self, result):
        """parses result from blog page into list of fields"""
        topic = self.get_content(result, 'span', self.CAT1_ID, get_text=True)
        title = self.get_content(result, 'a', self.TITLE_ID, get_text=True)
        url = self.get_content(result, 'a', self.TITLE_ID)['href']
        author = self.get_content(result, 'span', self.AUTHOR_ID, get_text=True)
        date = result.find('time').getText()
        post_text = self.get_blog_context(url, self.BLOGPOST_CONTENT_ID) if DETAILED_VERSION else ''
        return [date, title, topic, author, url, post_text]


if __name__ == "__main__":

    twitter = TwitterScraper()
    twitter.scrape_data()

    google = GoogleScraper()
    google.scrape_data()

    fb = FacebookScraper()
    fb.scrape_data()
