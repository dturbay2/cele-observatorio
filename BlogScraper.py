"""
General class for base BlogScraper
"""
from bs4 import BeautifulSoup
import json
import os
import requests
from retry import retry


WAIT_TIME = 2
MAX_ATTEMPTS = 3
DETAILED_VERSION = True

class BlogScraper:

    RESULT_ID = None
    URL_ID = None
    TITLE_ID = None
    DATE_ID = None
    CAT1_ID = None
    CAT2_ID = None
    AUTHOR_ID = None
    BLOGPOST_CONTENT_ID = None
    URL = None
    LOCAL_HTML_PATH = None
    HEADER = None
    DELIMITER = '\t'
    NAME = None


    def __init__(self, online=False, output_json=False):
        self.online = online
        self.output_json = output_json


    def fetch_page_with_lazy_loading(self):
        raise NotImplementedError


    def get_content(self, soup, tag_type, search_val, search_key='class', 
                    find_all=False, get_text=False):
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


    def read_page_source_from_file(self, path: str):
        """read html file to be parsed by for 'manual scraping'"""
        with open(path, "r", encoding='utf-8') as f:
            page_source = f.read()
        return page_source


    def write_to_csv(self, content, output_file):
        with open(output_file, "w", encoding='utf-8') as f:
            f.write(content)


    @retry(tries=MAX_ATTEMPTS, delay=WAIT_TIME)
    def get_blog_context(self, url, obj_id, obj_type='div'):
        soup = BeautifulSoup(requests.get(url).text, 'html.parser')
        content = self.get_content(soup, obj_type, obj_id, get_text=True)
        return '\n'.join([blob for blob in content.split('\n') if blob])


    def parse_result(self, result):
        pass


    def parse_page_to_records(self, page_source, parser, result_id, 
                              result_type='div'):
        """Parse page-source into list of records"""
        soup = BeautifulSoup(page_source, 'html.parser')
        results = self.get_content(soup, result_type, result_id, find_all=True)
        records = []
        for result in results:
            values = parser(result)
            records.append(values)
        return records


    def mk_parsed_content(self, header, path, parser, result_id, 
                          output_json=False, result_type='div', online=False):
        if online:
            page_source = self.fetch_page_with_lazy_loading(path)
        else:
            page_source = self.read_page_source_from_file(path)
        data = self.parse_page_to_records(page_source, parser, result_id,
                                          result_type)

        if DETAILED_VERSION or output_json:
            records = [json.dumps(dict(zip(header, record))) for record in data]
        else:
            data = [header] + data
            records = [self.DELIMITER.join(record) for record in data]

        return '\n'.join(records)


    def scrape_data(self, output_json=False):
        path = self.LOCAL_HTML_PATH if not self.online else self. URL
        print(f'fetching data from {path}...')
        content = self.mk_parsed_content(
            self.HEADER, path, self.parse_result, self.RESULT_ID,
            online=self.online, output_json=output_json
            )

        if not os.path.exists('output'):
            os.makedirs('output')

        version_type = "summary" if not DETAILED_VERSION else "detailed"
        file_name = f'output/{self.NAME}_{version_type}.csv'
        print(f'writing to {file_name}')
        self.write_to_csv(content, file_name)
