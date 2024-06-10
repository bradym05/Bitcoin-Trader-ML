# Dependencies
import time
import threading
import pandas as pd
import pandas_ta as ta

from typing import List
from main import TradeHandler
from machine_learning.predict import LivePredict

# SETTINGS
SAVE_KEYS = ["bought_orders"]
SAVE_NAME = "AUTO"

# Declare auto trader class
class AutoTrader():
    # Initialize object
    def __init__(self, paper:bool=True, n_predictions:int=5, usd_budget:float=10.0):
        # Initialize variables
        self.trader = TradeHandler(paper=paper, custom_tick=False)
        self.predict = LivePredict()
        self.bought_orders = []
        self.predictions = []
        self.decisions = []
        self.real = []
        self.n_predictions = n_predictions
        self.usd_budget = usd_budget
        self._running = False
        # Load saved values
        self.trader.save_service.load_into(SAVE_KEYS, SAVE_NAME, self)
        # Set tick callback
        self.trader.websocket.set_event_callback(self.predict.on_tick)
        # Begin main loop
        loop_thread = threading.Thread(target=self._loop, daemon=True)
        loop_thread.start()
    # Save data w/ save service
    def save(self):
        self.save_service.save_from(SAVE_KEYS, SAVE_NAME, self)
    # Callback on predict decision
    def on_decision(self, decision:int):
        # Check decision
        if decision == 0:
            # Do nothing
            return
        else:
            # Get most recent ticker price
            price = float(self.trader.order_service.get_price())
            # Check if buying or selling
            if decision == 1:
                # Calculate size from budget
                size = self.usd_budget/price
                # Make trade
                order_id = self.trader.buy(size=size, price=price)
                # Validate purchase
                if order_id != '':
                    self.bought_orders.append(order_id)
            else:
                # Check for purchased orders
                if len(self.bought_orders) > 0:
                    # Get oldest purchase
                    oldest_purchase = self.bought_orders.pop(0)
                    # Sell oldest purchase
                    order_id = self.trader.sell(bought_order_id=oldest_purchase, price=price)
                    # Validate sale
                    if order_id == '':
                        # Reinsert order due to failed trade
                        self.bought_orders.insert(0, order_id)
            # Autosave
            self.save()
    # Main loop method
    def _loop(self):
        # Check if running
        if self._running == False:
            # Update
            self._running = True
            # Begin loop
            while self._running == True:
                # Check data length
                if self.predict.data_length >= 20:
                    # Allow time for more data to be processed
                    time.sleep(5)
                    # Get predictions
                    decision, prediction_5min, real_df = self.predict.predict()
                    # Decision callback
                    self.on_decision(decision)
                    # Update prediction lists
                    self.predictions.append(prediction_5min)
                    self.decisions.append(decision)
                    self.real.append(real_df)
                    # Check length
                    if len(self.predictions) > self.n_predictions:
                        # Remove oldest prediction
                        self.predictions.pop(0)
                        self.decisions.pop(0)
                        self.real.pop(0)
            time.sleep(0.5)
