import os
import requests
import pandas as pd

class HypeFlyScraper:
    def __init__(self):
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'content-type': 'application/json',
            'origin': 'https://hypefly.co.in',
            'priority': 'u=1, i',
            'referer': 'https://hypefly.co.in/',
            'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        }
        self.all_brands = ["Nike", "Adidas", "Off-White", "New Balance", "Cactus Jack"]
        self.scrape_all_brands()

    def fetch_json(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def scrape_all_brands(self):
        for brand in self.all_brands:
            print(f"Processing brand: {brand}")
            brand_url = f'https://api.hypefly.co.in/api/core/collection/all-sneakers?brands={brand.replace(" ", "%20")}&price__lt=1000001&price__gt=-1'
            all_listings = self.fetch_json(brand_url)

            if all_listings is not None:
                for listing in all_listings:
                    self.process_listing(listing, brand)

    def process_listing(self, listing, brand):
        slug = listing.get("slug")
        details_url = f'https://api.hypefly.co.in/api/core/product/{slug}'
        details = self.fetch_json(details_url)

        if details is not None:
            title = details.get("title", "")
            body = details.get("description", "").replace("Hype Fly India", "HustleCulture")
            product_type = details.get("type", "")

            images = [{"alt_text": img.get("alt_text", ""), "Image": img.get("full_size_desktop", "")} for img in details.get("images", [])]

            variants = details.get("variants", [])
            for variant in variants:
                payload = self.create_payload(details, variant)
                self.save_to_csv(payload, brand)

    def create_payload(self, details, variant):
        return {
            "Handle": details.get("slug", ""),
            "Title": details.get("title", ""),
            "Body (HTML)": details.get("description", "").replace("Hype Fly India", "HustleCulture"),
            "Vendor": "",
            "Product Category": "Apparel & Accessories > Shoes",
            "Type": details.get("type", ""),
            "Tags": "",
            "Published": True,
            "Option1 Name": "size",
            "Option1 Value": variant.get("size"),
            "Option2 Name": "",
            "Option2 Value": "",
            "Option3 Name": "",
            "Option3 Value": "",
            "Variant SKU": "",
            "Variant Grams": "0",
            "Variant Inventory Tracker": "shopify",
            "Variant Inventory Qty": variant.get("quantity"),
            "Variant Inventory Policy": "deny",
            "Variant Fulfillment Service": "manual",
            "Variant Price": variant.get("price"),
            "Variant Compare At Price": variant.get("compare_at"),
            "Variant Requires Shipping": True,
            "Variant Taxable": False,
            "Variant Barcode": "",
            "Image Src": "",
            "Image Position": "",
            "Image Alt Text": "",
            "Gift Card": "",
            "SEO Title": "",
            "SEO Description": "",
            "Google Shopping / Google Product Category": "",
            "Google Shopping / Gender": "",
            "Google Shopping / Age Group": "",
            "Google Shopping / MPN": "",
            "Google Shopping / Condition": "",
            "Google Shopping / Custom Product": "",
            "Google Shopping / Custom Label 0": "",
            "Google Shopping / Custom Label 1": "",
            "Google Shopping / Custom Label 2": "",
            "Google Shopping / Custom Label 3": "",
            "Google Shopping / Custom Label 4": "",
            "Variant Image": "",
            "Variant Weight Unit": "",
            "Variant Tax Code": "",
            "Cost per item": "",
            "Included / India": "",
            "Price / India": "",
            "Compare At Price / India": "",
            "Included / International": "",
            "Price / International": "",
            "Compare At Price / International": "",
            "Status": "active"
        }

    def save_to_csv(self, payload, brand):
        filename = f'hypefly_{brand}.csv'
        df = pd.DataFrame([payload])
        if os.path.exists(filename):
            df.to_csv(filename, mode='a', index=False, header=False, encoding='utf-8')
        else:
            df.to_csv(filename, mode='w', index=False, header=True, encoding='utf-8')

if __name__ == '__main__':
    HypeFlyScraper()
