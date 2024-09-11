# -*- coding: utf-8 -*-
import scrapy
import re
import pandas as pd
import datetime
import os
import pymysql
import sainsburys.db_config as db
from sainsburys.items import SainsburysItem
import base64
from lxml import html
from scrapy.cmdline import execute


class SainsbuysDetailsSpider(scrapy.Spider):
    name = 'sainsbuys_details'
    allowed_domains = ['www.sainsburys.co.uk']
    start_urls = ['http://www.sainsburys.co.uk/']

    def __init__(self, name=None, start=0, end=0, **kwargs):
        super().__init__(name, **kwargs)

        # DATABASE SPECIFIC VALUES
        self.start = int(start)
        self.end = int(end)
        self.con = pymysql.connect(host=db.db_host, user=db.db_user, password=db.db_password, db=db.db_name)
        self.cursor = self.con.cursor()
        # self.PAGE_SAVE_PATH = f"C:/ASDA"
        self.PAGE_SAVE_PATH = f"/home/vrusahbh/PycharmProjects/pythonProject/scrapyprojects/sainsburys"
        self.data_insert = 0
        self.headers = {
            'authority': 'www.sainsburys.co.uk',
            'accept': 'application/json',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'content-type': 'application/json',
            'enabled-feature-flags': 'ads_conditionals,findability_v5,show_static_cnc_messaging,event_dates,fetch_future_slot_weeks,click_and_collect_promo_banner,cookie_law_link,citrus_banners,citrus_search_trio_banners,citrus_favourites_trio_banners,offers_trio_banners_single_call,special_logo,bhm_logo,custom_product_messaging,promotional_link,findability_search,findability_autosuggest,findability_orchestrator,fto_header_flag,recurring_slot_skip_opt_out,first_favourite_oauth_entry_point,seasonal_favourites,cnc_start_amend_order_modal,desktop_interstitial_variant,mobile_interstitial_variant,checkout_summary,favourites_product_cta_alt,get_favourites_from_v2,updated_home_delivery_banner,saver_slot_update,offers_config,alternatives_modal,relevancy_rank,disappearing_header_ab_test,pdp_promo_expiry_banners,constant_commerce_v2,favourites_pill_nav,nectar_destination_page,nectar_card_associated,meal_deal_noindex,bv_review_new,bv_review_new_api,catchweight_dropdown,citrus_xsell,exclude_nectar_cola_offer,favourites_whole_service,first_favourites_static,foodmaestro_modal,hfss_restricted,interstitial_variant,kg_price_label,nectar_prices,new_favourites_service,ni_brexit_banner,offer_promotion,offers_100_percent,print_recipes,review_syndication,sale_january,sponsored_featured_tiles,xmas_dummy_skus',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'wcauthtoken': '-1002%2C3jIiHU%2F3lFc4jalpGDAhYOztAdQ%3D',
        }
        # self.db_brands_list = self.db_brands_list()
        # self.cursor.execute(f"USE {db.db_name};")

    def manufacture_check(self, brand):

        query = f"SELECT Manufacturers FROM sainburys.manufacturers where Brand=`{brand}`;"

        try:
            self.cursor.execute(query)
            manufacturer = self.cursor.fetchone()
        except:
            manufacturer = None
        manufacturer = manufacturer[0] if manufacturer else None

        return manufacturer

    def start_requests(self):
        query = f"select * FROM {db.db_name}.{db.db_links_table} where status='Pending';"
        # query = f"select * FROM {db.db_name}.{db.db_links_table};"
        # query = f"select * FROM {db.db_name}.{db.db_links_table} where Product_URL='https://www.sainsburys.co.uk/gol-ui/product/whitley-neill-rhubarb-ginger-alcohol-free-spirit-70cl';"
        # and id between {self.start} and {self.end}"
        self.cursor.execute(query)
        query_results = self.cursor.fetchall()
        self.logger.info(f"\n\n\nTotal Results ...{len(query_results)}\n\n\n", )
        for query_result in query_results:
            meta = {
                "Id": query_result[0],
                "pro_url": query_result[1]
            }
            sku = query_result[1].split("product/")[-1]
            yield scrapy.Request(
                url=f'https://www.sainsburys.co.uk/groceries-api/gol-services/product/v1/product?filter[product_seo_url]=gb%2Fgroceries%2F{sku}&include[ASSOCIATIONS]=true&include[PRODUCT_AD]=citrus',
                headers=self.headers,
                # dont_filter=True,
                callback=self.parse,
                meta=meta,
            )

    def parse(self, response):

        all_data = response.json()["products"]
        platform = 'sainsburys'
        for p in all_data:
            item = SainsburysItem()
            try:
                product_id = p["product_uid"]
            except:
                product_id = None

            filepath = self.PAGE_SAVE_PATH + f'/product_pages/{product_id}.txt'
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
                f.close()

            try:
                sku_name = p["name"]
            except:
                sku_name = None

            if "blended irish whiskey" in sku_name.lower() or "blended irish whiskey Flav." in sku_name.lower() or "malt irish whiskey" in sku_name.lower():
                sector = "Irish Whiskey"
            elif "blended scotch" in sku_name.lower() or "grain scotch" in sku_name.lower() or "malt scotch" in sku_name.lower():
                sector = "Scotch Whisky"
            elif "blended" in sku_name.lower() or "bourbon" in sku_name.lower() or "american whiskey" in sku_name.lower() or "other us whiskey" in sku_name.lower() or "rye" in sku_name.lower() or "tennessee" in sku_name.lower():
                sector = "US Whiskey"
            else:
                sector = "NA"

            if "distille" in sku_name.lower():
                try:
                    Distillery = sku_name.lower().split("distille")[0]
                except:
                    Distillery = ""
            else:
                Distillery = ""

            try:
                age_whisky = re.findall(f"(\d+) years old", sku_name.lower())
            except:
                age_whisky = ""

            if not age_whisky:
                try:
                    age_whisky = re.findall(f"(\d+) year old", sku_name.lower())
                except:
                    age_whisky = ""

            if not age_whisky:
                age_whisky = 'NA'

            try:
                size = ''.join(re.findall('(\d+ litre)', sku_name.lower()))
            except:
                size = None

            if not size:
                try:
                    size = ''.join(re.findall('(\d+ml)', sku_name.lower()))
                except:
                    size = None

            if not size:
                try:
                    size = ''.join(re.findall('(\d+cl)', sku_name.lower()))
                except:
                    size = None
            if not size:
                try:
                    size = ''.join(re.findall('(\d+ cl)', sku_name.lower()))
                except:
                    size = None
            if not size:
                try:
                    size = ''.join(re.findall('(\d+l)', sku_name.lower()))
                except:
                    size = None

            if "cl" in size:
                size_pack = int(size.lower().replace("cl", "").strip()) * 10
            elif "ml" in size.lower():
                size_pack = size.lower().replace("ml", "").strip()
            elif "litre" in size.lower():
                size_pack = int(size.lower().replace("litre", "").strip()) * 1000
            elif "l" in size:
                size_pack = int(size.lower().replace("l", "").strip()) * 1000
            else:
                size_pack = "NA"
            try:
                breadcrumbs = p["breadcrumbs"]
            except:
                breadcrumbs = None
            all_category = []
            for b in breadcrumbs:
                all_category.append(b["label"])

            if len(all_category) == 4:
                category_1 = all_category[0]
                category_2 = all_category[1]
                category_3 = all_category[2]
                category_4 = all_category[3]
            elif len(all_category) == 3:
                category_1 = all_category[0]
                category_2 = all_category[1]
                category_3 = all_category[2]
                category_4 = 'NA'
            elif len(all_category) == 2:
                category_1 = all_category[0]
                category_2 = all_category[1]
                category_3 = 'NA'
                category_4 = 'NA'
            elif len(all_category) == 1:
                category_1 = all_category[0]
                category_2 = 'NA'
                category_3 = 'NA'
                category_4 = 'NA'
            else:
                category_1 = 'NA'
                category_2 = 'NA'
                category_3 = 'NA'
                category_4 = 'NA'

            try:
                brand = ''.join(p["attributes"]["brand"])
            except:
                brand = None

            try:
                detail_text = base64.b64decode(p["details_html"]).decode('UTF-8')
            except:
                detail_text = None

            if detail_text:
                detail_text_response = html.fromstring(detail_text)
                try:
                    manufacture = ""
                    manu = detail_text_response.xpath(
                        '//h3[contains(text(), "Manufacturer")]/following-sibling::div[@class="itemTypeGroup"]//p//text()')
                    if not manu:
                        manu = detail_text_response.xpath(
                            '//h3[contains(text(), "Manufacturer")][@class="productDataItemHeader"]/following-sibling::div/p/text()')
                    if manu:
                        for m in manu:
                            if " ltd" in m.lower():
                                manufacture = m
                            if not Distillery and "distille" in m.lower():
                                if "by:" in m.lower() or "at:" in m.lower() or "for:" in m.lower() or "Distilled and bottled for:" == m.lower():
                                    continue
                                try:
                                    Distillery = m.lower().split('distille')[0].replace(",", "")
                                except:
                                    Distillery = ""
                                # elif "Distilled and bottled for:" != m.lower():
                                #     try:
                                #         Distillery = m.split('distille')[0]
                                #     except:
                                #         Distillery = ""
                        if not manufacture:
                            if "by:" in manu[0] or "at:" in manu[0] or "for:" in manu[0]:
                                manufacture = manu[1].strip()
                            else:
                                manufacture = manu[0].strip()

                        if not Distillery:
                            if "distille" in manu[0]:
                                if "by:" in manu[0] or "at:" in manu[0] or "for:" in manu[0]:
                                    Distillery = manu[1].strip()

                except:
                    manufacture = ""

                if not manufacture:
                    manufacture = self.manufacture_check(brand)

                if not manufacture:
                    manufacture = "NA"

                try:
                    country_of_origin = detail_text_response.xpath(
                        '//h3[contains(text(), "Country of Origin")]/following-sibling::div[@class="itemTypeGroup"]//p//text()')[
                        0].replace("Country of origin:", "").strip()
                    if ":" in country_of_origin:
                        country_of_origin = country_of_origin.split(":")[1].strip()
                except:
                    country_of_origin = ""

                if not country_of_origin:
                    try:
                        country_of_origin = ''.join(detail_text_response.xpath(
                            '//h3[contains(text(), "Country of Origin")]/following-sibling::div[@class="productText"][1]/p/text()'))
                    except:
                        country_of_origin = ""

                if not country_of_origin:
                    country_of_origin = "NA"

                try:
                    pack_type_ = detail_text_response.xpath('//h3[contains(text(), "Packaging")]/following-sibling::div[@class="itemTypeGroup"]//p//text()')
                except:
                    pack_type_ = ""
                if not pack_type_:
                    try:
                        pack_type_ = detail_text_response.xpath(
                            '//h3[contains(text(), "Packaging")]/following-sibling::div[@class="productText"][1]/p/text()')
                    except:
                        pack_type_ = None
                pack_type = ""
                for pa in pack_type_:
                    if "bottle" in pa.lower():
                        pack_type = pa

                if not pack_type:
                    pack_type = 'NA'

                try:
                    ABV = ''.join(re.findall("Alcohol by volume: (\d+.\d+)%", detail_text))
                except:
                    ABV = None

                if not ABV:
                    try:
                        ABV = ''.join(re.findall("Alcohol by volume: (\d+)%", detail_text))
                    except:
                        ABV = None

                if not ABV:
                    try:
                        ABV = ''.join(detail_text_response.xpath(
                            "//span[contains(text(), 'Alcohol by volume:')]/following-sibling::span/text()")).replace(
                            "%", "").strip()
                    except:
                        ABV = ""
                if not ABV:
                    ABV = "NA"
            else:
                manufacture = "NA"
                ABV = "NA"
                pack_type = "NA"
                country_of_origin = "NA"

            if "distille" in Distillery.lower():
                try:
                    Distillery = Distillery.lower().split("distille")[0]
                except:
                    Distillery = Distillery

            if not Distillery:
                Distillery = "NA"

            try:
                Price_per_unit = p["unit_price"]["price"]
            except:
                Price_per_unit = "NA"

            try:
                retail_price = p["promotions"][0]["original_price"]
            except:
                retail_price = ""

            if not retail_price:
                try:
                    retail_price = p["retail_price"]["price"]
                except:
                    retail_price = 'NA'

            try:
                promo_Price = p["nectar_price"]["retail_price"]
            except:
                promo_Price = ""

            if not promo_Price:
                try:
                    promo_Price = p["nectar_price"]["unit_price"]
                except:
                    promo_Price = ""

            if not promo_Price:
                promo_Price = "NA"

            try:
                image = p["assets"]["plp_image"]
            except:
                image = 'NA'

            scraped_date = datetime.datetime.strftime(datetime.date.today(), "%d_%m_%Y")

            item['Id'] = response.meta["Id"]
            item['htmlpath'] = filepath
            item['Platform_Name'] = platform
            item['Platform_URL'] = response.meta["pro_url"]
            item['Product_id'] = product_id
            item['Category_1'] = category_1
            item['Category_2'] = category_2
            item['Category_3'] = category_3
            item['Category_4'] = category_4
            item['Sector'] = sector
            item['SKU_Name'] = sku_name
            item['Manufacturer'] = manufacture.replace(",", "")
            item['Brand'] = brand
            item['Pack_Size'] = size_pack
            item['Price'] = retail_price
            item['Promo_Price'] = promo_Price
            item['Price_per_unit'] = Price_per_unit
            item['Age_of_Whisky'] = age_whisky
            item['Country_of_Origin'] = country_of_origin
            item['Distillery'] = Distillery.replace(",", "") if Distillery else "NA"
            item['Pack_type'] = pack_type
            item['Tasting_Notes'] = "NA"
            item['Image_Urls'] = image
            item['ABV'] = ABV
            item['scrape_date'] = scraped_date

            # print(item)


            # df = pd.DataFrame([item])
            # filename = f"sainburys.csv"
            # if os.path.exists(filename):
            #     df.to_csv(filename, mode='a', index=False, header=False)
            # else:
            #     df.to_csv(filename, mode='a', index=False, header=True)
            yield item


if __name__ == '__main__':
    execute('scrapy crawl sainsbuys_details'.split())
