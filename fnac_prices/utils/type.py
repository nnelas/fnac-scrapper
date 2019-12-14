# Custom types for type hinting
from typing import TypeVar

AnyPath = TypeVar("AnyPath", bytes, str)
