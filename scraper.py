"""
Structure:

BlogScraper class takes in URL or path with a flag if its local or online
 - Clean up Code
 - refactor constants/settings
 - Add detailed version by fetching blog text
 - Basic Logging

 LOG: start 2:45 EST, 1hr
 LOG: start 4:35 EST, 

"""
from bs4 import BeautifulSoup
import requests
from retry import retry
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

URL_META = 'https://www.facebook.com/formedia/blog'
URL_TWITTER = 'https://blog.twitter.com'
URL_GOOGLE = 'https://blog.google/outreach-initiatives/public-policy'
WAIT_TIME = 2

DETAILED_VERSION = False
DELIMITER = '\t'


# TWITTER CLASS NAMES
TWITTER_RESULT_ID = 'result'
TWITTER_CAT = 'result__topic'
TWITTER_TITLE = 'result__title'
TWITTER_AUTHOR = 'bl14__author'

# FACEBOOK CLASS NAMES
FB_RESULT_ID = '_9vxg _9w4f'
FB_TITLE = '_9vxq'
FB_URL = '_9vxl'
FB_CAT1 = '_9vxp'
FB_CAT2 = '_9wia _9wlj'
FB_DATE = '_9vxs'

# GOOGLE CLASS NAMES
GOOGLE_RESULT_ID = 'feed-article'
GOOGLE_URL = 'feed-article__overlay'
GOOGLE_TITLE = 'feed-article__title'
GOOGLE_DATE = 'uni-timesince'
GOOGLE_CAT = 'eyebrow__tag'


def get_content(soup, tag_type, search_val, search_key='class', find_all=False, get_text=False):
    try:
        if find_all:
            return soup.find_all(tag_type, {search_key: search_val})
        else:
            query = soup.find(tag_type, {search_key: search_val})
            return query.getText() if get_text else query
    except Exception as err:
        print(f"Error finding content: {err}, {type(err)}, returning empty string")
        print(f"Content: tag_type = {tag_type}, Search Key,Val: {search_key}->{search_val} ")
        return ''


def read_page_source_from_file(path: str):
    """read html file to be parsed by for 'manual scraping'"""
    with open(path, "r", encoding='utf-8') as f:
        page_source = f.read()
    return page_source


def write_to_csv(content, output_file):
    with open(output_file, "w", encoding='utf-8') as f:
        f.write(content)


def parse_google_result(result):
    """parses result from blog page into list of fields"""
    category = get_content(result, 'a', GOOGLE_CAT, get_text=True)
    title = get_content(result, 'h3', GOOGLE_TITLE, get_text=True)
    date = get_content(result, 'time', GOOGLE_DATE, get_text=False)['datetime']
    url = get_content(result, 'a', GOOGLE_URL)['href']
    if DETAILED_VERSION:
        post_soup = BeautifulSoup(requests.get(url).text, 'html.parser')
        post_text = get_content(post_soup, 'div', 'bl13-rich-text-editor', get_text=True) # TODO: do fetch result from GOOGLE
    else:
        post_text = ''
    return [date, title, category, url, post_text]


def parse_fb_result(result):
    """parses result from blog page into list of fields"""
    date = get_content(result, 'div', FB_DATE, get_text=True)
    title = get_content(result, 'div', FB_TITLE, get_text=True)
    cat1 = get_content(result, 'div', FB_CAT1, get_text=True)
    cat2 = get_content(result, 'a', FB_CAT2, get_text=True)
    url = get_content(result, 'a', FB_URL, get_text=False)['href']
    if DETAILED_VERSION:
        post_soup = BeautifulSoup(requests.get(url).text, 'html.parser')
        post_text = get_content(post_soup, 'div', 'bl13-rich-text-editor', get_text=True) # TODO: do fetch result from FB
    else:
        post_text = ''
    return [date, title, cat1, cat2, url, post_text]


def parse_twitter_result(result):
    """parses result from blog page into list of fields"""
    topic = get_content(result, 'span', TWITTER_CAT, get_text=True)
    title = get_content(result, 'a', TWITTER_TITLE, get_text=True)
    path = get_content(result, 'a', TWITTER_TITLE)['href']
    author = get_content(result, 'span', TWITTER_AUTHOR, get_text=True)
    date = result.find('time').getText()
    if DETAILED_VERSION:
        post_soup = BeautifulSoup(requests.get(url).text, 'html.parser')
        post_text = get_content(post_soup, 'div', 'bl13-rich-text-editor', get_text=True) # TODO: finalize
    else:
        post_text = ''
    return [date, title, topic, author, path, post_text]


def parse_page_to_records(page_source, parser, result_id, result_type='div'):
    """Parse page-source into list of records"""
    soup = BeautifulSoup(page_source, 'html.parser')
    results = get_content(soup, result_type, result_id, find_all=True)
    records = []
    for result in results:
        values = parser(result)
        records.append(values)
    return records


def mk_parsed_content(header, path, parser, result_id, result_type='div', online=False):
    if online:
        raise NotImplementedError
        page_source = fetch_page_with_lazy_loading(path)
    else:
        page_source = read_page_source_from_file(path)
    data = parse_page_to_records(page_source, parser, result_id, result_type)

    # csv output
    data = [header] + data
    delim_records = [DELIMITER.join(record) for record in data]
    return '\n'.join(delim_records)


if __name__ == "__main__":
    # twitter
    print('fetching twitter data...')
    twitter_header = ['date', 'title', 'topic', 'author', 'path', 'post_text']
    twitter_path = 'source_html/twitter_blog_src.html'
    twitter_content = mk_parsed_content(
        twitter_header, twitter_path, parse_twitter_result, TWITTER_RESULT_ID,
        online=False)
    write_to_csv(twitter_content, 'output/twitter_summary.csv')

    # fb
    print('fetching fb data...')
    fb_header = ['date', 'title', 'cat1', 'cat2', 'url', 'post_text']
    fb_path = 'source_html/fb_blog_src.html'
    fb_content = mk_parsed_content(
        fb_header, fb_path, parse_fb_result, FB_RESULT_ID,
        online=False)
    write_to_csv(fb_content, 'output/fb_summary.csv')

    # google
    print('fetching google data...')
    google_header = ['date', 'title', 'category', 'url', 'post_text']
    google_path = 'source_html/google_blog_src.html'
    google_content = mk_parsed_content(
        google_header, google_path, parse_google_result, GOOGLE_RESULT_ID, 
        online=False)
    write_to_csv(google_content, 'output/google_summary.csv')

# def get_more_content(driver, trigger='click'):
#     """
#     """
#     print('Fetching More Content')

#     if trigger == 'click':
#         links = []
#         link_count = 0
        
#         while True:
#             see_more_button = driver.find_element(By.LINK_TEXT, 'See more')
#             see_more_button.click()
#             page = driver.page_source
#             tsoup = BeautifulSoup(page, 'html.parser')
#             links.extend(tsoup.find_all('a', {"class": "result__title"}))
#             links = list(set(links))
#             if len(links) == link_count:
#                 break
#             link_count += len(links)
#             print('links', link_count)
#             driver.refresh()
#             time.sleep(2)
#     else:
#         last_height = driver.execute_script("return document.body.scrollHeight")
#         scroll_count = 0
#         while True:
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             print(f'Scroll Iteration: {scroll_count}')
#             time.sleep(2)  # Adjust sleep time as needed
#             new_height = driver.execute_script("return document.body.scrollHeight")
#             if new_height == last_height:
#                 break
#             last_height = new_height
    
#     return driver.page_source


# def set_driver(url):
#     chrome_options = Options()
#     chrome_options.add_argument('--headless')
#     print('Driver Started')
#     driver = webdriver.Chrome(options=chrome_options)
#     print(f'Getting URL: {url}')
#     driver.get(url)
#     return driver


# def fetch_page_with_lazy_loading(url):
#     driver = set_driver(url)
#     page_source = get_more_content(driver)
#     driver.quit()
#     return page_source