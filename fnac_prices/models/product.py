from dataclasses import dataclass, field
from typing import List

from dataclasses_json import dataclass_json


@dataclass
class Offer:
    name: str
    price: float
    shipping: float


@dataclass
class Product:
    url: str
    view: str = field(default=None)
    name: str = field(default=None)
    offers: List[Offer] = field(default_factory=list)


@dataclass_json
@dataclass
class Inventory:
    products: List[Product] = field(default_factory=list)


@dataclass
class Match:
    url: str
    store_offer: Offer
    lowest_offer: Offer


@dataclass_json
@dataclass
class Renewed:
    products: List[Match] = field(default_factory=list)


@dataclass
class Market:
    url: str
    old_offer: Offer
    new_offer: Offer
    lowest_offer: Offer


@dataclass_json
@dataclass
class Changed:
    products: List[Market] = field(default_factory=list)
