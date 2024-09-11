import os
import time
import json
import aiohttp
import asyncio
import pandas as pd
from lxml import html
import logging
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Scraper:
    def __init__(self, token: str, output_dir: str, max_retries: int = 3):
        self.token = token
        self.output_dir = output_dir
        self.max_retries = max_retries
        self.session = aiohttp.ClientSession()

    async def fetch(self, url: str) -> str:
        for attempt in range(self.max_retries):
            try:
                async with self.session.get(f'http://api.scrape.do?token={self.token}&url={url}',
                                            timeout=30) as response:
                    if response.status == 200:
                        return await response.text()
            except Exception as e:
                logging.error(f'Error fetching {url}: {e}')
                await asyncio.sleep(5)
        return ''

    async def product_details(self, url: str, name: str, category: str) -> None:
        response_text = await self.fetch(url)
        if not response_text:
            with open('Skipped_Links.txt', 'a') as f:
                f.write(f'{url}\n')
            return

        doc = html.fromstring(response_text)
        item = {
            'URL': url,
            'Category': category,
            'Name': name,
            'Description': ''.join(doc.xpath('//*[@itemprop="description"]//p//text()')).strip(),
            'Strain-Feelings': ', '.join(
                doc.xpath('//h3[contains(text(),"Feelings")]/following-sibling::div//a//p//text()')),
            'Strain-Negatives': ', '.join(
                doc.xpath('//h3[contains(text(),"Negatives")]/following-sibling::div//a//p//text()')),
            'Strain-Flavors': ', '.join(
                doc.xpath('//div[@class="col-1/3"]//a[contains(@href,"lists/flavor")]//p//text()')),
            'Rating': doc.xpath(
                '//*[@href="#strain-reviews-section"]//span[contains(@class,"star-rating")]/preceding-sibling::span[1]//text()')[
                0].strip()
        }

        filename = 'leafy_data.csv'
        df = pd.DataFrame([item])
        df['Name'] = df['Name'].apply(lambda x: f'="{x}"')
        if os.path.exists(filename):
            df.to_csv(filename, mode='a', index=False, header=False)
        else:
            df.to_csv(filename, mode='a', index=False, header=True)
        logging.info(f'Processed: {item}')

    async def fetch_strains(self, offset: int) -> List[Dict]:
        headers = {
            'authority': 'consumer-api.leafly.com',
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'origin': 'https://www.leafly.com',
            'referer': 'https://www.leafly.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }

        async with self.session.get(
                f'https://consumer-api.leafly.com/api/strain_playlists/v2?enableNewFilters=true&skip={offset}&strain_playlist=&take=18&lat=23.0276&lon=72.5871&sort[0][strain_name]=asc',
                headers=headers
        ) as response:
            if response.status == 200:
                return await response.json().get('hits', {}).get('strain', [])
            return []

    async def scrape(self):
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

        offset = 0
        while True:
            strains = await self.fetch_strains(offset)
            if not strains:
                break

            for strain in strains:
                await asyncio.sleep(3)  # Be polite and avoid rate-limiting
                slug = strain['slug']
                name = strain['name']
                category = strain['category']
                product_url = f'https://www.leafly.com/strains/{slug}'
                await self.product_details(product_url.lower(), name, category)

            offset += 18

    async def close(self):
        await self.session.close()


async def main():
    scraper = Scraper(token='', output_dir='JSON_Files')
    await scraper.scrape()
    await scraper.close()


if __name__ == '__main__':
    asyncio.run(main())
