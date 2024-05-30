# Dependencies
from dataclasses import dataclass

@dataclass
class FeatureMap:
    date:str
    open_price:str
    close_price:str
    high:str
    low:str
    btc_vol:str
    usdc_vol:str