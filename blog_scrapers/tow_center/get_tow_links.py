import pandas as pd
from bs4 import BeautifulSoup
import logging
from tqdm import tqdm
import requests
from retry import retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@retry(tries=5, delay=2, logger=logger)
def extract_page_text(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
        }
    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        logger.warning(f'Failed to retrieve the page. Error: {e.__doc__}. URL: {url}')
        return f'Failed to retrieve the page. Status: {e.__doc__}'
    if response.status_code == 200:
        return response.text
    else:
        logger.info(f"Failed to retrieve the page. Status code: {response.status_code}. URL: {url}")
        return f'Failed to retrieve the page. Status: {response.status_code}'


def clean_html(text):
    return BeautifulSoup(text, 'html.parser').get_text()


def main():
    skip_links = [
        'https://fyi.bulletin.com/395013411957187',
        'https://www.businesswire.com/news/home/20210217005588/en/News-Corp-and-Google-Agree-to-Global-Partnership-on-News',
        'https://publicmediamergers.org/',
        'https://www.businesswire.com/news/home/20200401005793/en/Fox-News-Channel-Facebook-Present-Virtual-Town',
        'https://tbhtime.com/news/',
    ]

    input_file = "7_tow_platform_timeline.csv"
    output_file = "7_tow_platform_timeline_output.json"

    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        exit(f"File '{input_file}' not found.")

    if 'link' not in df.columns:
        exit("CSV file does not contain 'link' column.")
    
    df['text'] = ''
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Progress"):
        link = row['link']
        if pd.isnull(link) or link in skip_links:
            continue
        text = extract_page_text(link)
        if text:
            normalized_text = clean_html(text)
            df.at[index, 'text'] = normalized_text

    json = df.to_json(orient='records', lines=True)
    with open(output_file, 'w') as f:
        f.write(json)

    logger.info(f"Scraping completed. Data saved to '{output_file}'.")


if __name__ == '__main__':
    main()