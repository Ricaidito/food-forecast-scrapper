from typing import Union
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from datetime import datetime
from scraping.categories.sources.sirena_category import SirenaCategory
from scraping.categories.product_mapper import ProductMapper


class Sirena:
    def __init__(self, category: SirenaCategory, wait_time_seconds: int = 5):
        self.__wait_time = wait_time_seconds
        self.__category = category
        self.__base_url = f"https://sirena.do/products/category/{self.__category.value}?page=1&limit=0&sort=1"

    def __extract_products(self) -> str:
        driver_options = ChromeOptions()
        driver_options.add_argument("--headless=new")
        driver = webdriver.Chrome(options=driver_options)

        driver.get(self.__base_url)

        WebDriverWait(driver, self.__wait_time).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.item-product-info"))
        )
        driver.implicitly_wait(self.__wait_time)

        html_doc = driver.page_source

        driver.quit()

        return html_doc

    def __parse_price(self, price: str) -> float:
        return float(price.split("$")[1].replace(",", ""))

    def __extract_image_url(self, image: str) -> str:
        return image.split("(")[1].split(")")[0]

    def __get_products(
        self, html_content: str
    ) -> tuple[list[dict[str, str]], list[dict[str, Union[str, float]]]]:
        items = []
        prices = []
        soup = BeautifulSoup(html_content, "html.parser")

        products = soup.find_all("div", class_="item-product")

        for product in products:
            name = product.find("p", class_="item-product-title").text.strip()
            price = product.find("p", class_="item-product-price").strong.text.strip()
            image = product.find("a", class_="item-product-image")["style"]
            item_url = product.find("a", class_="item-product-image")["href"]
            date = datetime.now().isoformat()
            product_to_add = {
                "productName": name,
                "category": ProductMapper.get_product_category(self.__category).value,
                "imageUrl": self.__extract_image_url(image),
                "productUrl": f"https://sirena.do{item_url}",
                "origin": "sirena",
                "extractionDate": date,
            }
            price_to_add = {
                "productPrice": self.__parse_price(price),
                "productUrl": f"https://sirena.do{item_url}",
                "date": date,
            }
            items.append(product_to_add)
            prices.append(price_to_add)

        return items, prices

    def switch_category(self, category: SirenaCategory):
        self.__category = category
        self.__base_url = f"https://sirena.do/products/category/{self.__category.value}?page=1&limit=0&sort=1"

    def get_products(
        self,
    ) -> tuple[list[dict[str, str]], list[dict[str, Union[str, float]]]]:
        html = self.__extract_products()
        products, prices = self.__get_products(html)
        return products, prices
