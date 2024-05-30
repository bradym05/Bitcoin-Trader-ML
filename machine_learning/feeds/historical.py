# Dependencies
import pandas as pd
import pandas_ta as pdta
import datetime

from machine_learning.types import FeatureMap

# Declare historical feed class
class HistoricalFeed:
    # Initialize object
    def __init__(
        self, 
        csv_file:str="machine_learning\\data\\Binance_BTCUSDT_1h.csv",
        key_map:FeatureMap=FeatureMap(
            date="Date",
            open_price="Open",
            close_price="Close",
            high="High",
            low="Low",
            btc_vol="Volume BTC",
            usdc_vol="Volume USDT"
        )
        ) -> None:
        # Attempt to read given file
        try:
            with open(csv_file, 'r') as f:
                # Initialize variables
                data = []
                dates = []
                # Iterate over each row
                for row in f:
                    # Seperate by commas
                    seperated = row[:-1].split(',')
                    # Append date, and other data
                    data.append(seperated[1:])
                    dates.append(seperated[0])
                # Convert dates to index
                dates = pd.DatetimeIndex(dates[1:])
                # Create dataframe
                self.df = pd.DataFrame(data=data[1:], index=dates, columns=data[0])
        except FileNotFoundError:
            print(f'File at path "{csv_file}" not found')
            return
        # Flip key map
        self.key_map = {}
        for feature_key, df_key in key_map.__dict__.items():
            self.key_map[str(df_key)] = str(feature_key)
        # Match data columns to expected features
        self.df.rename(columns=self.key_map, inplace=True)
        # Remove unused columns
        for column in self.df.columns:
            if not column in key_map.__dict__:
                self.df.pop(column)
        # Sort from oldest to newest date
        self.df.sort_index(inplace=True, ascending=True)
        # Initialize variables
        self.max_index = len(self.df)
        self.index = 24 # Start at 24 hours
    # Step forward and get current data
    def step(self) -> pd.DataFrame:
        # Get row at current index time
        row = self.df.loc[[self.df.index[self.index]]]
        # Get row from 24 hours back
        yesterday_row = self.df.loc[[self.df.index[self.index - 24]]]
        # Calculate values
        price_float = float(row['close_price'].item())
        price_change_24_h = (price_float - float(yesterday_row['close_price'].item()))/price_float
        volume_24_h = float(row['btc_vol'].item()) + float(yesterday_row['btc_vol'].item())
        high_24_h = max(float(row['high'].item()), float(yesterday_row['high'].item()))
        low_24_h = min(float(row['low'].item()), float(yesterday_row['low'].item()))
        # Create ticker event dict
        ticker_event = {
            'type':"ticker",
            'product_id':"BTC-USD",
            'price':row["close_price"].item(),
            'price_percent_chg_24_h':str(price_change_24_h),
            'volume_24_h':str(volume_24_h),
            'high_24_h':str(high_24_h),
            'low_24_h':str(low_24_h),
            'best_bid':row['high'].item(),
            'best_ask':row['low'].item(),
            'low_52_w':"",
            'high_52_w':"",
            'best_bid_quantity':"",
            'best_ask_quantity':""
        }
        # Update index
        self.index += 1
        # Check index bounds
        if self.index > self.max_index:
            self.index = 0
        # Return obtained data row
        return ticker_event