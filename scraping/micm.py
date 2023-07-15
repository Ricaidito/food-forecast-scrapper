from typing import Union
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
from scraping.categories.sources.micm_category import MICMPCategory
from scraping.categories.product_mapper import ProductMapper


class MICMP:
    def __init__(self, category: MICMPCategory, wait_time_seconds: int = 1):
        self.__url = "https://preciosjustos.micm.gob.do/"
        self.__wait_time = wait_time_seconds
        self.__category = category

    def __get_basket_html(self) -> str:
        driver_options = ChromeOptions()
        driver_options.add_argument("--headless=new")

        driver = webdriver.Chrome(options=driver_options)

        driver.get(self.__url)

        driver.implicitly_wait(self.__wait_time)

        html_doc = driver.page_source

        driver.quit()

        return html_doc

    def __get_section_html(self) -> str:
        driver_options = ChromeOptions()
        driver_options.add_argument("--headless=new")

        driver = webdriver.Chrome(options=driver_options)

        driver.get(self.__url)
        driver.implicitly_wait(self.__wait_time)

        meat_category = driver.find_element(
            By.CSS_SELECTOR,
            f"li.nav-item[data-category='{self.__category.value}'] a.nav-link",
        )
        meat_category.click()

        driver.implicitly_wait(self.__wait_time)

        while True:
            try:
                driver.implicitly_wait(self.__wait_time)

                mas_productos_button = driver.find_element(
                    By.XPATH, "//*[contains(text(), 'Mas Productos')]"
                )

                driver.execute_script("arguments[0].click();", mas_productos_button)

                if not mas_productos_button.is_displayed():
                    break

            except NoSuchElementException:
                break

        driver.implicitly_wait(self.__wait_time)

        html_content = driver.page_source

        driver.quit()

        return html_content

    def __parse_price(self, price: str) -> float:
        return float(price.split(" ")[1])

    def __calculate_total_amount(
        self, basic_basket_products: list[dict[str, str]]
    ) -> float:
        total_amount = 0
        for product in basic_basket_products:
            total_amount += product["productPrice"]

        return round(total_amount, 2)

    def __extract_basket(
        self, html_content: str
    ) -> dict[str, Union[str, float, list[dict[str, Union[str, float]]]]]:
        basic_basket_products = []
        soup = BeautifulSoup(html_content, "html.parser")

        products = soup.find_all("div", class_="product-card")

        date = datetime.now().isoformat()

        for product in products:
            name = product.find("span", class_="productTitle").text.strip()
            price = product.find("strong", class_="productPrice").text.strip()
            image = product.find("img").get("src")
            basic_basket_products.append(
                {
                    "productName": name,
                    "productPrice": self.__parse_price(price),
                    "imageUrl": f"https://preciosjustos.micm.gob.do/{image}",
                }
            )

        basket = {
            "productsAmount": len(basic_basket_products),
            "totalAmount": self.__calculate_total_amount(basic_basket_products),
            "products": basic_basket_products,
            "extractionDate": date,
            "origin": "micmp",
        }

        return basket

    def __extract_section(
        self, html_content: str
    ) -> tuple[list[dict[str, str]], list[dict[str, Union[str, float]]]]:
        items = []
        prices = []
        soup = BeautifulSoup(html_content, "html.parser")

        products = soup.find_all("div", class_="product-card")

        for product in products:
            name = product.find("span", class_="productTitle").text.strip()
            price = product.find("strong", class_="productPrice").text.strip()
            image = product.find("img").get("src")
            item_url = product.find("span", class_="productTitle").text.strip()
            date = datetime.now().isoformat()
            product_to_add = {
                "productName": name,
                "category": ProductMapper.get_product_category(self.__category).value,
                "imageUrl": f"https://preciosjustos.micm.gob.do/{image}",
                "productUrl": item_url,
                "origin": "micmp",
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

    def get_basic_basket(self):
        html = self.__get_basket_html()
        basic_basket = self.__extract_basket(html)
        return basic_basket

    def get_products(self):
        html = self.__get_section_html()
        items, prices = self.__extract_section(html)
        return items, prices

    def switch_category(self, category: MICMPCategory):
        self.__category = category
