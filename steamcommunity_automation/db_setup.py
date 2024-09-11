import logging
from pymongo import ASCENDING, errors


def check_or_create_index(collection, field_name):
    """Check if the index exists, and create it if not."""
    existing_indexes = collection.index_information()
    if not any(field_name in index['key'][0] for index in existing_indexes.values()):
        try:
            collection.create_index([(field_name, ASCENDING)], unique=True)
            logging.info(f"Unique index created on {field_name} for {collection.name}")
        except errors.PyMongoError as e:
            logging.error(f"Error creating index on {field_name}: {e}")
    else:
        logging.info(f"Index on {field_name} already exists for {collection.name}")


def initialize_collections(db):
    """Initialize and return collections with indexes checked."""
    game_collection = db['steamcommunity_game_links']
    product_collection = db['steamcommunity_data']
    listing_collection = db['steamcommunity_links']

    # Ensure indexes are created only if they don't already exist
    check_or_create_index(game_collection, "game_link")
    check_or_create_index(product_collection, "Url")
    check_or_create_index(listing_collection, "product_url")

    return game_collection, product_collection, listing_collection
