# Dependencies
import json
import threading

from typing import Dict, List
from dacite import from_dict
from coinbase.websocket import WSClient, WSClientConnectionClosedException, WSClientException
from main.private import key_file_path
from main.services import SingletonBase
from main.types import *

# SETTINGS
PRODUCT_IDS = ["BTC-USD"]
CHANNELS = ["ticker", "heartbeats"]

# Declare websocket service
class WebsocketService(SingletonBase):
    # Initialize object
    def __init__(self, ticker_length:int=10) -> None:
        # Initialize websocket
        self.ws = WSClient(key_file=key_file_path, on_message=self.on_message)
        # Initialize variables
        self.ticker_length = ticker_length
        self.ticks:Dict[str, List[TickerEvent]] = {}
    # Start connection thread
    def run(self):
        ws_thread = threading.Thread(target=self._connect, daemon=True)
        ws_thread.start()
    # Set optional callback to receive websocket events
    def set_event_callback(self, callback:callable):
        self._event_callback = callback
    # Connect to websocket
    def _connect(self):
        print("Websocket Connecting")
        # Except errors
        try:
            # Open websocket connection and subscribe
            self.ws.open()
            self.ws.subscribe(product_ids=PRODUCT_IDS, channels=CHANNELS)
            print("Websocket Connected")
            # Catch exceptions
            self.ws.run_forever_with_exception_check()
        except WSClientConnectionClosedException as e:
            # Handle client closed
            print(f"Client connection closed! Reconnecting in {RECONNECT_SLEEP_TIME}s")
            time.sleep(RECONNECT_SLEEP_TIME)
            self._connect()
        except WSClientException as e:
            print("Error encountered!")
        finally:
            self.ws.close()
    # Callback on websocket message
    def on_message(self, msg:str):
        # Load from JSON
        data = json.loads(msg)
        # Ignore heartbeat ticks
        if data["channel"] == "heartbeats":
            return
        # Format as websocket message
        data = from_dict(WebsocketMessage, data)
        # Iterate over ticker data
        for ticker in data.events[0].tickers or []:
            # Get product
            product = ticker.product_id
            # Check if product is referenced
            if not product in self.ticks:
                self.ticks[product] = []
            # Update ticks
            self.ticks[product].append(ticker)
            # Maintain length
            if len(self.ticks[product]) > self.ticker_length:
                self.ticks[product].pop(0)
            # Check for event callback
            if getattr(self, "_event_callback", None):
                self._event_callback(ticker.__dict__)
    # Get ticks from product id
    def get_ticks(self, product:str) -> List[TickerEvent]:
        if product in self.ticks:
            return self.ticks[product]
        else:
            return []