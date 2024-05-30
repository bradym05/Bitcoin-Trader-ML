# Dependencies
import time
import random
import threading

from typing import Dict, List
from dacite import from_dict
from machine_learning.feeds import HistoricalFeed
from main.services import SingletonBase
from main.types import *

# Declare custom tick service
class CustomTickService(SingletonBase):
    # Initialize object
    def __init__(self, feed=HistoricalFeed(), ticker_length:int=10) -> None:
        # Initialize variables
        self.feed = feed
        self.ticker_length = ticker_length
        self.ticks:Dict[str, List[TickerEvent]] = {}
        self.tick_sequence:List[Dict[str, any]] = []
        self._loop_started = False
    # Start ticker thread
    def run(self):
        tick_thread = threading.Thread(target=self._tick_loop, daemon=True)
        tick_thread.start()
    # Main tick loop
    def _tick_loop(self):
        # Make sure loop has not started
        if self._loop_started == False:
            # Begin loop
            self._loop_started = True
            while self._loop_started == True:
                # Get tick from feed
                ticker = from_dict(TickerEvent, self.feed.step())
                # Check if product is referenced
                product = ticker.product_id
                if not product in self.ticks:
                    self.ticks[product] = []
                # Reference tick
                self.ticks[product].append(ticker)
                # Check length
                if len(self.ticks[product]) > self.ticker_length:
                    self.ticks[product].pop(0)
                # Sleep for a random interval >= 0.2
                time.sleep(0.2 + random.random())
    # Get ticks from product id
    def get_ticks(self, product:str) -> List[TickerEvent]:
        if product in self.ticks:
            return self.ticks[product]
        else:
            return []