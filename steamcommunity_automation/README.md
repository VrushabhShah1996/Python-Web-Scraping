# Steam Market Scraper

This project is a web scraping tool designed to gather data from the Steam Community Market. The project uses Selenium
for web scraping and MongoDB for storing the extracted data.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Database Structure](#database-structure)
- [Logging](#logging)
- [License](#license)

## Installation

### Prerequisites

1. **Python 3.10**
2. **MongoDB** - Make sure MongoDB is installed and running locally or on a server.
3. **Selenium WebDriver** - Specifically, the Chrome WebDriver needs to be installed and available on your system.
4. **Chrome Browser** - Selenium uses Chrome for scraping, so it must be installed.

### Install dependencies

```bash
pip install -r requirements.txt
```

## `db_setup.py` - MongoDB Setup for Steam Market Scraper

This file, `db_setup.py`, is responsible for initializing and managing MongoDB collections used in the Steam Market
Scraper project. It ensures that the necessary indexes are created in MongoDB collections to prevent duplicate entries
and optimize query performance.

## Features

- **Collection Initialization**: The script initializes three collections in MongoDB, specifically designed to store
  game links, product data, and listing URLs from the Steam Market.
- **Index Management**: The script creates unique indexes on key fields to avoid duplication and improve search
  efficiency.

## Functions

### `initialize_collections(db)`

This function initializes the required MongoDB collections and ensures that proper indexing is in place. It takes
the `db` object, which is the MongoDB database connection, and returns three collections:

- `steamcommunity_game_links`: Stores game URLs.
- `steamcommunity_data`: Stores detailed product information.
- `steamcommunity_links`: Stores product listing URLs.

Each collection will have a unique index on a specified field:

- `game_link` in `steamcommunity_game_links`.
- `Url` in `steamcommunity_data`.
- `product_url` in `steamcommunity_links`.

#### Example

```python
game_collection, product_collection, listing_collection = initialize_collections(db)
```

# `driver_setup.py` - Selenium WebDriver Initialization for Steam Market Scraper

This file, `driver_setup.py`, is responsible for setting up and initializing the Selenium WebDriver used in the Steam
Market Scraper. The script configures the WebDriver with randomized user agents and manages retries to handle potential
initialization failures.

## Features

- **WebDriver Initialization**: Initializes a Selenium WebDriver instance with necessary configurations for web
  scraping.
- **Randomized User-Agent**: Rotates between different user-agent strings to avoid detection and improve scraping
  success.
- **Retry Mechanism**: Includes retry logic to handle initialization failures, ensuring the WebDriver is properly
  launched.

## Functions

### `init_driver()`

This function initializes the Selenium WebDriver with specific options, including randomized user-agent strings, and
handles WebDriver initialization retries.

- **Options Configured**:
    - **No Sandbox**: `--no-sandbox` is used for compatibility in environments where sandboxing can cause issues.
    - **Disable Dev Shm Usage**: `--disable-dev-shm-usage` prevents WebDriver from encountering shared memory
      limitations.
    - **Window Size**: The browser window is set to `1920x1080` for optimal page rendering during scraping.

- **Randomized User-Agent**: A list of user-agent strings is used to randomly set the user-agent for each WebDriver
  instance to help avoid scraping blocks.

- **Retry Logic**: The function attempts to initialize the WebDriver up to 3 times if the initialization fails. If all
  attempts fail, it raises a `RuntimeError`.

# `data_extraction.py` - Steam Market Data Extraction

This script, `data_extraction.py`, is responsible for scraping data from the Steam Community Market. It uses Selenium
WebDriver to automate the scraping process and interacts with MongoDB to store the extracted game links, product
listings, and product details.

## Features

- **Game Link Extraction**: Scrapes links to games from the Steam Market.
- **Product Listing Extraction**: Extracts product URLs from game pages.
- **Product Details Extraction**: Retrieves and stores detailed product information such as prices and offers.

## Functions

### `fetch_page_source(driver, url)`

A helper function that fetches the HTML page source for a given URL with retry logic to handle timeouts and WebDriver
exceptions. It introduces randomized delays to avoid detection as a bot.

- **Parameters**:
    - `driver`: The Selenium WebDriver instance.
    - `url`: The URL of the page to fetch.

### `all_games(game_collection)`

This function scrapes all game links from the Steam Market's main page and stores them in the `game_collection`. It
creates a pending entry for each game link in the MongoDB collection.

- **Parameters**:
    - `game_collection`: The MongoDB collection where game links will be stored.

### `game_listing(game_collection, listing_collection)`

This function scrapes product listing URLs for each game found in the `game_collection`. The links are inserted into
the `listing_collection` with a pending status.

- **Parameters**:
    - `game_collection`: MongoDB collection storing the game links.
    - `listing_collection`: MongoDB collection for storing product URLs.

- **Workflow**:
    - For each pending game, it paginates through the game’s product listing pages and extracts the product URLs.
    - Inserts the product links into the MongoDB `listing_collection`.

### `pdp_data(listing_collection, product_collection)`

This function extracts detailed product data from each product page URL in the `listing_collection`. The extracted data
includes the product name, buy/sell prices, and buy/sell offers, which are stored in the `product_collection`.

- **Parameters**:
    - `listing_collection`: MongoDB collection with product URLs.
    - `product_collection`: MongoDB collection where product details will be stored.

- **Workflow**:
    - For each pending product, it navigates to the product page, extracts product information, and inserts it into
      the `product_collection`.
    - Updates the product's status to `done` in the `listing_collection` once data is successfully extracted.

### `parse_offer_details(driver, offer_type)`

A helper function to extract price and offer details for both buy and sell offers.

- **Parameters**:
    - `driver`: The Selenium WebDriver instance.
    - `offer_type`: Either 'buy' or 'sell' to specify the type of offer details being extracted.

- **Returns**:
    - Price and offer count extracted from the page.

### `save_product_data(name, url, sell_price, sell_offers, buy_price, buy_offers, product_collection)`

This function saves the extracted product data into the MongoDB `product_collection`.

- **Parameters**:
    - `name`: Name of the product.
    - `url`: URL of the product page.
    - `sell_price`: Selling price of the product.
    - `sell_offers`: Number of sell offers.
    - `buy_price`: Buying price of the product.
    - `buy_offers`: Number of buy offers.
    - `product_collection`: MongoDB collection for storing product details.

### `update_listing_status(field_name, collection_name)`

This helper function updates the status of a product or game to `done` after its data has been successfully scraped.

- **Parameters**:
    - `field_name`: The URL or identifier of the item.
    - `collection_name`: The MongoDB collection where the item is stored.

## Workflow Overview

1. **Game Links Scraping**:
    - Use `all_games(game_collection)` to scrape all game links from the Steam Market and store them in
      the `game_collection`.

2. **Product Listing Scraping**:
    - Use `game_listing(game_collection, listing_collection)` to scrape product URLs from each game page and store them
      in the `listing_collection`.

3. **Product Data Extraction**:
    - Use `pdp_data(listing_collection, product_collection)` to extract detailed product information like prices and
      offers, and store them in the `product_collection`.

## Logging

The script logs various activities and errors using Python’s `logging` module:

- Info logs are generated for successful operations like fetching pages and inserting data.
- Warning logs are used when duplicate data is detected.
- Error logs capture exceptions and issues encountered during scraping or database interactions.

## Conclusion

The `data_extraction.py` script is a crucial part of the Steam Market Scraper, automating the data collection process
from Steam and ensuring that the information is stored efficiently in MongoDB. It handles everything from initial game
link extraction to detailed product data collection, all while managing errors and retrying failed operations to ensure
reliable data scraping.

# `main.py` - Steam Market Scraper Main Execution

The `main.py` file serves as the entry point for the Steam Market Scraper. It initializes the database connection, sets
up the required MongoDB collections, and triggers the data extraction process for the Steam Community Market.

## Features

- **MongoDB Connection**: Connects to a local MongoDB instance and creates a database named `steamcommunity`.
- **Collection Initialization**: Uses `db_setup.py` to initialize MongoDB collections and ensure that the necessary
  indexes are created.
- **Data Extraction**: Calls functions from `data_extraction.py` to start scraping data from the Steam Community Market,
  including product details.

## Functions and Workflow

### MongoDB Connection

The script connects to MongoDB using the following:

```python
client = MongoClient('mongodb://localhost:27017/')
db = client['steamcommunity']
```

## MongoDB Collections

- **`steamcommunity_game_links`**: Stores game URLs with a status of either `pending` or `done`.
- **`steamcommunity_links`**: Stores product listing URLs extracted from game pages.
- **`steamcommunity_data`**: Stores detailed product information, including prices and offers.

## Logging

- The project uses Python's logging module to log important events, including errors, information, and warnings. Logs
  are recorded for events like:

- Successful WebDriver initialization.
- Data insertion into MongoDB.
- Errors during data scraping or insertion.
- Retrying on failed operations.

### Summary:

- **Installation**: Describes the prerequisites and steps to install dependencies, including how to set up MongoDB and
  the Chrome WebDriver.
- **Usage**: Explains how to start MongoDB and run the script.
- **File Structure**: Provides a detailed explanation of each file's role and functions.
- **Database Structure**: Describes the MongoDB collections and indexing strategy.
- **Logging**: Outlines the logging mechanism.
- **License**: Specifies the licensing information.

You can now copy-paste this content into your `README.md` file.
