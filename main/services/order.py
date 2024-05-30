# Dependencies
import uuid
from main.types import *
from main.services import SingletonBase, RestClientService, PaperClientService, WebsocketService
from decimal import Decimal, ROUND_DOWN

# Declare order service
class OrderService(SingletonBase):
    # Initialize object
    def __init__(self, config:CurrencyPairConfig=CurrencyPairConfig(pair=CurrencyPair.BTC_USDC, precision=8), paper:bool=True) -> None:
        self.rest_client = PaperClientService.get_instance() if paper == True else RestClientService.get_instance()
        self.websocket = WebsocketService.get_instance()
        self.config = config
        self.paper = paper
    # Get most recent ticker price
    def get_price(self) -> str:
        ticks = self.websocket.get_ticks(self.config.pair.value)
        if len(ticks) > 0:
            return ticks[-1].price
    # Get unique id for orders
    def get_client_order_id(self) -> str:
        return str(uuid.uuid4())
    # Match currency precision
    def adjust_precision(self, amt, precision:int=4) -> str:
        return str(Decimal(amt).quantize(Decimal("1."+("0" * precision)), rounding=ROUND_DOWN))
    # Place buy order
    def buy(self, size:str, price:str) -> str | None:
        # Get most recent tick
        ticks = self.websocket.get_ticks(self.config.pair.value)
        if len(ticks) > 0:
            last_tick = ticks[-1]
            best_ask = last_tick.best_ask
            # Validate asking price
            if Decimal(price) >= Decimal(best_ask):
                # Adjust price to match best ask
                print(f"Buy price at or above best ask {best_ask} at {price}")
                price = str(Decimal(best_ask) - Decimal("0.0001"))
            # Initialize variables
            order_id = self.get_client_order_id()
            size = self.adjust_precision(size, self.config.precision)
            price = self.adjust_precision(price)
            # Get server response
            response = self.rest_client.limit_order_gtc_buy(
                client_order_id=order_id,
                product_id=self.config.pair.value + "C",
                base_size=size,
                limit_price=price,
            )
            print(response)
            # Validate response
            if 'success' in response and response['success'] == True:
                order_id = response['order_id']
                return order_id
            else:
                return None
        else:
            print("No Available Ticks")
    # Place sell order
    def sell(self, size:str, price:str) -> str | None:
        # Get most recent tick
        ticks = self.websocket.get_ticks(self.config.pair.value)
        if len(ticks) > 0:
            last_tick = ticks[-1]
            best_bid = last_tick.best_bid
            # Validate bid price
            if Decimal(price) <= Decimal(best_bid):
                # Adjust price to match best bid
                print(f"Sell price at or below best bid {best_bid} at {price}")
                price = str(Decimal(best_bid) + Decimal("0.0001"))
            # Initialize variables
            order_id = self.get_client_order_id()
            size = self.adjust_precision(size, self.config.precision)
            price = self.adjust_precision(price)
            # Get server response
            response = self.rest_client.limit_order_gtc_sell(
                client_order_id=order_id,
                product_id=self.config.pair.value + "C",
                base_size=size,
                limit_price=price,
            )
            # Validate response
            if 'success' in response and response['success'] == True:
                order_id = response['order_id']
                return order_id
            else:
                return None
        else:
            print("No Available Ticks")
