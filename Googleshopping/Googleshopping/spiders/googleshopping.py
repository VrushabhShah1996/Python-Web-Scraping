import json
import os.path
import time

import scrapy


class GoogleshoppingSpider_data(scrapy.Spider):
    name = "googleshopping_data"
    base_url = 'https://www.google.com'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US', 'Connection': 'keep-alive', 'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', }

    handle_httpstatus_list = [400, 401, 429, 500, 502]

    RETRY_ENABLED = True
    RETRY_TIMES = 3

    # Get the current working directory
    parent_directory = os.path.dirname(os.path.dirname(__file__))
    urls_json_filename = "google_shopping_no_urls.json"
    data_json_filename = "google_shopping_no_output.json"
    input_filepath = os.path.join(parent_directory, urls_json_filename)
    output_filepath = os.path.join(parent_directory, data_json_filename)

    def start_requests(self):
        try:
            all_links = json.loads(open(self.input_filepath, "r").read())
        except:
            all_links = None
        if all_links:
            for links in all_links:
                product_link = links["Product link"]
                gtin = links["Gtin"]
                if product_link:
                    yield scrapy.Request(product_link, headers=self.headers, callback=self.parse, meta={"Gtin": gtin})
        else:
            print('The urls json is not found')

    def parse(self, response, **kwargs):
        title = response.xpath('//div[@class="f0t7kf"]/a/text()').get()
        gtin = response.meta["Gtin"]
        while response.status != 200 or not title:
            time.sleep(30)
            yield scrapy.Request(response.url, headers=self.headers, callback=self.parse, meta={"Gtin": gtin})
        all_competitor = response.xpath('//table[@class="dOwBOc"]/tbody/tr[@data-hveid]')
        if all_competitor:
            for com in all_competitor:

                competitor_name = ''.join(com.xpath('./td[1]/div[@class="kPMwsc"]/a/text()').getall()).replace('\xa0',
                                                                                                               '').replace(
                    '\n', '').replace('\t', '').strip()

                competitor_link = ''.join(com.xpath('./td[1]/div[@class="kPMwsc"]/a/@href').getall()).replace('\xa0',
                                                                                                              '').replace(
                    '\n', '').replace('\t', '').strip()
                if 'url?q=' in competitor_link:
                    competitor_link = competitor_link.split('url?q=')[1]

                competitor_price = ''.join(com.xpath('./td[4]//text()').getall()).replace(',', '.').replace('\xa0',
                                                                                                            '').replace(
                    '\n', '').replace('\t', '').strip()

                competitor_price_total = ''.join(com.xpath('./td[5]//div[@class="drzWO"]/text()').getall()).replace(',',
                                                                                                                    '.').replace(
                    '\xa0', '').replace('\n', '').replace('\t', '').strip()
                all_data = []
                data = {'title': title, 'competitor_name': competitor_name, 'competitor_price': competitor_price,
                        'competitor_price_total': competitor_price_total, 'availability': 'IS', 'gtin': f'{gtin}',
                        'competitor_url': competitor_link}

                print(data)
                all_data.append(data)
                if not os.path.exists(self.output_filepath):
                    open(self.output_filepath, "w").write(json.dumps(all_data))
                else:
                    exist_data = open(self.output_filepath, "r").read()
                    all_new_data = json.loads(exist_data) + all_data
                    open(self.output_filepath, "w").write(json.dumps(all_new_data))
