import logging

from fnac_prices import settings
from fnac_prices.exceptions.fnac import FNACLoginException
from fnac_prices.selenium.fnac import FNACSelenium
from fnac_prices.utils import file
from fnac_prices.utils.helper import Helper


class ManagedApp:
    def __init__(self, email: str, password: str, input_path: str = None,
                 logger: logging.Logger = logging.getLogger("ManagedApp")):
        self.email = email
        self.password = password
        self.input_path = input_path
        self.logger = logger
        self.fnac = FNACSelenium(self.email, self.password)

    def __run_login(self):
        self.logger.info("Logging in...")
        try:
            self.fnac.make_login()
        except FNACLoginException:
            self.logger.error("Couldn't login at '{}'. Please check your credentials."
                              .format(settings.HOMEPAGE))
            exit()

    def __get_inventory(self):
        self.logger.info("Opening inventory...")
        self.fnac.open_inventory(1)
        total_prod = self.fnac.get_total_products()
        total_pages = Helper.get_number_of_pages(total_prod)
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
        renewed = Helper.build_prices_match(inventory)
        file.write_match_file(renewed)
        changed = Helper.build_lowest_prices(renewed)
        file.write_changed_file(changed)
        self.logger.info("Found a total of '{}' products to change"
                         .format(len(changed.products)))
        self.fnac.change_product_price(changed)

    def run(self):
        if self.input_path is None:
            self.logger.warning("Initializing ManagedApp without inventory file")
            self.__run_login()
            inventory = self.__get_inventory()
            file.write_inventory_file(inventory)
        else:
            self.logger.warning("Found an inventory file at '{}'".format(self.input_path))
            inventory = file.read_from_file(self.input_path)

        self.__change_prices(inventory)
