from fnac_prices import settings
from fnac_prices.models.product import Inventory, Renewed, Changed


def write_inventory_file(inventory: Inventory):
    with open(settings.INVENTORY_FILE, "w", encoding=settings.DEFAULT_ENCODING) as f:
        f.write(inventory.to_json())


def write_match_file(renewed: Renewed):
    with open(settings.MATCH_FILE, "w", encoding=settings.DEFAULT_ENCODING) as f:
        f.write(renewed.to_json())


def write_changed_file(changed: Changed):
    with open(settings.CHANGED_FILE, "w", encoding=settings.DEFAULT_ENCODING) as f:
        f.write(changed.to_json())


def read_from_file(path: str) -> Inventory:
    with open(path, "r", encoding=settings.DEFAULT_ENCODING) as f:
        return Inventory.from_json(f.read())
