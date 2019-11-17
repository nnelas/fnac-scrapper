import logging
import re
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

from fnac_prices import settings
from selenium import webdriver

from fnac_prices.exceptions.fnac import FNACLoginException
from fnac_prices.models.product import Product, Inventory, Offer, Changed


class FNACSelenium:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.logger = logging.getLogger("Selenium")
        self.browser = self.__make_selenium()
        self.inventory = Inventory()

    @staticmethod
    def __make_selenium():
        options = Options()
        options.headless = settings.HEADLESS
        return webdriver.Chrome(settings.CHROME_PATH, chrome_options=options)

    def __login(self):
        try:
            username = self.browser.find_element_by_id("email")
            password = self.browser.find_element_by_id("password")
            button = self.browser.find_element_by_class_name("button__signin")

            if not username.get_attribute("value"):
                username.send_keys(self.email)

            password.send_keys(self.password)
            button.click()

            time.sleep(settings.TIMER_PAGE)

            if settings.LOGIN_URL in self.browser.current_url:
                raise FNACLoginException

        except NoSuchElementException:  # most likely already logged in
            pass

    def make_login(self):
        self.browser.get(settings.LOGIN_URL)
        self.__login()

    def open_inventory(self, index: int):
        self.browser.get(settings.INVENTORY_URL.format(id=index, num=settings.PRODUCTS))
        self.__login()

    def get_total_products(self) -> int:
        total = self.browser.find_element_by_class_name("filters__total").text
        return int(re.search(r"(\d+)", total).group(1))

    def query_inventory(self) -> Inventory:
        def get_url(product) -> str:
            details = product.find_elements_by_tag_name("td")
            for i, detail in enumerate(details):
                if i == 1:  # link
                    return detail.find_element_by_tag_name("a").get_attribute("href")

        table = self.browser.find_element_by_id("myOfferTable")
        products = table.find_elements_by_tag_name("tr")
        for product in products:
            url = get_url(product)
            if url:
                self.inventory.products.append(Product(get_url(product)))

        return self.inventory

    def query_views(self, inventory: Inventory) -> Inventory:
        for idx, product in enumerate(inventory.products):
            if idx % 10 == 0:
                self.logger.info("Fetching product information from products {} to {}"
                                 .format(idx, idx + 10))
            self.browser.get(product.url)
            product.view = self.browser.find_element_by_class_name("prod")\
                .find_element_by_tag_name("a").get_attribute("href")
            time.sleep(settings.TIMER_OP)
        return self.inventory

    def query_products(self, inventory: Inventory) -> Inventory:
        for idx, product in enumerate(inventory.products):
            try:
                if idx % 10 == 0:
                    self.logger.info("Fetching other prices from products {} to {}"
                                     .format(idx, idx+10))
                self.browser.get(product.view)
                product.name = self.browser\
                    .find_element_by_class_name("f-productHeader-Title").text
                time.sleep(settings.TIMER_OP)

                unordered_list = self.browser.find_element_by_class_name("f-otherOffers-list")
                offers = unordered_list.find_elements_by_tag_name("li")
                for offer in offers:
                    price = offer.find_element_by_class_name("f-otherOffers-itemPrice").text
                    shipping = offer.find_element_by_class_name("f-otherOffers-shipping").text
                    store = offer.find_element_by_class_name("f-otherOffers-sellerName").text

                    # to cope with promotions. last price is first
                    prices = re.findall(r"(\d*,\d* €)", price)
                    for price in prices:
                        # to remove currency and cast to float
                        price = price.replace(",", ".")[:-2]
                        break

                    shipping = shipping.replace(",", ".").replace("Custos de envio +", "")[:-2]

                    product.offers.append(
                        Offer(
                            name=store,
                            price=float(price),
                            shipping=float(shipping)
                        ))
            except NoSuchElementException:
                self.logger.warning("Couldn't fetch product information for item: '{}'"
                                    .format(product.view))
        return self.inventory

    def change_product_price(self, changed: Changed):
        self.open_inventory(1)  # only needed to login, if input file is added
        for product in changed.products:
            try:
                self.browser.get(product.url)
                price = self.browser.find_element_by_id("shop_product_price")
                price.clear()
                price.send_keys(str(product.new_offer.price))
                button = self.browser.find_element_by_id("shop_product_publish")
                button.click()
                self.logger.info("Changed price for item: '{}'".format(product.url))
                time.sleep(settings.TIMER_OP)
            except NoSuchElementException:
                self.logger.warning("Couldn't change price for item: '{}'"
                                    .format(product.url))
