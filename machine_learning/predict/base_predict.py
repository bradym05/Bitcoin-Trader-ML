# Dependencies
import pandas as pd
import numpy as np
import pandas_ta as ta
import math
import threading

from typing import Dict
from neuralforecast import NeuralForecast

# Declare base predict class
class BasePredict:
    # Initialize predict
    # n_ticks: number of ticks to track (must be divisible by ta_length)
    # ta_length: length of each ta step
    def __init__(self, ta_length:int=10):
        # Initialize variables
        self.data = []
        self.index = []
        self.ticks = []
        self.data_length = 0
        self.ta_length = ta_length
        self.nf = NeuralForecast.load(path='machine_learning\\training\\saved\\Autoformer_V8\\')
    # Input ticker event
    def on_tick(self, tick_row:pd.DataFrame):
        # Convert to float
        tick_row = tick_row.astype('float64')
        # Append to tick array
        self.ticks.append(tick_row)
        # Validate tick array length
        if len(self.ticks) > self.ta_length * 2:
            # Remove oldest tick
            self.ticks.pop(0)
            # Create dataframe of past ticks
            indicator_df = pd.concat(objs=self.ticks)
            # Get indicators
            indicators ={
                'bb':indicator_df.ta.bbands(length=self.ta_length).tail(n=self.ta_length),
                'ema':indicator_df.ta.ema(length=self.ta_length).tail(n=self.ta_length),
                'wma':indicator_df.ta.wma(length=self.ta_length).tail(n=self.ta_length),
                'sma':indicator_df.ta.sma(length=self.ta_length).tail(n=self.ta_length)
            }
            # Update index
            current_index = self.data_length + 1
            self.data_length = current_index
            # Process
            process_thread = threading.Thread(daemon=True, target=self.process, args=[tick_row, indicators, current_index])
            process_thread.start()
    # Process ticks + indicators
    def process(self, tick_row:pd.DataFrame, indicators:Dict[str, pd.Series], current_index:int):
        # Initialize list of features
        features = {}
        date = tick_row.index.item()
        # Iterate over tick features
        for column in tick_row.columns:
            features[column] = tick_row[column].item()
        # Iterate over indicators
        for key, iseries in indicators.items():
            for i, val in enumerate(iseries):
                if type(val) == float:
                    features[key + str(i)] = float(val)
        # Update data
        self.data.insert(current_index, features)
        self.index.insert(current_index, date)
    # Get entire dataframe
    def get_dataframe(self) -> pd.DataFrame:
        # Create unique index column
        data_length = self.data_length
        unique_ids = pd.RangeIndex(data_length).to_series()
        # Create dataframe from snapshot
        target_key = 'close_price' if 'close_price' in self.data[0] else 'price'
        df = pd.DataFrame(data=self.data[:data_length], copy=True).rename(columns={'close_price':'y'})
        # Insert required columns
        df.insert(0, 'ds', pd.DatetimeIndex(self.index[:data_length], copy=True))
        df.insert(0, 'unique_id', unique_ids.map(lambda x: 0))
        # Format dates
        df['ds'] = pd.to_datetime(df['ds'])
        # Return final dataframe
        return df
    # Make prediction and reset data
    def predict(self) -> pd.DataFrame:
        # Get dataframe
        df = self.get_dataframe()
        # Reset data
        self.data.clear()
        self.index.clear()
        self.data_length = 0
        # Make prediction
        prediction_df = self.nf.predict(df=df).reset_index()
        # Return result
        return prediction_df