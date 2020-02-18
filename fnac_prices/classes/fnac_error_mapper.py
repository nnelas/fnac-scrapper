from dataclasses import dataclass, field
from enum import Enum

import re


class FnacErrorCodes(Enum):
    DISCOUNT_ERROR = 1
    BASKET_ERROR = 2
    UNKNOWN_ERROR = -1001


@dataclass
class FnacErrorEntity:
    code: Enum
    message: str = field(default=None)


class FnacErrorMapper:
    def __init__(self):
        pass

    def __is_invalid_discount_error(self, error: str) -> FnacErrorEntity:
        match = re.search(r"desconto inválido", error)
        if match:
            return FnacErrorEntity(code=FnacErrorCodes.DISCOUNT_ERROR)

    def __is_invalid_basket_error(self, error: str) -> FnacErrorEntity:
        match = re.search(r"basket inválido", error)
        if match:
            return FnacErrorEntity(code=FnacErrorCodes.BASKET_ERROR)

    def map(self, error: str) -> FnacErrorEntity:
        mapped_error = self.__is_invalid_discount_error(error) or \
                       self.__is_invalid_basket_error(error)

        if not mapped_error:
            mapped_error = FnacErrorEntity(
                code=FnacErrorCodes.UNKNOWN_ERROR,
                message="For an unknown reason, can't change product price.",
            )

        return mapped_error
