# Dependencies
import pandas as pd
import numpy as np
import pandas_ta as ta
import math
import threading

from typing import Dict
from neuralforecast import NeuralForecast

# SETTINGS
BTC_SCALE = 71000
DECISION_TRANSLATIONS = {'-0.8': '-1', '-0.9': '-1', '-0.7': '-1', '-1.0': '-1', '-1.1': '-1', '-1.2': '-1', '-0.5': '-1', '-0.6': '-1', '-0.4': '-1', '-1.3': '-1', '-1.5': '-1', '-1.4': '-1', '0.1': '0', '0.0': '0', '-0.0': '0', '-0.1': '0', '0.2': '0', '-0.2': '0', '-0.3': '0', '0.3': '0', '-9.0': '0', '7.2': '0', '2.6': '0', '-7.9': '0', '0.4': '1', '0.8': '1', '1.3': '1', '1.4': '1', '1.2': '1', '1.1': '1', '1.0': '1', '0.6': '1', '0.5': '1', '0.9': '1', '0.7': '1', '1.5': '1', '-6.9': '1'}

# Initialize constant variables
prediction_columns = {}
for pred_num in range(12):
    prediction_columns[pred_num] = 'p'+str(pred_num+1)

# Declare base predict class
class BasePredict:
    # Initialize predict
    # ta_length: length of each ta step
    def __init__(self, ta_length:int=10):
        # Initialize variables
        self.data = []
        self.predictions = []
        self.decisions = []
        self.raw_decisions = []
        self.index = []
        self.ticks = []
        self.data_length = 0
        self.ta_length = ta_length
        self.autoformer_5min = NeuralForecast.load(path='machine_learning\\training\\saved\\Autoformer_5M\\')
        self.decision_autoformer = NeuralForecast.load(path='machine_learning\\training\\saved\\DecisionAutoformer')
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
    # Translate raw decision float into int decision (-1, 0, or 1)
    def translate_decision(self, raw_decision) -> int:
        # Truncate decision
        truncated = str(math.fabs(raw_decision))[:3]
        truncated = str(math.copysign(float(truncated), raw_decision))
        # Check for direct match
        if truncated in DECISION_TRANSLATIONS:
            return int(DECISION_TRANSLATIONS[truncated])
        else:
            # Initialize dist variables
            closest_dist, closest_val = math.inf, ''
            # Iterate over all translations
            for other_val, translation in DECISION_TRANSLATIONS.items():
                # Calculate magnitude
                magnitude = float(truncated) - float(other_val)
                magnitude = math.fabs(magnitude)
                # Compare with closest
                if magnitude < closest_dist:
                    # Update closest
                    closest_dist = magnitude
                    closest_val = other_val
            # Return result
            return int(DECISION_TRANSLATIONS[closest_val])
    # Make prediction and reset data
    def predict(self) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
        # Get dataframe
        df = self.get_dataframe()
        # Reset data
        self.data.clear()
        self.index.clear()
        self.data_length = 0
        # Make price predictions
        prediction_5min = self.autoformer_5min.predict(df=df).reset_index()
        # Rescale predicted prices
        rescaled_predictions = prediction_5min.copy()
        rescaled_predictions["Autoformer"] /= BTC_SCALE
        # Rescale dataframe
        scaled_df = df.copy()
        for col in scaled_df:
            if col != 'ds' and col != 'unique_id':
                scaled_df[col] /= BTC_SCALE
        # Create series of previous decisions
        decision_list = self.decisions.copy()
        decision_list.reverse()
        decision_list = decision_list[:len(scaled_df.index)]
        decision_list = pd.Series(data=decision_list).reindex(index=scaled_df.index.copy())
        decision_list = decision_list.fillna(0)
        # Swap y column
        scaled_df = scaled_df.rename(columns={"y":"close_price"})
        scaled_df.insert(0, 'y', decision_list)
        # Create decision dataframe
        decision_df = pd.DataFrame(data=[rescaled_predictions.get("Autoformer").array]).T.rename(columns=prediction_columns)
        decision_df = decision_df.reindex(index=scaled_df.index.copy())
        decision_df = decision_df.bfill().interpolate('linear')
        decision_df = decision_df.join(scaled_df)
        # Get raw decision prediction
        autoformer_decision = self.decision_autoformer.predict(df=decision_df).reset_index()
        raw_decision = autoformer_decision.get("Autoformer").item()
        # Translate decision
        int_decision = self.translate_decision(raw_decision=raw_decision)
        # Append results
        self.raw_decisions.append(raw_decision)
        self.decisions.append(int_decision)
        self.predictions.append(prediction_5min)
        # Return results
        return int_decision, prediction_5min, df