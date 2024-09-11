from pymongo import MongoClient
from db_setup import initialize_collections
from data_extraction import *

if __name__ == '__main__':
    client = MongoClient('mongodb://localhost:27017/')
    db = client['steamcommunity']

    # Initialize collections and indexes if necessary
    game_collection, product_collection, listing_collection = initialize_collections(db)

    # Start the data extraction process
    # all_games(game_collection)
    # game_listing(game_collection, listing_collection)
    pdp_data(listing_collection, product_collection)
