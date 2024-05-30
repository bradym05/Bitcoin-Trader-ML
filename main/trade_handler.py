# Dependencies
import threading
import time

from typing import Optional, List, Dict
from dacite import from_dict
from main.private import portfolio_uuid
from main.services import SaveService, RestClientService, PaperClientService, WebsocketService, CustomTickService, OrderService
from main.types import *

# SETTINGS
ORDER_UPDATE_INTERVAL = 0.5
SAVE_KEYS = ["orders", "inventory", "sold_from"]
SAVE_NAME = "MAIN"

# Declare trade handler class
class TradeHandler():
    # Initialize handler
    def __init__(
        self, 
        save_version:str="0", 
        save_path:Optional[str]=None,
        paper:bool=True,
        custom_tick:bool=False
        ):
        # Initialize services
        self.rest_client = PaperClientService.get_instance() if paper == True else RestClientService.get_instance()
        self.websocket = CustomTickService.get_instance() if custom_tick == True else WebsocketService.get_instance()
        self.order_service = OrderService.get_instance(paper=paper)
        self.save_service = SaveService.get_instance(version=save_version, path=save_path)
        self.uuid = portfolio_uuid
        self._watch = {}
        self.orders:Dict[str, Dict[str, Order]] = {"BUY":{}, "SELL":{}}
        self.sold_from:Dict[str, Order] = {}
        self.inventory:List[Order] = []
        # Load saved values
        self.save_service.load_into(SAVE_KEYS, SAVE_NAME, self)
        self.reconcile_loaded()
        # Connect websocket
        self.websocket.run()
    # Save data w/ save service
    def save(self):
        self.save_service.save_from(SAVE_KEYS, SAVE_NAME, self)
    # Track loaded orders
    def reconcile_loaded(self):
        for side, order_dict in self.orders.items():
            for order_id, order in order_dict.items():
                # Create thread to watch order status
                watch_thread = threading.Thread(target=self.watch_order, daemon=True, args=[order_id, side])
                # Refererence thread
                self._watch[order_id] = watch_thread
                # Start thread
                watch_thread.start()
    # Get portfolio breakdown
    def portfolio_breakdown(self) -> PortfolioBreakdown:
        return from_dict(
            data_class=PortfolioBreakdown,
            data=self.rest_client.get_portfolio_breakdown(self.uuid),
        )
    # Callback on order finished
    def order_finished(self, order:Order):
        # Remove referenced thread
        self._watch.pop(order.order_id, None)
        # Initialize variables
        order_side = OrderSide(order.side)
        # Check order side
        if order_side == OrderSide.BUY:
            # Check fill amount
            if float(order.filled_size) > 0:
                # Add to inventory
                self.inventory.append(order)
        elif order_side == OrderSide.SELL and float(order.filled_size) > 0:
            # Initialize variables
            filled_size = float(order.filled_size)
            base_size = float(order.order_configuration.limit_limit_gtc.base_size)
            sold_order:Order = self.sold_from.pop(order.order_id)
            # Check fill amount
            if filled_size < base_size:
                # Update bought order
                remainder = base_size - filled_size
                sold_order.filled_size = remainder
                # Add back to inventory
                self.inventory.append(sold_order)
        else:
            return
        # Remove from active orders
        self.orders[order.side].pop(order.order_id)
        # Autosave
        self.save()
    # Update order status
    def watch_order(self, order_id:str, side:str):
        finished = False
        while finished == False:
            try:
                # Get order from rest client
                response = self.rest_client.get_order(order_id=order_id)
                # Validate response
                if 'order' in response:
                    # Convert to order class
                    order:Order = from_dict(Order, response['order'])
                    order_status = OrderStatus(order.status)
                    self.orders[side][order_id] = order
                    # Check if order is pending/open
                    if order_status != OrderStatus.OPEN and order_status != OrderStatus.PENDING:
                        # Call order finished callback
                        finished = True
                        self.order_finished(order)
                    else:
                        # Autosave
                        self.save()
            except:
                pass
            finally:
                time.sleep(ORDER_UPDATE_INTERVAL)
    # Place buy order
    def buy(self, size:float, price:float) -> None:
        # Get order id
        order_id = self.order_service.buy(size=str(size), price=str(price))
        # Check status
        if order_id != None:
            # Create thread to watch order status
            watch_thread = threading.Thread(target=self.watch_order, daemon=True, args=[order_id, "BUY"])
            # Refererence thread
            self._watch[order_id] = watch_thread
            # Start thread
            watch_thread.start()
    # Sell purchased order
    def sell(self, bought_order_id:Optional[str]=None, price:Optional[float]=None) -> None:
        # Initialize variables
        bought_order = None
        # Check if given a order id
        if bought_order_id == None:
            # Check inventory length
            if len(self.inventory) > 0:
                bought_order:Order = self.inventory.pop(0)
                bought_order_id = bought_order.order_id
            else:
                print("Inventory Is Empty")
                return
        else:
            # Iterate over inventory
            for i, order in enumerate(self.inventory):
                if order.order_id == bought_order_id:
                    bought_order:Order = self.inventory.pop(i)
                    break
            if bought_order == None:
                print(f"Order {bought_order_id} Not Found")
                return
        # Check if given a price
        if price == None:
            # Get last tick
            ticks = self.websocket.get_ticks(self.order_service.config.pair.value)
            if len(ticks) > 0:
                last_tick:TickerEvent = ticks[-1]
                price = last_tick.price
            else:
                print("No Available Ticks")
                self.inventory.append(bought_order)
                return
        # Get sell order id
        sell_order_id = self.order_service.sell(size=bought_order.filled_size, price=str(price))
        # Check status
        if sell_order_id != None:
            # Reference where order was sold from
            self.sold_from[sell_order_id] = bought_order
            # Create thread to watch order status
            watch_thread = threading.Thread(target=self.watch_order, daemon=True, args=[sell_order_id, "SELL"])
            # Refererence thread
            self._watch[sell_order_id] = watch_thread
            # Start thread
            watch_thread.start()
        else:
            self.inventory.append(bought_order)