# Dependencies
from . import BasePredict
from typing import Dict
from datetime import datetime

import pandas as pd

# Declare live predict class
class LivePredict(BasePredict):
    # Initialize object
    def __init__(self, *args, **kwargs):
        # Initialize from base class
        super(LivePredict, self).__init__(*args, **kwargs)
    # Input ticker event
    def on_tick(self, tick:Dict):
        # Convert to pandas dataframe
        index = datetime.today()
        # Ensure all values can be converted to float type
        valid_tick = {}
        for key, val in tick.items():
            try:
                float_val = float(val)
                valid_tick[key] = [val]
            except ValueError:
                continue
        valid_tick['close_price'] = valid_tick['price']
        tick_row = pd.DataFrame(data=valid_tick, index=pd.DatetimeIndex([index]))
        # Call base method
        return BasePredict.on_tick(self, tick_row=tick_row)