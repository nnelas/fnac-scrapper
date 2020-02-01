import logging
import time

import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

from fnac_prices import settings
from fnac_prices.exceptions.fnac_exceptions import FnacLoginException
from fnac_prices.models.product import Product, Inventory, Offer, Changed, Market


class FnacSelenium:
    def __init__(self, debug: bool, options: Options, inventory: Inventory):
        self.email = None
        self.password = None
        self.logger = logging.getLogger("Selenium")
        self.browser = self.__make_selenium(debug, options)
        self.inventory = inventory

    def __make_selenium(self, debug: bool, options: Options):
        if not debug:
            options.headless = settings.HEADLESS
        else:
            options.headless = False
        return webdriver.Chrome(settings.CHROME_PATH, chrome_options=options)

    def __login(self, email: str, password: str):
        try:
            element_username = self.browser.find_element_by_id("email")
            element_password = self.browser.find_element_by_id("password")
            element_button = self.browser.find_element_by_class_name("button__signin")

            if not element_username.get_attribute("value"):
                element_username.send_keys(email)

            element_password.send_keys(password)
            element_button.click()

            time.sleep(settings.TIMER_PAGE)

            if settings.LOGIN_URL in self.browser.current_url:
                raise FnacLoginException

        except NoSuchElementException:  # most likely already logged in
            pass

    def make_login(self, email: str, password: str):
        self.email, self.password = email, password  # cache it for future usages
        self.browser.get(settings.LOGIN_URL)
        self.__login(email, password)

    def open_inventory(self, index: int):
        self.browser.get(settings.INVENTORY_URL.format(id=index, num=settings.PRODUCTS))
        self.__login(self.email, self.password)

    def get_total_products(self) -> int:
        total = self.browser.find_element_by_class_name("filters__total").text
        return int(re.search(r"(\d+)", total).group(1))

    def query_inventory(self) -> Inventory:
        table = self.browser.find_element_by_id("myOfferTable")
        products = table.find_elements_by_tag_name("tr")
        for item in products:
            product = Product()
            details = item.find_elements_by_tag_name("td")
            for i, detail in enumerate(details):
                if i == 1:  # link
                    url = detail.find_element_by_tag_name("a").get_attribute("href")
                    product.url = url
                if i == 2:  # ean
                    ean = detail.find_element_by_tag_name("a").text
                    product.ean = ean

            if product.url and product.ean:
                self.inventory.products.append(product)
        return self.inventory

    def query_views(self, inventory: Inventory) -> Inventory:
        for idx, product in enumerate(inventory.products):
            if idx % 10 == 0:
                self.logger.info("Fetching product information from products {} to {}"
                                 .format(idx, idx + 10))
            try:
                self.browser.get(product.url)
                product.view = self.browser.find_element_by_class_name("prod") \
                    .find_element_by_tag_name("a").get_attribute("href")
                time.sleep(settings.TIMER_OP)
            except NoSuchElementException:
                self.logger.warning("Couldn't fetch product information for item: "
                                    "'{}'".format(product.ean))
        return self.inventory

    def query_products(self, inventory: Inventory) -> Inventory:
        for idx, product in enumerate(inventory.products):
            try:
                if idx % 10 == 0:
                    self.logger.info("Fetching other prices from products {} to {}"
                                     .format(idx, idx + 10))
                self.browser.get(product.view)
                product.name = self.browser \
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
            except Exception:
                self.logger.warning("Couldn't fetch other prices information for item: "
                                    "'{}'".format(product.ean))
        return self.inventory

    def change_products_price(self, changed: Changed):
        self.open_inventory(1)  # only needed to login, if input file is added
        for product in changed.products:
            try:
                self.__change_product_price(product)
            except Exception:
                self.logger.warning("Couldn't change price for item: '{}'"
                                    .format(product.ean))

    def __change_product_price(self, product: Market):
        self.browser.get(product.url)
        element_price = self.browser.find_element_by_id("shop_product_price")
        element_price.clear()
        element_price.send_keys(str(product.new_offer.price))
        time.sleep(settings.TIMER_OP)
        result = self.__submit_price_change(product)
        while not result:
            time.sleep(settings.TIMER_OP)
            result = self.__submit_price_change(product)

    def __submit_price_change(self, product: Market) -> bool:
        button = self.browser.find_element_by_id("shop_product_publish")
        button.click()

        element_alert = self.browser.find_element_by_class_name("alert")

        if "A atualização foi efetuada" in element_alert.text:
            self.logger.info("Changed price successfully for item: '{}' - "
                             "old price: '{}', new price: '{}'"
                             .format(product.ean, product.old_offer.price,
                                     product.new_offer.price))
            return True
        else:
            alert_text = element_alert.text
            self.logger.error("Couldn't change price for item '{}': '{}'. Retrying..."
                              .format(product.ean, alert_text.replace("\n", ". ")))
            return False
