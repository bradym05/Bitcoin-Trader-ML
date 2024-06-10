# Dependencies
from neuralforecast import NeuralForecast
from neuralforecast.models import Autoformer, PatchTST, TimesNet
from neuralforecast.losses.pytorch import MAE, DistributionLoss
import torch

import pickle
import pandas as pd
import numpy as np

# SETTINGS
DATA_PATH = "machine_learning\data\BTCUSDT_TICKER_5M.pkl"
BTC_FACTOR = 71000
print(torch.cuda.is_available())
pd.Series.to_list
# Get preprocessed data
with open(DATA_PATH, 'rb') as f:
    # Load base dataset
    preprocessed = pd.DataFrame(pickle.load(f))
    preprocessed['ds'] = pd.to_datetime(preprocessed['ds'])
    preprocessed['unique_id'] = preprocessed['unique_id'].map(lambda x: 0)

print(preprocessed.head())
print(preprocessed.tail())
print(preprocessed.shape)

horizon = 8

#'''
nf = NeuralForecast(
    models=[
        Autoformer(
            h=horizon,
            input_size=24,
            hidden_size=512,
            conv_hidden_size=32,
            encoder_layers=2,
            decoder_layers=1,
            n_head=4,
            loss=MAE(),
            scaler_type='standard',
            learning_rate=1e-4,
            max_steps=1000,
            val_check_steps=10)
        ],
    freq='30T'
    )
#'''
#nf = NeuralForecast.load(path="machine_learning\\training\\saved\\Autoformer_V4")
# Fit to dataset
nf.fit(df=preprocessed, sort_df=False, val_size=0)
# Save
nf.save(path='machine_learning\\training\\saved\\Autoformer_30M\\',
        model_index=None, 
        overwrite=True,
        save_dataset=True)
