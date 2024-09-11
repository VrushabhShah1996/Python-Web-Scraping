# -*- coding: utf-8 -*-
import scrapy
import waitrose.db_config as db
import pymysql
import re
import json
import os
import datetime
from waitrose.items import WaitroseItem
from scrapy.cmdline import execute

class WaitroseDataSpider(scrapy.Spider):
    name = 'waitrose_data'
    allowed_domains = ['www.waitrose.com']
    start_urls = ['http://www.waitrose.com/']

    def __init__(self, name=None, start=0, end=0, **kwargs):
        super().__init__(name, **kwargs)

        # DATABASE SPECIFIC VALUES
        self.start = int(start)
        self.end = int(end)
        self.con = pymysql.connect(host=db.db_host, user=db.db_user, password=db.db_password, db=db.db_name)
        self.cursor = self.con.cursor()
        # self.PAGE_SAVE_PATH = f"C:/ASDA"
        self.PAGE_SAVE_PATH = f"/home/vrusahbh/PycharmProjects/pythonProject/scrapyprojects/waitrose/product_pages"
        self.data_insert = 0
        self.headers = {
            'authority': 'www.waitrose.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'cache-control': 'max-age=0',
            # 'cookie': 'gtm_session=1; mt.v=2.193581503.1686935016989; wtr_cookie_consent=1; wtr_cookies_advertising=1; wtr_cookies_analytics=1; wtr_cookies_functional=1; IR_gbd=waitrose.com; _gcl_au=1.1.986493802.1686935020; _gid=GA1.2.957314991.1686935020; _cs_c=1; unbxd.userId=uid-1686935020423-8490; _fbp=fb.1.1686935020814.794166170; _pin_unauth=dWlkPU1UWTBOVEExTWpjdFl6Z3daaTAwTkRVM0xUZ3haRFF0T0RVM05qZG1Oell5Wmpjdw; eds=INS-vi42-303388996:265076283-1686935020^709016667-1686935020; BVImplecom=17263_2_0; BVBRANDID=8bd7c772-ce2b-490b-844d-281bbc0d2401; _hjSessionUser_1434770=eyJpZCI6IjBlNWRlODQzLWUzMDctNWM5Ni1hZjg2LTVmZmQ2NmVlNGMxOSIsImNyZWF0ZWQiOjE2ODY5MzUwMjA2MDEsImV4aXN0aW5nIjp0cnVlfQ==; _hjHasCachedUserAttributes=true; _abck=25D4399309397C4EF466DFF5BE409BB7~0~YAAQPHxBF5f1oKSIAQAAkffTyAr2OT5vt1a1Dx9+NXVJR/A71fm7/WybXgnR3tpAFlLu/krfc8tZM1yiuKYHbgU9sYXcd8CyOLkVHhoMFXd6Zq7+JJOfmGvDYrxswlNflg5RqAYP2wupLa9jCvJ9D96i7bBk3kTf3RLWM92E8IC/XJvM/G5DqIOW9yuZmC8R++xyyUJF3Ll1J/JAmD8/yCRMISNALLw2USowxHlC4KmtrqBMb/hQLDkP3f3UXxyBDisPaffG4xdzJUJFtbapp3HspDsiCVtFc69OddTPJecFPqLb5k8BFJprJnE4q6sN8B48cCdsOJRCmW6nf3OCcbbOzZgHBf9me5DbidCt38QaW1JL5J7vsZ0p8JVuA0+SFYSUQ0usggMCgmCO4Gq5MEQSyQ9rKURYlA==~-1~-1~-1; bm_sz=197E47AE04E14725EA59D80662F964CE~YAAQPHxBF5j1oKSIAQAAkffTyBS/XXxHATsoBrz3jShkFoZLcnwbATADHIbY2vcV9C31YLENFh9AwYQrbj/a20x17NljqkVO0g92ogWUEpDtiGmMOv9oDzIMIajCc4TFRSK2ucdGPAdiM5wsA25fzyk2yxJ2tJd++yRc9T9FxFL2klJzG/MPT7R+OGexAg7rZsVXi4vfUXifOlzt7pGoP4ROqpxunVcfQ4L81udglt3V9Pyab7RkQsOzNibb1yrUT5nCN8sef41lJYQYraJa30RLQ+56DZWDxYenh8q+01nCmhzcQQ==~3294772~3356466; mt.sc=%7B%22i%22%3A1686997686938%2C%22d%22%3A%5B%22cs%3Bdirect%22%5D%7D; website_csat_session=2023-06-17:7974296367; unbxd.visitId=visitId-1686997687780-64914; _cs_mk_ga=376840719_1686997688039; _hjSession_1434770=eyJpZCI6ImZhMWJlNDNhLWMxYzMtNDBkNC04OWEyLTQzOWUyOGJjNTJlZiIsImNyZWF0ZWQiOjE2ODY5OTc2ODgyMDQsImluU2FtcGxlIjpmYWxzZX0=; _hjAbsoluteSessionInProgress=0; _hjIncludedInSessionSample_1434770=0; PIM-SESSION-ID=X9KfOwrPtAdPpOtm; unbxd.visit=repeat; BVBRANDSID=c99e2266-448c-431b-959b-2708b9821bde; bm_sv=5CB2F9E14D58B14E83CB00F55D3D7D42~YAAQPHxBF/Zdq6SIAQAAohVRyRQjl2X3nYFM8Dcoz7QpZ3+sYB3ImexrZC5h/5etojZWsjKaXB5o2xOo2Q2tdI4Nqg6HdyOiQ1d/EGhnpzvDH/3T/U1cxxd0mDDlcKKhDxZ8ZyAtPmgEpccerOG/mTTnufaru80kg4nKGsBjSxOsSPs9H7KwLzHt8scwPUvZeaPnuVtrfsMEs9Njj48f8U6fFrlr7hRGgvtVwOS40jxmbF2W99Fy6bDBNssEe1yIuKBZgw==~1; IR_12163=1687004715143%7C0%7C1687004715143%7C%7C; _cs_id=1e335946-b3c1-a2df-c3ad-d38152ad83fa.1686935020.13.1687004715.1686999373.1.1721099020396; _cs_s=66.0.0.1687006515575; _ga_DZJD4TQPGV=GS1.1.1686997687.4.1.1687004715.0.0.0; _ga=GA1.2.2.193581503.1686935016989; _ga_5NQ8P4PPP7=GS1.1.1686997688.5.1.1687004716.0.0.0; _ga_8YN3DG5SKT=GS1.1.1686997687.5.1.1687004810.60.0.0; ecos.dt=1687004906724',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
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
        query = f"select * FROM {db.db_name}.{db.db_links_table} where status='Pending' limit 10;"
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

            yield scrapy.Request(url=query_result[1], headers=self.headers, meta=meta, callback=self.parse)

    def parse(self, response):
        try:
            breadcrumbs_list = \
                json.loads(response.xpath('//script[@data-testid="seo-meta-breadcrumbs"]/text()').get())[
                    "itemListElement"]
        except:
            breadcrumbs_list = None

        breadcrumbs = []
        for b in breadcrumbs_list:
            breadcrumbs.append(b["name"])

        if len(breadcrumbs_list) == 8:
            category_1 = breadcrumbs[0]
            category_2 = breadcrumbs[1]
            category_3 = breadcrumbs[2]
            category_4 = breadcrumbs[3]
            category_5 = breadcrumbs[4]
            category_6 = breadcrumbs[5]
            category_7 = breadcrumbs[6]
            category_8 = breadcrumbs[7]
        elif len(breadcrumbs_list) == 7:
            category_1 = breadcrumbs[0]
            category_2 = breadcrumbs[1]
            category_3 = breadcrumbs[2]
            category_4 = breadcrumbs[3]
            category_5 = breadcrumbs[4]
            category_6 = breadcrumbs[5]
            category_7 = breadcrumbs[6]
            category_8 = "NA"
        elif len(breadcrumbs_list) == 6:
            category_1 = breadcrumbs[0]
            category_2 = breadcrumbs[1]
            category_3 = breadcrumbs[2]
            category_4 = breadcrumbs[3]
            category_5 = breadcrumbs[4]
            category_6 = breadcrumbs[5]
            category_7 = "NA"
            category_8 = "NA"
        elif len(breadcrumbs_list) == 5:
            category_1 = breadcrumbs[0]
            category_2 = breadcrumbs[1]
            category_3 = breadcrumbs[2]
            category_4 = breadcrumbs[3]
            category_5 = breadcrumbs[4]
            category_6 = "NA"
            category_7 = "NA"
            category_8 = "NA"
        elif len(breadcrumbs_list) == 4:
            category_1 = breadcrumbs[0]
            category_2 = breadcrumbs[1]
            category_3 = breadcrumbs[2]
            category_4 = breadcrumbs[3]
            category_5 = "NA"
            category_6 = "NA"
            category_7 = "NA"
            category_8 = "NA"
        elif len(breadcrumbs_list) == 3:
            category_1 = breadcrumbs[0]
            category_2 = breadcrumbs[1]
            category_3 = breadcrumbs[2]
            category_4 = "NA"
            category_5 = "NA"
            category_6 = "NA"
            category_7 = "NA"
            category_8 = "NA"
        elif len(breadcrumbs_list) == 2:
            category_1 = breadcrumbs[0]
            category_2 = breadcrumbs[1]
            category_3 = "NA"
            category_4 = "NA"
            category_5 = "NA"
            category_6 = "NA"
            category_7 = "NA"
            category_8 = "NA"
        elif len(breadcrumbs_list) == 1:
            category_1 = breadcrumbs[0]
            category_2 = "NA"
            category_3 = "NA"
            category_4 = "NA"
            category_5 = "NA"
            category_6 = "NA"
            category_7 = "NA"
            category_8 = "NA"
        else:
            category_1 = "NA"
            category_2 = "NA"
            category_3 = "NA"
            category_4 = "NA"
            category_5 = "NA"
            category_6 = "NA"
            category_7 = "NA"
            category_8 = "NA"

        all_basic_item = json.loads(response.xpath('//script[@data-testid="seo-structured-data"]/text()').get())
        product_id = all_basic_item["mpn"]
        if not os.path.exists(self.PAGE_SAVE_PATH):
            os.makedirs(self.PAGE_SAVE_PATH)
        filepath = self.PAGE_SAVE_PATH + f'/{product_id}.txt'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)
            f.close()

        try:
            brand = all_basic_item["brand"]["name"]
        except:
            brand = ""

        all_data = json.loads(
            response.xpath('//script[contains(text(), "window.__PRELOADED_STATE__ = ")]/text()').get().replace(
                "window.__PRELOADED_STATE__ = ", ""))
        # print(all_data)
        product = all_data["entities"]["products"][product_id]
        # print(json.dumps(product))
        try:
            name = product["name"]
        except:
            name = ""

        if "aperitif" in name.lower() or "wine" in name.lower():
            return None

        if "blended irish whiskey" in name.lower() or "blended irish whiskey Flav." in name.lower() or "malt irish whiskey" in name.lower() or "irish whiskey" in name.lower():
            sector = "Irish Whiskey"
        elif "blended scotch" in name.lower() or "grain scotch" in name.lower() or "malt scotch" in name.lower() or "scotch whisky" in name.lower():
            sector = "Scotch Whisky"
        elif "blended" in name.lower() or "bourbon" in name.lower() or "other us whiskey" in name.lower() or "rye" in name.lower() or "tennessee" in name.lower() or "american whiskey" in name.lower():
            sector = "US Whiskey"
        else:
            sector = ""

        if not sector:
            for ba in breadcrumbs_list:
                if "blended irish whiskey" in ba["name"].lower() or "blended irish whiskey Flav." in ba[
                    "name"].lower() or "malt irish whiskey" in ba["name"].lower() or "irish whiskey" in ba[
                    "name"].lower():
                    sector = "Irish Whiskey"
                    break
                elif "blended scotch" in ba["name"].lower() or "grain scotch" in ba["name"].lower() or "malt scotch" in \
                        ba[
                            "name"].lower() or "scotch whisky" in ba["name"].lower():
                    sector = "Scotch Whisky"
                    break
                elif "blended" in ba["name"].lower() or "bourbon" in ba["name"].lower() or "other us whiskey" in ba[
                    "name"].lower() or "rye" in ba["name"].lower() or "tennessee" in ba[
                    "name"].lower() or "american whiskey" in ba["name"].lower():
                    sector = "US Whiskey"
                    break
                else:
                    sector = ""

        try:
            size = product["size"]
        except:
            size = ""

        if "cl" in size.lower():
            size_pack = float(size.lower().replace("cl", "").strip()) * 10
        elif "litre" in size.lower():
            size_pack = float(size.lower().replace("litre", "").strip()) * 1000
        elif "ml" in size.lower():
            size_pack = float(size.lower().replace("ml", "").strip())
        elif "l" in size.lower():
            size_pack = float(size.lower().replace("l", "").strip()) * 1000
        else:
            size_pack = "NA"

        try:
            try:
                unit = product["promotion"]["promotionalPricePerUnit"]
            except:
                unit = ""

            if not unit:
                try:
                    unit = product["displayPriceQualifier"]
                except:
                    unit = ""
            try:
                unit_price = ''.join(re.findall('(\d+.\d+)', unit))
            except:
                unit_price = ""

            if not unit_price:
                try:
                    unit_price = ''.join(re.findall('(\d+)', unit))
                except:
                    unit_price = ""

        except:
            unit_price = ""

        try:
            promo_price = product["promotion"]["promotionUnitPrice"]["amount"]
        except:
            promo_price = ""

        try:
            retail_price = product["currentSaleUnitPrice"]["price"]["amount"]
        except:
            retail_price = ""

        country_of_origin = ""
        try:
            country = product["contents"]["origins"]
            for c in country:
                try:
                    if c["name"].lower() == "country of origin":
                        country_of_origin = c["value"]
                except:
                    pass
        except:
            country_of_origin = ""

        if not brand:
            try:
                brand = product["brand"]
            except:
                brand = ""

        try:
            pack_type = product["packaging"]
        except:
            pack_type = ""

        try:
            age_whisky = ''.join(re.findall('(\d+) year old', name.lower()))
        except:
            age_whisky = ""

        if not age_whisky:
            try:
                age_whisky = ''.join(re.findall('(\d+) years old', name.lower()))
            except:
                age_whisky = ""

        try:
            ABV = product["alcoholDetails"]["percentByVolume"]
        except:
            ABV = "NA"

        try:
            image = product["productImageUrls"]["extraLarge"]
        except:
            image = ""

        if not image:
            try:
                image = response.xpath('//div[@class="detailsContainer___wNaUH"]/img/@src').get()
            except:
                image = ''

        manufacturer = self.manufacture_check(brand)
        if not manufacturer:
            "NA"

        scraped_date = datetime.datetime.strftime(datetime.date.today(), "%d_%m_%Y")

        item = WaitroseItem()
        item['Id'] = response.meta["Id"]
        item['htmlpath'] = filepath
        item['Platform_Name'] = "waitrose"
        item['Platform_URL'] = response.meta["pro_url"]
        item['Product_id'] = product_id
        item['Category_1'] = category_1
        item['Category_2'] = category_2
        item['Category_3'] = category_3
        item['Category_4'] = category_4
        item['Category_5'] = category_5
        item['Category_6'] = category_6
        item['Category_7'] = category_7
        item['Category_8'] = category_8
        item['Sector'] = sector.replace("\n", "").replace(",", "").strip() if sector else "NA"
        item['SKU_Name'] = name
        item['Manufacturer'] = manufacturer.replace(",", "") if manufacturer else "NA"
        item['Brand'] = brand.replace("\n", "").replace("\t", "").replace("\a", "").replace(",",
                                                                                            "").strip() if brand else "NA"
        item['Pack_Size'] = size_pack
        item['Price'] = str(retail_price).replace("\n", "").replace("\t", "").replace("\a", "").replace(",",
                                                                                                        "").strip() if str(
            retail_price) else "NA"
        item['Promo_Price'] = str(promo_price).replace("\n", "").replace("\t", "").replace("\a", "").replace(",",
                                                                                                             "").strip() if str(
            promo_price) else "NA"
        item['Price_per_unit'] = str(unit_price).replace("\n", "").replace("\t", "").replace("\a", "").replace(",",
                                                                                                               "").strip() if str(
            unit_price) else "NA"
        item['Age_of_Whisky'] = age_whisky.replace("\n", "").replace("\t", "").replace("\a", "").replace(",",
                                                                                                         "").strip() if str(
            age_whisky) else "NA"
        item['Country_of_Origin'] = country_of_origin.replace("\n", "").replace("\t", "").replace("\a", "").replace(",",
                                                                                                                    "").strip() if country_of_origin else "NA"
        item['Distillery'] = "NA"
        item['Pack_type'] = "NA"
        item[
            'Tasting_Notes'] = "NA"  # unit_taste.replace("\n", "").replace("\t", "").replace("\a", "").replace(",", "").strip() if unit_taste else "NA"
        item['Image_Urls'] = image.replace("\n", "").replace("\t", "").replace("\a", "").replace(",", "").strip()
        item['ABV'] = str(ABV).replace("\n", "").replace("\t", "").replace("\a", "").replace(",", "").strip() if str(
            ABV) else "NA"
        item['scrape_date'] = scraped_date

        yield item


if __name__ == '__main__':
    execute("scrapy crawl waitrose_data".split())
