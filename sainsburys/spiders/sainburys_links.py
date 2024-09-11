import scrapy
import json
from scrapy.cmdline import execute
import pymysql
import sainsburys.db_config as db
from sainsburys.items import SainsburyslinkItem


# from scrapyprojects.sainsburys.sainsburys.middlewares import CloudScraperMiddleware


class SainsburysSpider(scrapy.Spider):
    name = "sainsburys"
    allowed_domains = ['sainsburys.co.uk']

    def __init__(self):
        super().__init__()
        self.con = pymysql.connect(host=db.db_host, user=db.db_user, password=db.db_password)
        self.cursor = self.con.cursor()
        self.PAGE_SAVE_PATH = f"/home/vrusahbh/PycharmProjects/pythonProject/scrapyprojects/sainsburys"
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

    def start_requests(self):

        all_category_code = [12287, 199702, 12286, 12291, 12293, 41153, 12294, 510355, 12306,
                             458395, 508357, 458855, 458854]

        for category_code in all_category_code:
            page_number = 1
            url = f'https://www.sainsburys.co.uk/groceries-api/gol-services/product/v1/product?filter[keyword]=&filter[category]={category_code}&browse=true&hfss_restricted=false&page_number={page_number}&sort_order=FAVOURITES_FIRST&include[PRODUCT_AD]=citrus&citrus_placement=category-only'
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse,
                                 meta={"Category_Id": category_code, "page_number": page_number})

    def parse(self, response):
        filepath = self.PAGE_SAVE_PATH + f'/link_pages/{response.meta["Category_Id"]}.txt'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)
            f.close()
        category_code = response.meta["Category_Id"]
        page_number = response.meta["page_number"]
        data = json.loads(response.body)
        all_products = []

        try:
            all_data = data["products"]
            all_products.extend(all_data)
        except:
            all_data = None

        if not all_data:
            return None
        else:
            page_number += 1
        try:
            all_sponsors_data = data["ads"]["sponsored_products"]["spotlight_product_ads"]
            all_products.extend(all_sponsors_data)
        except:
            pass

        for product in all_products:
            item = SainsburyslinkItem()
            try:
                links = product["full_url"]
                product_id = product["product_uid"]
            except:
                try:
                    links = product["product"]["full_url"]
                    product_id = product["product"]["product_uid"]
                except:
                    continue
            print(links, "\t", product_id)

            item['Product_URL'] = links
            item['Product_id'] = product_id
            item["Category_Id"] = response.meta["Category_Id"]
            item['Status'] = 'Pending'

            yield item

        url = f'https://www.sainsburys.co.uk/groceries-api/gol-services/product/v1/product?filter[keyword]=&filter[category]={category_code}&browse=true&hfss_restricted=false&page_number={page_number}&sort_order=FAVOURITES_FIRST&include[PRODUCT_AD]=citrus&citrus_placement=category-only'
        yield scrapy.Request(url=url, headers=self.headers, callback=self.parse,
                             meta={"Category_Id": category_code, "page_number": page_number})


if __name__ == '__main__':
    execute('scrapy crawl sainsburys'.split())
