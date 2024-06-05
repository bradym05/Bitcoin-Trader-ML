# Dependencies
from neuralforecast import NeuralForecast
from neuralforecast.models import DeepAR, NHITS
import torch

import pickle
import pandas as pd
import numpy as np

# SETTINGS
DATA_PATH = "machine_learning\data\Preprocessed_1hour.pkl"
print(torch.cuda.is_available())

# Get preprocessed data
with open(DATA_PATH, 'rb') as f:
    preprocessed = pd.DataFrame(pickle.load(f))
    preprocessed['ds'] = pd.to_datetime(preprocessed['ds'])

models = [
    DeepAR(
        h=4,
        start_padding_enabled=True,
        scaler_type='standard',
        input_size=64,
        learning_rate=1e-4)
    ]

nf = NeuralForecast(models=models, freq='4H')
nf.fit(df=preprocessed, val_size=0)
nf.save(path='machine_learning\\agents\\saved\\v1\\',
        model_index=None, 
        overwrite=True,
        save_dataset=True)