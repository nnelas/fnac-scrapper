import math

from fnac_prices import settings
from fnac_prices.models.product import Inventory, Renewed, Match, Changed, Market, Offer


class Helper:
    @staticmethod
    def get_number_of_pages(num_products: int) -> int:
        return math.ceil(num_products/settings.PRODUCTS)

    @staticmethod
    def build_prices_match(inventory: Inventory) -> Renewed:
        renewed = Renewed()
        for product in inventory.products:
            max_price, max_shipping = settings.MAX_OFFER, settings.MAX_OFFER
            for offer in product.offers:
                if offer.name == settings.STORE:
                    store_offer = offer

                if (offer.price + offer.shipping) < (max_price + max_shipping):
                    max_price = offer.price
                    max_shipping = offer.shipping
                    lowest_offer = offer

            renewed.products.append(Match(
                url=product.url,
                ean=product.ean,
                store_offer=store_offer,
                lowest_offer=lowest_offer
            ))
        return renewed

    @staticmethod
    def build_lowest_prices(renewed: Renewed) -> Changed:
        changed = Changed()
        for product in renewed.products:
            if product.store_offer.name != product.lowest_offer.name:
                new_price = product.store_offer.price
                while (new_price + product.store_offer.shipping) > \
                        (product.lowest_offer.price + product.lowest_offer.shipping):
                    new_price -= settings.DECREASE_BY

                market = Market(url=product.url,
                                ean=product.ean,
                                old_offer=product.store_offer,
                                new_offer=Offer(product.store_offer.name,
                                                (math.floor(new_price*100)/100),
                                                product.store_offer.shipping),
                                lowest_offer=product.lowest_offer)
                changed.products.append(market)
        return changed
