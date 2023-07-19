from typing import Union
from pymongo import MongoClient


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
            added = self.__products_collection.insert_many(filtered_products)
            print(f"Added {len(added.inserted_ids)} new products.")
        else:
            print("No new products to add.")

        self.__prices_collection.insert_many(prices)
        print("Prices uploaded successfully to the database.")
