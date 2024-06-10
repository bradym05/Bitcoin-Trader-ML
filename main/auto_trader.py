# Dependencies
import time
import threading
import pandas as pd
import pandas_ta as ta

from typing import List
from main import TradeHandler
from machine_learning.predict import LivePredict

# Declare auto trader class
class AutoTrader():
    # Initialize object
    def __init__(self, paper:bool=True, n_predictions:int=5):
        # Initialize variables
        self.trader = TradeHandler(paper=paper, custom_tick=False)
        self.predict = LivePredict()
        self.predictions = []
        self.decisions = []
        self.real = []
        self.n_predictions = n_predictions
        self._running = False
        # Set tick callback
        self.trader.websocket.set_event_callback(self.predict.on_tick)
        # Begin main loop
        loop_thread = threading.Thread(target=self._loop, daemon=True)
        loop_thread.start()
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
