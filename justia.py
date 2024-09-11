import os
import requests
from lxml import html
import pandas as pd


class JustiaScraper:
    def __init__(self):
        self.base_url = 'https://law.justia.com'
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Referer': f'{self.base_url}/codes/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        self.filename = "Justia.csv"
        self.scrape_states()

    def fetch_html(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return html.fromstring(response.text)
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_state_links(self, doc):
        state_links = doc.xpath('//*[contains(text(),"State Codes and Statutes")]//following-sibling::div/ul//li/a')
        return [state.xpath('.//text()')[0].strip().lower() for state in state_links]

    def scrape_states(self):
        url = f'{self.base_url}/codes/'
        doc = self.fetch_html(url)
        if doc is not None:
            state_names = self.parse_state_links(doc)
            for state_name in state_names:
                self.scrape_titles(state_name)

    def scrape_titles(self, state_name):
        url = f'{self.base_url}/codes/{state_name}/2021/title-1/chapter-1/section-1-1-1/'
        doc = self.fetch_html(url)
        if doc is not None:
            item = self.extract_info(doc)
            self.save_to_csv(item)

    def extract_info(self, doc):
        item = {
            "Title": "".join(doc.xpath('//h1[@class="heading-1"]/text()')),
            "Universal Citation": "".join(
                doc.xpath('//strong[contains(text(), "Universal Citation")]/following-sibling::a[1]/text()')).strip(),
            "Text": "".join(doc.xpath('//div[@id="codes-content"]//text()')),
            "Desclimer": "".join(doc.xpath('//div[@class="disclaimer"]//text()')).replace("Disclaimer:", "").strip(),
        }
        return item

    def save_to_csv(self, item):
        df = pd.DataFrame([item])
        if os.path.exists(self.filename):
            df.to_csv(self.filename, mode='a', index=False, header=False)
        else:
            df.to_csv(self.filename, mode='w', index=False, header=True)


if __name__ == '__main__':
    """ to run this scraper please install all dependencies:
        lxml == 5.1.1
        pandas == 2.2.2
        Requests == 2.32.3
    """
    JustiaScraper()
