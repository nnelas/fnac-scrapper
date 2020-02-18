from fnac_prices.classes.fnac_error_mapper import FnacErrorEntity, FnacErrorCodes


class FnacErrorHandler:
    def __init__(self, browser):
        self.browser = browser

    def __handle_invalid_discount(self) -> bool:
        # keeping this because error handling for invalid
        # discount may change on FNAC implementation
        return True

    def __handle_invalid_basket(self) -> bool:
        element_basket = self.browser.find_element_by_id(
            "shop_product_shop_product_promotions_0_trigger_cart_value")
        element_basket.clear()
        return True

    def run_error_recovery(self, fnac_error: FnacErrorEntity) -> bool:
        if fnac_error.code == FnacErrorCodes.UNKNOWN_ERROR:
            return True
        elif fnac_error.code == FnacErrorCodes.DISCOUNT_ERROR:
            return self.__handle_invalid_discount()
        elif fnac_error.code == FnacErrorCodes.BASKET_ERROR:
            return self.__handle_invalid_basket()
