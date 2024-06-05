# Dependencies
import time
import random
import threading

from tqdm import tqdm
from typing import Dict, List
from dacite import from_dict
from machine_learning.feeds import HistoricalFeed
from main.services import SingletonBase
from main.types import *

# Declare custom tick service
class CustomTickService(SingletonBase):
    # Initialize object
    def __init__(self, feed=HistoricalFeed(), ticker_length:int=10, no_wait:bool=False) -> None:
        # Initialize variables
        self.feed = feed
        self.ticker_length = ticker_length
        self.ticks:Dict[str, List[TickerEvent]] = {}
        self.tick_sequence:List[Dict[str, any]] = []
        self._loop_started = False
        self.no_wait = no_wait
    # Start ticker thread
    def run(self):
        tick_thread = threading.Thread(target=self._tick_loop, daemon=True)
        tick_thread.start()
    # Set optional callback to receive tick rows as pandas dataframe
    def set_row_callback(self, callback:callable):
        self._row_callback = callback
    # Main tick loop
    def _tick_loop(self):
        # Make sure loop has not started
        if self._loop_started == False:
            # Begin loop
            self._loop_started = True
            while self._loop_started == True:
                # Get tick from feed
                index = self.feed.index
                ticker, row = self.feed.step()
                ticker = from_dict(TickerEvent, ticker)
                # Check if product is referenced
                product = ticker.product_id
                if not product in self.ticks:
                    self.ticks[product] = []
                # Reference tick
                self.ticks[product].insert(index, ticker)
                # Check length
                if len(self.ticks[product]) > self.ticker_length:
                    self.ticks[product].pop(0)
                # Check for row callback
                if getattr(self, "_row_callback", None):
                    self._row_callback(row)
                # Check if waiting is expected
                if self.no_wait == False:
                    # Sleep for a random interval >= 0.05
                    time.sleep(0.05 + (random.random()/2))
                elif self.feed.index == 0:
                    # Stop loop (when using for preprocessing w/ no wait)
                    self._loop_started = 0
                    break
                else:
                    continue
    # Get ticks from product id
    def get_ticks(self, product:str) -> List[TickerEvent]:
        if product in self.ticks:
            return self.ticks[product]
        else:
            return []