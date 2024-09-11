import json
import os
import time

import pandas as pd
import scrapy


class GoogleshoppingSpider_links(scrapy.Spider):
    name = "googleshopping_compare_links"
    base_url = 'https://www.google.com'

    # Define HTTP headers for the web requests
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US', 'Connection': 'keep-alive', 'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', }

    # Define a list of HTTP status codes to handle
    handle_httpstatus_list = [400, 401, 500, 502, 429]

    # Get the current working directory
    parent_directory = os.path.dirname(os.path.dirname(__file__))
    csv_filename = "google_shopping_no_input.csv"
    json_filename = "google_shopping_no_urls.json"
    input_filepath = os.path.join(parent_directory, csv_filename)
    output_filepath = os.path.join(parent_directory, json_filename)

    # # Initialize variables for proxy settings
    product_retry = 0

    def start_requests(self):
        # Read data from a CSV file
        df = pd.read_csv(self.input_filepath)

        # Iterate through the rows in the CSV file
        for d in df.index:
            gtin = df["gtin"][d]
            # Construct the search link based on the GTIN
            search_link = f'https://www.google.com/search?ql=no&tbm=shop&hl=nn-NO&psb=1&q={gtin}&oq={gtin}&gl=NO'

            # Send a web request to the search link
            yield scrapy.Request(search_link, headers=self.headers, callback=self.parse, meta={"gtin": gtin})

    def parse(self, response, **kwargs):
        gtin = response.meta["gtin"]

        # Extract product data from the web page
        all_product = response.xpath('//div[@class="sh-dgr__content"]')
        all_data = []

        # Retry the request if it didn't return a 200 status or no product data
        while response.status != 200 or not all_product:

            time.sleep(30)
            self.product_retry += 1

            # If retries exceed a threshold, save data and return
            if self.product_retry > 3:
                self.product_retry = 0
                data = {"Product link": '', "Gtin": str(gtin)}
                if data not in all_data:
                    all_data.append(data)
                    filename = f"google_shopping_no_urls.json"

                    if not os.path.exists(filename):
                        open(filename, "w").write(json.dumps(all_data))
                    else:
                        exist_data = open(filename, "r").read()
                        all_new_data = json.loads(exist_data) + all_data
                        open(filename, "w").write(json.dumps(all_new_data))
                    return

            # Retry the web request
            yield scrapy.Request(response.url, headers=self.headers, callback=self.parse, meta={"gtin": gtin})

        # Process product data if available
        if all_product:
            for product in all_product:
                compare_link = product.xpath('.//a[@class="iXEZD"]/@href').get()
                if compare_link:
                    compare_link = self.base_url + compare_link
                else:
                    compare_link = ""

                if compare_link:
                    data = {"Product link": compare_link, "Gtin": str(gtin)}
                    if data not in all_data:
                        all_data.append(data)

            if not os.path.exists(self.output_filepath):
                open(self.output_filepath, "w").write(json.dumps(all_data))
            else:
                exist_data = open(self.output_filepath, "r").read()
                all_new_data = json.loads(exist_data) + all_data
                open(self.output_filepath, "w").write(json.dumps(all_new_data))
