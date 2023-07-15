from typing import Union
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from bs4 import BeautifulSoup
from datetime import datetime
from scraping.categories.sources.jumbo_category import JumboCategory
from scraping.categories.product_mapper import ProductMapper


class Jumbo:
    def __init__(self, category: JumboCategory):
        self.__category = category
        self.__url = f"https://jumbo.com.do/supermercado/{self.__category.value}?product_list_limit=all"

    def __extract_products(self) -> str:
        driver_options = ChromeOptions()
        driver_options.add_argument("--headless=new")
        driver = webdriver.Chrome(options=driver_options)

        driver.get(self.__url)

        html = driver.page_source

        driver.quit()

        return html

    def __parse_price(self, price: str) -> float:
        return float(price.split("$")[1].replace(",", ""))

    def __get_products(
        self, html_content: str
    ) -> tuple[list[dict[str, str]], list[dict[str, Union[str, float]]]]:
        items = []
        prices = []
        soup = BeautifulSoup(html_content, "html.parser")

        products = soup.find_all("div", class_="product-item-info")

        for product in products:
            name = product.find("div", class_="product-item-tile__name").text.strip()
            price = product.find(
                "span", class_="product-item-tile__price-current"
            ).text.strip()
            image = product.find("img", class_="product-item-tile__img")["src"]
            item_url = product.find("a", class_="product-item-tile__link")["href"]
            date = datetime.now().isoformat()
            product_to_add = {
                "productName": name,
                "category": ProductMapper.get_product_category(self.__category).value,
                "imageUrl": image,
                "productUrl": item_url,
                "origin": "jumbo",
                "extractionDate": date,
            }
            price_to_add = {
                "productPrice": self.__parse_price(price),
                "productUrl": item_url,
                "date": date,
            }
            items.append(product_to_add)
            prices.append(price_to_add)

        return items, prices

    def switch_category(self, category: JumboCategory):
        self.__category = category
        self.__url = f"https://jumbo.com.do/supermercado/{self.__category.value}?product_list_limit=all"

    def get_products(
        self,
    ) -> tuple[list[dict[str, str]], list[dict[str, Union[str, float]]]]:
        html = self.__extract_products()
        items, prices = self.__get_products(html)
        return items, prices
