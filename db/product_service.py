from typing import Union
from pymongo import MongoClient
from datetime import datetime


class ProductService:
    def __init__(
        self,
        mongo_uri: str = "mongodb://localhost:27017/",
        db_name: str = "foodforecast",
    ):
        self.__client = MongoClient(mongo_uri)
        self.__products_collection = self.__client[db_name]["products"]
        self.__prices_collection = self.__client[db_name]["prices"]
        self.__basic_basket_collection = self.__client[db_name]["baskets"]
        self.__price_drops_collection = self.__client[db_name]["priceDrops"]

    def upload_basket_to_db(self, basket: dict[str, Union[str, float, list[dict]]]):
        self.__basic_basket_collection.insert_one(basket)
        print("Basket uploaded successfully to the database.")

    def upload_products_and_prices_to_db(
        self, products: list[dict[str, str]], prices: list[dict[str, Union[str, float]]]
    ):
        product_urls = [product["productUrl"] for product in products]

        existing_products = self.__products_collection.find(
            {"productUrl": {"$in": product_urls}}
        )

        existing_product_urls = set(
            product["productUrl"] for product in existing_products
        )

        filtered_products = [
            product
            for product in products
            if product["productUrl"] not in existing_product_urls
        ]

        if filtered_products:
            added_products = self.__products_collection.insert_many(filtered_products)
            print(f"Added {len(added_products.inserted_ids)} new products.")
        else:
            print("No new products to add.")

        price_drop_entries = []
        for price in prices:
            existing_product = self.__prices_collection.find_one(
                {"productUrl": price["productUrl"]}, sort=[("date", -1)]
            )

            if existing_product:
                current_price = price["productPrice"]
                previous_price = existing_product["productPrice"]
                price_diff = current_price - previous_price

                if current_price != previous_price:
                    price_change_type = "rise" if price_diff > 0 else "drop"
                    price_drop_entry = {
                        "productName": price["productName"],
                        "productUrl": price["productUrl"],
                        "priceDifference": price_diff,
                        "previousPrice": previous_price,
                        "currentPrice": current_price,
                        "priceChangeType": price_change_type,
                        "date": datetime.now().isoformat(),
                    }
                    price_drop_entries.append(price_drop_entry)

        if prices:
            added_prices = self.__prices_collection.insert_many(prices)
            print(f"Added {len(added_prices.inserted_ids)} new prices.")

        if price_drop_entries:
            added_price_drops = self.__price_drops_collection.insert_many(
                price_drop_entries
            )
            print(f"Added {len(added_price_drops.inserted_ids)} price drops.")
        else:
            print("No price drops found.")

    def purge_collections(self):
        self.__products_collection.drop()
        self.__prices_collection.drop()
        self.__basic_basket_collection.drop()
        self.__price_drops_collection.drop()
        print("Collections purged successfully.")
