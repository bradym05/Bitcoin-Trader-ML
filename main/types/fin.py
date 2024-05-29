# Dependencies
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from main.types import *

class CurrencyPair(Enum):
    BTC_USDC = "BTC-USD"

@dataclass
class CurrencyPairConfig:
    pair: CurrencyPair
    precision: int