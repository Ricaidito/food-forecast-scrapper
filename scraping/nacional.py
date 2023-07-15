from typing import Union
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from datetime import datetime
from scraping.categories.sources.nacional_category import NacionalCategory
from scraping.categories.product_mapper import ProductMapper


class Nacional:
    def __init__(self, category: NacionalCategory, wait_time_seconds: int = 7):
        self.__wait_time = wait_time_seconds
        self.__category = category
        self.__base_url = f"https://supermercadosnacional.com/{self.__category.value}"

    def __parse_price(self, price: str) -> float:
        return float(price.replace("$", "").replace(",", ""))

    def __extract_products(
        self,
    ) -> tuple[list[dict[str, str]], list[dict[str, Union[str, float]]]]:
        driver_options = ChromeOptions()
        driver_options.add_argument("--headless=new")
        driver = webdriver.Chrome(options=driver_options)

        driver.get(self.__base_url)

        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(self.__wait_time)

            new_height = driver.execute_script("return document.body.scrollHeight")

            try:
                mas_productos_button = driver.find_element(
                    By.XPATH, "//*[contains(text(), 'Ver Más')]"
                )

                driver.execute_script("arguments[0].click();", mas_productos_button)
                time.sleep(self.__wait_time)

                if not mas_productos_button.is_displayed():
                    if new_height == last_height:
                        break

            except Exception:
                if new_height == last_height:
                    break

            last_height = new_height

        html = driver.page_source

        items = []
        prices = []

        soup = BeautifulSoup(html, "html.parser")

        products = soup.find_all("li", class_="product-item")

        for product in products:
            name = product.find("a", class_="product-item-link").text.strip()
            price = product.find("span", class_="price").text.strip()
            image = product.find("img", class_="product-image-photo")["src"]
            item_url = product.find("a", class_="product photo product-item-photo")[
                "href"
            ]
            date = datetime.now().isoformat()
            product_to_add = {
                "productName": name,
                "category": ProductMapper.get_product_category(self.__category).value,
                "imageUrl": image,
                "productUrl": item_url,
                "origin": "nacional",
                "extractionDate": date,
            }
            price_to_add = {
                "productPrice": self.__parse_price(price),
                "productUrl": item_url,
                "date": date,
            }
            items.append(product_to_add)
            prices.append(price_to_add)

        driver.quit()

        return items, prices

    def get_products(
        self,
    ) -> tuple[list[dict[str, str]], list[dict[str, Union[str, float]]]]:
        items, prices = self.__extract_products()
        return items, prices

    def switch_category(self, category: NacionalCategory):
        self.__category = category
        self.__base_url = f"https://supermercadosnacional.com/{self.__category.value}"
