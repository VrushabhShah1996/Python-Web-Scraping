import logging
import random
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from driver_setup import init_driver
from pymongo import errors


# Helper function to fetch page source with retry logic
def fetch_page_source(driver, url):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            logging.info(f"Fetching page: {url}")
            driver.get(url)
            time.sleep(random.uniform(2, 5))  # Random delay to avoid scraping detection
            return driver.page_source
        except (TimeoutException, WebDriverException) as e:
            logging.error(f"Failed to fetch page: {e}. Retrying... ({attempt + 1}/{max_retries})")
            time.sleep(random.uniform(5, 10))
    raise RuntimeError(f"Failed to retrieve page source after {max_retries} attempts.")


# Function to scrape all games and insert links into game_collection
def all_games(game_collection):
    driver = init_driver()
    try:
        driver.get("https://steamcommunity.com/market")
        time.sleep(2)
        elements = driver.find_elements(By.XPATH, '//a[@class="game_button"]')
        all_game_links = [element.get_attribute("href") for element in elements]

        documents = [{"game_link": link, "status": "pending"} for link in all_game_links]

        try:
            game_collection.insert_many(documents, ordered=False)
            logging.info(f"Inserted game links into the database.")
        except errors.DuplicateKeyError:
            logging.warning(f"Duplicate game links detected.")
        except errors.PyMongoError as e:
            logging.error(f"Error inserting game links into the database: {e}")
    finally:
        driver.quit()


# Function to process game listings and extract product URLs
def game_listing(game_collection, listing_collection):
    driver = init_driver()
    old_page_source = ""
    try:
        pending_games = game_collection.find({'status': 'pending'})
        for game in pending_games:
            game_link = game["game_link"]
            page_count = 1
            while page_count < 51:
                game_page_url = f"{game_link}#p{page_count}_popular_desc"
                driver.get(game_page_url)
                time.sleep(2)
                if old_page_source == driver.page_source:
                    break
                else:
                    old_page_source = driver.page_source

                product_links_elements = driver.find_elements(By.XPATH, '//a[@class="market_listing_row_link"]')
                product_links = [element.get_attribute("href") for element in product_links_elements]

                documents = [{"product_url": link, "status": "pending"} for link in product_links]
                try:
                    listing_collection.insert_many(documents, ordered=False)
                    logging.info(f"Inserted product links from page {page_count} of {game_link}")
                except errors.DuplicateKeyError:
                    logging.warning(f"Duplicate product links detected.")
                except errors.PyMongoError as e:
                    logging.error(f"Error inserting product links into the database: {e}")

                page_count += 1

            # Mark game as processed
            update_listing_status(game_link, game_collection)
            # game_collection.update_one({"game_link": game_link}, {'$set': {'status': 'done'}})
    finally:
        driver.quit()


# Function to extract product details and save them into the product collection
def pdp_data(listing_collection, product_collection):

    try:
        pending_links = listing_collection.find({'status': 'pending'})
        for product in pending_links:
            driver = init_driver()
            url = product["product_url"]
            page_source = fetch_page_source(driver, url)

            try:
                name = driver.find_element(By.XPATH, '//h1[@id="largeiteminfo_item_name"]').text
                logging.info(f"Extracting data for product: {name}")
            except NoSuchElementException as e:
                logging.error(f"Failed to locate product name: {e}")
                continue

            driver.execute_script("window.scrollTo(0, 800);")
            time.sleep(1)

            sell_price, sell_offers = parse_offer_details(driver, 'sell')
            buy_price, buy_offers = parse_offer_details(driver, 'buy')

            save_product_data(name, url, sell_price, sell_offers, buy_price, buy_offers, product_collection)
            update_listing_status(url, listing_collection)
            driver.close()
            driver.quit()
    finally:
        driver.quit()


# Helper function to parse offer details
def parse_offer_details(driver, offer_type):
    if offer_type == 'sell':
        details_xpath = '//div[@id="market_commodity_forsale"]//span[@class="market_commodity_orders_header_promote"]'
    else:
        details_xpath = '//div[@id="market_commodity_buyrequests"]//span[@class="market_commodity_orders_header_promote"]'

    details_elements = driver.find_elements(By.XPATH, details_xpath)
    price, offers = "0", "0"
    for element in details_elements:
        text = element.text
        if "$" in text:
            price = text
        else:
            offers = text
    return price, offers


# Helper function to save product data
def save_product_data(name, url, sell_price, sell_offers, buy_price, buy_offers, product_collection):
    product_data = {
        "Name": name,
        "Buy/Sell Price": f"{buy_price}/{sell_price}",
        "Buy/Sell Offers": f"{buy_offers}/{sell_offers}",
        "Url": url
    }
    try:
        product_collection.insert_one(product_data)
        logging.info(f"Data successfully inserted for {name}")
    except errors.DuplicateKeyError:
        logging.warning(f"Duplicate document found for {name}")
    except errors.PyMongoError as e:
        logging.error(f"Failed to insert data for {name}: {e}")


# Helper function to update listing status
def update_listing_status(field_name, collection_name):
    try:
        collection_name.update_one({"product_url": field_name}, {'$set': {'status': 'done'}})
        logging.info(f"Listing status updated for {field_name}")
    except errors.PyMongoError as e:
        logging.error(f"Failed to update status for {field_name}: {e}")
