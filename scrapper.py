from db.product_service import ProductService
from scraping.categories.sources.jumbo_category import JumboCategory
from scraping.categories.sources.micm_category import MICMPCategory
from scraping.categories.sources.nacional_category import NacionalCategory
from scraping.categories.sources.sirena_category import SirenaCategory
from scraping.jumbo import Jumbo
from scraping.micm import MICMP
from scraping.nacional import Nacional
from scraping.sirena import Sirena
import requests


class ProductScrapper:
    def __init__(self):
        self.__product_service = ProductService()

    def __scrap_basket(self, upload_to_db: bool = True):
        print("\nStarting basket scraping...\n")
        micmp = MICMP(MICMPCategory.CARNES)
        print("\nGetting basic basket..")
        basic_basket = micmp.get_basic_basket()

        if upload_to_db:
            print("Uploading basic basket to db...")
            self.__product_service.upload_basket_to_db(basic_basket)
            print("Basic basket uploaded successfully to db.")

        print("\nBasket done.\n")

    def __scrap_micm(self, upload_to_db: bool = True):
        print("\nStarting MICM scraping...\n")
        for category in MICMPCategory.__members__.values():
            micmp = MICMP(category)
            print(f"\nGetting prices for category: [{category}]")
            products, prices = micmp.get_products()

            if upload_to_db:
                print(f"Uploading products to db for category: [{category}]")
                self.__product_service.upload_products_and_prices_to_db(
                    products, prices
                )
                print(f"Products successfully added to db for category: [{category}]")

        print("\nMICM done.\n")

    def __scrap_sirena(self, upload_to_db: bool = True):
        print("\nStarting La Sirena scraping...\n")
        for category in SirenaCategory.__members__.values():
            sirena = Sirena(category)
            print(f"\nGetting prices for category: [{category}]")
            products, prices = sirena.get_products()

            if upload_to_db:
                print(f"Uploading products to db for category: [{category}]")
                self.__product_service.upload_products_and_prices_to_db(
                    products, prices
                )
                print(f"Products successfully added to db for category: [{category}]")

        print("\nLa Sirena done.\n")

    def __scrap_jumbo(self, upload_to_db: bool = True):
        print("\nStarting Jumbo scraping...\n")
        for category in JumboCategory.__members__.values():
            jumbo = Jumbo(category)
            print(f"\nGetting prices for category: [{category}]")
            products, prices = jumbo.get_products()

            if upload_to_db:
                print(f"Uploading products to db for category: [{category}]")
                self.__product_service.upload_products_and_prices_to_db(
                    products, prices
                )
                print(f"Products successfully added to db for category: [{category}]")

        print("\nJumbo done.\n")

    def __scrap_nacional(self, upload_to_db: bool = True):
        print("\nStarting Nacional scraping...\n")
        for category in NacionalCategory.__members__.values():
            nacional = Nacional(category)
            print(f"\nGetting prices for category: [{category}]")
            products, prices = nacional.get_products()

            if upload_to_db:
                print(f"Uploading products to db for category: [{category}]")
                self.__product_service.upload_products_and_prices_to_db(
                    products, prices
                )
                print(f"Products successfully added to db for category: [{category}]")

        print("\nNacional done.\n")

    def do_scraping(
        self,
        basket: bool,
        micm: bool,
        sirena: bool,
        jumbo: bool,
        nacional: bool,
        upload_to_db: bool = True,
        purge_db: bool = False,
    ):
        if purge_db:
            print("\nPurging collections...\n")
            self.__product_service.purge_collections()

        print("\nStarting scraping...\n")
        if basket:
            self.__scrap_basket(upload_to_db)
        if micm:
            self.__scrap_micm(upload_to_db)
        if sirena:
            self.__scrap_sirena(upload_to_db)
        if jumbo:
            self.__scrap_jumbo(upload_to_db)
        if nacional:
            self.__scrap_nacional(upload_to_db)



        print("\nSending notifications\n")

        result = requests.get("https://food-forecast-server.azurewebsites.net/price-drops/send")
        print(result.text)

        print("\nScraping done.\n")

    def test_scraping(self):
        from datetime import datetime

        products = []
        prices = [
            {
                "productName": "Fajita de Res Lb.",
                "productPrice": 20,
                "productUrl": "https://sirena.do/products/index/fajita-de-res-lb",
                "date": datetime.now().isoformat(),
            },
        ]
        self.__product_service.upload_products_and_prices_to_db(products, prices)
