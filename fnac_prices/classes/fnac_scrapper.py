import logging

from fnac_prices import settings
from fnac_prices.exceptions.fnac_exceptions import FnacLoginException
from fnac_prices.selenium.fnac_selenium import FnacSelenium
from fnac_prices.utils import file
from fnac_prices.utils.fnac_helper import FnacHelper


class FnacScrapper:
    def __init__(self, email: str, password: str, fnac_selenium: FnacSelenium, fnac_helper: FnacHelper,
                 input_path: str = None, logger: logging.Logger = logging.getLogger("ManagedApp")):
        self.email = email
        self.password = password
        self.input_path = input_path
        self.logger = logger
        self.fnac = fnac_selenium
        self.helper = fnac_helper

    def __run_login(self, email: str, password: str):
        self.logger.info("Logging in...")
        try:
            self.fnac.make_login(email, password)
        except FnacLoginException:
            self.logger.error("Couldn't login at '{}'. Please check your credentials."
                              .format(settings.HOMEPAGE))
            exit()

    def __get_inventory(self):
        self.logger.info("Opening inventory...")
        self.fnac.open_inventory(1)
        total_prod = self.fnac.get_total_products()
        total_pages = self.helper.get_number_of_pages(total_prod)
        self.logger.info("Found a total of '{}' products".format(total_prod))

        for index in range(1, total_pages):
            self.logger.info("Opening inventory - page {} of {}"
                             .format(index, total_pages))
            self.fnac.open_inventory(index)
            self.logger.info("Getting initial URLs...")
            inventory = self.fnac.query_inventory()
        self.logger.info("Getting views URLs...")
        inventory = self.fnac.query_views(inventory)
        self.logger.info("Querying products...")
        return self.fnac.query_products(inventory)

    def __change_prices(self, inventory):
        self.logger.info("Searching for lower prices...")
        renewed = self.helper.build_prices_match(inventory)
        file.write_match_file(renewed)
        changed = self.helper.build_lowest_prices(renewed)
        file.write_changed_file(changed)
        self.logger.info("Found a total of '{}' products to change"
                         .format(len(changed.products)))
        self.fnac.change_products_price(changed)

    def run(self):
        self.__run_login(self.email, self.password)
        file.create_directory(settings.LOGS_DIR)    # create if not exists
        if self.input_path is None:
            self.logger.warning("Initializing ManagedApp without inventory file")
            inventory = self.__get_inventory()
            file.write_inventory_file(inventory)
        else:
            self.logger.warning("Found an inventory file at '{}'".format(self.input_path))
            inventory = file.read_from_file(self.input_path)

        self.__change_prices(inventory)
