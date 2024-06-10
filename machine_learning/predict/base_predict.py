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
DECISION_TRANSLATIONS = {'-0.88': '-1', '-0.9': '-1', '-0.89': '-1', '-0.94': '-1', '-0.99': '-1', '-0.84': '-1', '-0.83': '-1', '-0.8': '-1', '-0.87': '-1', '-0.82': '-1', '-0.79': '-1', '-0.75': '-1', '-0.77': '-1', '0.00033': '-1', '-1.0': '-1', '-0.86': '-1', '-0.96': '-1', '-0.91': '-1', '-0.93': '-1', '-0.97': '-1', '-0.98': '-1', '-0.92': '-1', '-0.95': '-1', '-0.73': '-1', '-0.71': '-1', '-0.85': '-1', '-0.81': '-1', '-0.74': '-1', '-0.58': '-1', '-0.62': '-1', '-0.63': '-1', '-0.59': '-1', '-0.56': '-1', '-0.5': '-1', '-0.69': '-1', '-0.55': '-1', '-0.7': '-1', '-0.78': '-1', '-0.72': '-1', '-0.65': '-1', '-0.61': '-1', '-0.45': '-1', '-0.67': '-1', '-0.6': '-1', '-0.43': '-1', '-0.76': '-1', '-0.68': '-1', '-0.57': '-1', '-0.53': '-1', '-0.46': '-1', '-0.52': '-1', '-0.54': '-1', '-0.32': '0', '-0.37': '-1', '-0.41': '0', '-0.39': '-1', '-0.51': '-1', '-0.42': '-1', '-0.66': '-1', '-0.49': '-1', '-0.64': '-1', '-0.47': '-1', '-0.48': '-1', '-0.0062': '0', '-0.44': '0', '-0.33': '-1', '0.11': '0', '0.093': '0', '0.1': '0', '0.088': '0', '0.094': '0', '0.082': '0', '0.034': '0', '0.028': '0', '0.0094': '0', '0.0079': '0', '0.0044': '0', '0.01': '0', '0.066': '0', '-0.0021': '0', '-0.1': '0', '-0.062': '0', '-0.056': '0', '-0.037': '0', '-0.024': '0', '-0.006': '0', '0.16': '0', '0.19': '0', '0.28': '0', '0.24': '0', '0.15': '0', '0.005': '0', '-0.0035': '0', '0.007': '0', '0.003': '0', '-0.051': '0', '0.038': '0', '0.097': '0', '0.0087': '0', '0.044': '0', '0.051': '0', '0.023': '0', '0.0081': '0', '-0.0034': '0', '-0.012': '0', '-0.16': '0', '-0.11': '0', '-0.033': '0', '-0.07': '0', '-0.15': '0', '0.074': '0', '0.14': '0', '0.0017': '0', '0.072': '0', '0.019': '0', '-0.082': '0', '-0.14': '0', '-0.17': '0', '-0.03': '0', '-0.0051': '0', '0.043': '0', '0.13': '0', '0.083': '0', '0.089': '0', '0.069': '0', '0.04': '0', '-0.034': '0', '-0.069': '0', '-0.076': '0', '-0.028': '0', '0.0036': '0', '0.059': '0', '0.036': '0', '0.02': '0', '-0.00017': '0', '-0.2': '0', '-0.29': '0', '-0.25': '0', '-0.0024': '0', '-0.0053': '0', '-0.061': '0', '0.033': '0', '0.067': '0', '0.08': '0', '0.015': '0', '0.016': '0', '0.035': '0', '0.06': '0', '0.065': '0', '-0.097': '0', '-0.049': '0', '-0.044': '0', '-0.047': '0', '-0.059': '0', '-0.019': '0', '-0.01': '0', '-0.017': '0', '-0.066': '0', '-0.23': '0', '-0.21': '0', '-0.24': '0', '0.061': '0', '0.017': '0', '0.12': '0', '0.049': '0', '-0.0033': '0', '-0.023': '0', '-0.12': '0', '-0.04': '0', '0.087': '0', '0.073': '0', '0.053': '0', '0.0018': '0', '-0.011': '0', '-0.00026': '0', '0.0097': '0', '0.011': '0', '0.018': '0', '0.0092': '0', '-0.002': '0', '-0.19': '0', '0.0059': '0', '0.05': '0', '-0.021': '0', '-0.0056': '0', '-0.031': '0', '-0.018': '0', '-0.13': '0', '-0.042': '0', '-0.026': '0', '0.0072': '0', '-0.0081': '0', '0.0027': '0', '-0.013': '0', '0.021': '0', '0.032': '0', '0.079': '0', '0.027': '0', '-0.092': '0', '-0.088': '0', '-0.079': '0', '-0.086': '0', '-0.083': '0', '-0.038': '0', '-0.089': '0', '-0.099': '0', '-0.09': '0', '0.084': '0', '0.075': '0', '0.058': '0', '0.046': '0', '-0.029': '0', '-0.055': '0', '-0.078': '0', '0.004': '0', '0.17': '0', '0.18': '0', '0.2': '0', '0.22': '0', '0.068': '0', '0.081': '0', '-0.041': '0', '-0.014': '0', '0.006': '0', '-0.00071': '0', '0.013': '0', '0.0076': '0', '0.063': '0', '0.031': '0', '-0.084': '0', '0.029': '0', '0.008': '0', '0.022': '0', '0.092': '0', '0.056': '0', '0.07': '0', '0.095': '0', '0.039': '0', '-0.025': '0', '0.091': '0', '0.077': '0', '0.054': '0', '0.086': '0', '-0.0094': '0', '-0.035': '0', '-0.065': '0', '-0.058': '0', '0.0014': '0', '-0.02': '0', '-0.071': '0', '-0.036': '0', '-0.022': '0', '0.012': '0', '0.055': '0', '0.045': '0', '-0.032': '0', '0.041': '0', '-0.094': '0', '-0.0061': '0', '-0.095': '0', '0.014': '0', '-0.085': '0', '-0.053': '0', '-0.22': '0', '-0.098': '0', '-0.28': '0', '-0.0071': '0', '-0.18': '0', '-0.0042': '0', '0.024': '0', '-0.077': '0', '0.042': '0', '-0.0063': '0', '0.00058': '0', '0.00059': '0', '-0.0075': '0', '0.0063': '0', '-0.0091': '0', '-0.0049': '0', '-0.027': '0', '-0.0013': '0', '-0.015': '0', '-0.0074': '0', '0.064': '0', '0.0011': '0', '-0.057': '0', '0.048': '0', '0.025': '0', '0.0088': '0', '-0.26': '0', '0.00056': '0', '-0.043': '0', '-0.0055': '0', '-0.0078': '0', '-0.0084': '0', '-0.0099': '0', '0.047': '0', '-0.045': '0', '0.0042': '0', '0.0066': '0', '0.0013': '0', '0.076': '0', '0.052': '0', '-0.016': '0', '-0.0066': '0', '0.0008': '0', '-0.0088': '0', '-0.046': '0', '-0.0077': '0', '0.0056': '0', '-0.081': '0', '-0.0041': '0', '0.0053': '0', '-0.067': '0', '0.037': '0', '-0.096': '0', '0.0061': '0', '-0.048': '0', '-0.0043': '0', '-0.073': '0', '-0.093': '0', '-0.0052': '0', '0.00081': '0', '-0.00012': '0', '0.062': '0', '0.057': '0', '0.0031': '0', '0.0098': '0', '0.078': '0', '-0.072': '0', '-0.091': '0', '0.0009': '0', '-0.068': '0', '-0.08': '0', '0.0085': '0', '-0.063': '0', '-0.05': '0', '0.0095': '0', '-0.074': '0', '0.0064': '0', '-0.052': '0', '0.0082': '0', '0.0073': '0', '0.23': '0', '0.09': '0', '0.071': '0', '0.085': '0', '0.0054': '0', '0.0047': '0', '0.098': '0', '0.0026': '0', '-0.0083': '0', '0.0052': '0', '-0.008': '0', '0.00072': '0', '-0.36': '0', '0.026': '0', '0.03': '0', '-0.0073': '0', '0.0055': '0', '0.33': '0', '-0.0011': '0', '0.099': '0', '0.26': '0', '-0.005': '0', '-0.054': '0', '-0.00042': '0', '-0.0017': '0', '-0.0047': '0', '-0.087': '0', '-0.0025': '0', '0.21': '0', '-0.0015': '0', '-0.003': '0', '0.00054': '0', '0.096': '0', '-0.3': '0', '-0.31': '0', '-0.0032': '0', '-0.06': '0', '-0.0092': '0', '-0.039': '0', '0.35': '0', '0.3': '0', '-0.064': '0', '-0.0016': '0', '-0.0045': '0', '0.0068': '0', '-0.0028': '0', '-0.0012': '0', '0.0093': '0', '-0.34': '0', '0.0005': '0', '-0.0057': '0', '0.0069': '0', '0.00039': '0', '0.00052': '0', '-0.0054': '0', '-0.0039': '0', '0.002': '0', '0.0078': '0', '0.0045': '0', '0.0033': '0', '-0.075': '0', '-0.0037': '0', '-0.00052': '0', '0.00096': '0', '0.00037': '0', '0.00041': '0', '-0.00036': '0', '-0.0072': '0', '0.0099': '0', '0.0016': '0', '-0.0097': '0', '0.0024': '0', '0.009': '0', '0.25': '0', '0.0051': '0', '-0.0064': '0', '0.0012': '0', '-0.0023': '0', '0.0067': '0', '-0.0046': '0', '-0.27': '0', '-0.0093': '0', '0.29': '0', '0.0034': '0', '-0.0095': '0', '0.0086': '0', '-9.0': '0', '-0.0089': '0', '-0.0096': '0', '-0.0069': '0', '0.0096': '0', '0.0071': '0', '-0.0059': '0', '0.0037': '0', '-0.35': '0', '0.42': '0', '0.34': '1', '0.0019': '0', '-0.00057': '0', '0.00044': '0', '7.0': '0', '-0.001': '0', '0.0077': '0', '0.0022': '0', '0.0041': '0', '0.27': '0', '-0.00075': '0', '0.00064': '0', '-0.0029': '0', '0.0038': '0', '0.00075': '0', '0.0039': '0', '-0.00049': '0', '0.001': '0', '-0.00048': '0', '-0.00024': '0', '0.0065': '0', '-0.004': '0', '0.0048': '0', '0.0028': '0', '-0.0065': '0', '-0.0079': '0', '2.0': '0', '-0.0098': '0', '0.0091': '0', '-0.4': '0', '0.0089': '0', '-0.00083': '0', '0.0057': '0', '-0.0038': '0', '-0.00044': '0', '-7.0': '0', '0.0062': '0', '0.00043': '0', '-0.0086': '0', '-0.0068': '0', '0.0049': '0', '-0.0087': '0', '-0.0076': '0', '0.0021': '0', '-0.38': '0', '-0.0082': '0', '0.0023': '0', '-0.0048': '0', '-0.00094': '0', '0.0029': '0', '0.0074': '0', '-0.0085': '0', '0.00048': '0', '-0.0026': '0', '0.0035': '0', '-0.007': '1', '0.00084': '0', '0.00068': '0', '-0.00043': '0', '0.0075': '1', '-0.00095': '0', '0.0046': '1', '-0.009': '0', '-0.00047': '0', '0.0084': '0', '0.0083': '0', '0.45': '1', '0.88': '1', '1.0': '1', '0.66': '1', '0.55': '1', '0.48': '1', '0.56': '1', '0.95': '1', '0.69': '1', '0.82': '1', '0.77': '1', '0.83': '1', '0.85': '1', '0.89': '1', '0.76': '1', '0.74': '1', '0.73': '1', '0.75': '1', '0.9': '1', '0.8': '1', '0.98': '1', '0.91': '1', '0.7': '1', '0.68': '1', '0.78': '1', '0.97': '1', '0.94': '1', '0.99': '1', '0.6': '1', '0.79': '1', '0.96': '1', '0.86': '1', '0.87': '1', '0.84': '1', '0.93': '1', '0.92': '1', '0.81': '1', '0.64': '1', '0.67': '1', '0.58': '1', '0.53': '1', '0.4': '1', '0.63': '1', '0.65': '1', '0.61': '1', '0.57': '1', '0.44': '1', '0.59': '1', '0.46': '1', '0.62': '1', '0.71': '1', '0.47': '1', '0.5': '1', '0.72': '1', '0.54': '1', '0.32': '1', '0.38': '1', '0.52': '1', '0.37': '1', '0.51': '1', '0.31': '1', '0.43': '1', '-6.0': '1', '0.49': '1', '0.36': '1', '0.41': '1', '0.39': '1', '-0.00093': '1'}

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
        truncated = str(math.fabs(raw_decision))
        trim_point = 0
        # Iterate over each digit
        for digit in truncated:
            # Increment trim point
            trim_point += 1
            # Check if digit is not 0
            if digit != '.' and digit != '0':
                # Include one extra digit
                trim_point += 1
                break
        # Truncate up to trim point
        truncated = truncated[:trim_point]
        # Get sign from raw value
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