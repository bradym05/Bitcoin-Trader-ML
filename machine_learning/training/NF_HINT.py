# Dependencies
import pandas as pd

from hierarchicalforecast.utils import aggregate

# Define hierarchical levels
spec = [
    ['PreviousClose'],
    ['PreviousClose', 'Sentiment'],
    ['PreviousClose', 'Sentiment', 'Open'],
    ['PreviousClose', 'Sentiment', 'Open', 'High'],
    ['PreviousClose', 'Sentiment', 'Open', 'High', 'Low'],
    ['PreviousClose', 'Sentiment', 'Open', 'High', 'Low', 'Close'],
    ['PreviousClose', 'Sentiment', 'Open', 'High', 'Low', 'Close', 'Action'],
]
