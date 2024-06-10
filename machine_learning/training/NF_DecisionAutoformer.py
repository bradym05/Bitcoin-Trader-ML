# Dependencies
from neuralforecast import NeuralForecast
from neuralforecast.models import Autoformer, PatchTST, TimesNet
from neuralforecast.losses.pytorch import MAE, DistributionLoss
import torch

import pickle
import math
import pandas as pd
import numpy as np

# SETTINGS
DATA_PATH = "machine_learning\data\BTCUSDT_DECISION_15M.pkl"
BTC_FACTOR = 71000

# Get preprocessed data
with open(DATA_PATH, 'rb') as f:
    # Load base dataset
    preprocessed = pd.DataFrame(pickle.load(f))
    preprocessed['ds'] = pd.to_datetime(preprocessed['ds'])
    preprocessed['unique_id'] = preprocessed['unique_id'].map(lambda x: 0)

print(preprocessed.head())
print(preprocessed.tail())
print(preprocessed.shape)

horizon = 1

nf = NeuralForecast(
    models=[
        Autoformer(
            h=horizon,
            input_size=32,
            hidden_size=512,
            conv_hidden_size=32,
            encoder_layers=2,
            decoder_layers=1,
            n_head=4,
            loss=MAE(),
            scaler_type='robust',
            learning_rate=5e-8,
            max_steps=50000,
            val_check_steps=100)
        ],
    freq='15T'
    )
# Fit to dataset
nf.fit(df=preprocessed, sort_df=False, val_size=0)
# Save
nf.save(path='machine_learning\\training\\saved\\DecisionAutoformer2\\',
        model_index=None, 
        overwrite=True,
        save_dataset=True)

'''
# CREATE DICTIONARY OF TRANSLATIONS FOR AUTOFORMER
# Example Autoformer Output: -0.872364, Example y Value: -1
# Resulting Translation: {'-0.9':'-1'}
nf = NeuralForecast.load(path='machine_learning\\training\\saved\\DecisionAutoformer\\')
predictions = nf.predict_insample()
predictions.index = pd.RangeIndex(len(predictions.index))
translations = {'-1':[], '0':[], '1':[]}

print(predictions)

for n in range(len(predictions.index)):
    i = predictions.index[n]
    predicted_value = predictions["Autoformer"][i]
    real_value = predictions["y"][i]
    translations[str(int(real_value))].append(predicted_value)

occurences = {}

for key, all_vals in translations.items():
    occurences[key] = {}
    for val in all_vals:
        truncated = str(math.fabs(val))[:3]
        truncated = float(truncated)
        truncated = math.copysign(truncated, val)
        truncated = str(truncated)
        if not truncated in occurences[key]:
            occurences[key][truncated] = 0
        occurences[key][truncated] += 1

direct_translations = {}

for key, occ_dict in occurences.items():
    for val_key, count in occ_dict.items():
        highest = True
        for other_key, other_dict in occurences.items():
            if other_key != key and val_key in other_dict:
                if other_dict[val_key] > count:
                    highest = False
                    break
        if highest == True:
            direct_translations[val_key] = key

print(occurences)
print(direct_translations)
'''