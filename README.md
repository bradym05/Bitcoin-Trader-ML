# Bitcoin-Trader-ML
 
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Bitcoin Trader ML is a automatic *crypto trading bot* for *Coinbase* using Transformer Neural Networks.

Train one Autoformer for crypto price predictions, and one for trade decisions (-1: Sell, 0: Hold, 1: Buy).

## Requirements Installation

To get started with this project, you need to install the required packages. Follow the steps below:

1. **Create a virtual environment (optional but recommended)**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\ScriptsActivate`
    ```

2. **Install the required packages**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage Instructions

1. **Clone the repository**:
    ```bash
    git clone https://github.com/bradym05/Bitcoin-Trader-ML.git
    cd Bitcoin-Trader-ML
    ```

2. **Get your coinbase API key**:

    Create your API key and download the JSON file (coinbase_cloud_api_key.json)
    https://portal.cdp.coinbase.com/access/api

3. **Setup private folder**:

    In Bitcoin-Trader-ML\main
    Create folder "private"
    Copy your coinbase API file to Bitcoin-Trader-ML\main\private\coinbase_cloud_api_key.json
    Create init file inside of "private" folder:
    ```python
    key_file_path = "main\\private\\coinbase_cloud_api_key.json"
    portfolio_uuid = "YOUR PORTFOLIO UUID"
    ```

4. **Train Price Prediction Autoformer**:

    *Using neuralforecast,*

    1. **Preprocess your dataset**:

        *Columns*
        >y is the price
        ```python
        ['ds', 'unique_id', 'open_price', 'high', 'low', 'y', 'btc_vol',
        'usdc_vol', 'ema0', 'ema1', 'ema2', 'ema3', 'ema4', 'ema5', 'ema6',
        'ema7', 'ema8', 'ema9', 'wma0', 'wma1', 'wma2', 'wma3', 'wma4', 'wma5',
        'wma6', 'wma7', 'wma8', 'wma9', 'sma0', 'sma1', 'sma2', 'sma3', 'sma4',
        'sma5', 'sma6', 'sma7', 'sma8', 'sma9']
        ```
        *Example Dataframe*
        ```bash
                        ds  unique_id  open_price      high       low         y   btc_vol  usdc_vol  ...      sma2      sma3      sma4      sma5      sma6      sma7      sma8      sma9
        0 2017-08-19 00:00:00          0    0.143153  0.145590  0.142314  0.145074  0.001439  5.925526  ...  0.149302  0.148726  0.148141  0.146973  0.145702  0.144943  0.144299  0.143965
        1 2017-08-19 00:05:00          0    0.143313  0.145609  0.142485  0.145030  0.001403  5.780747  ...  0.149254  0.148677  0.148043  0.146867  0.145639  0.144889  0.144271  0.143939
        2 2017-08-19 00:10:00          0    0.143473  0.145627  0.142655  0.144987  0.001367  5.635968  ...  0.149206  0.148628  0.147946  0.146761  0.145576  0.144836  0.144243  0.143914
        3 2017-08-19 00:15:00          0    0.143633  0.145646  0.142826  0.144943  0.001331  5.491189  ...  0.149158  0.148579  0.147849  0.146655  0.145512  0.144782  0.144216  0.143888
        4 2017-08-19 00:20:00          0    0.143793  0.145664  0.142997  0.144900  0.001294  5.346409  ...  0.149110  0.148531  0.147751  0.146549  0.145449  0.144728  0.144188  0.143862
        [648853 rows x 38 columns]
        ```

    2. **Train your autoformer**:
        >Optional: Edit and use machine_learning\training\NF_Autoformer.py according to your dataset
        
        Save your trained autoformer to: machine_learning\training\saved\Autoformer_30M\

5. **Train Decision Autoformer**:

    *Using neuralforecast,*

    1. **Preprocess your dataset**:

        Decisions are mapped as follows:

        ## Decisions Chart

        | Value    | Decision |
        |----------|----------|
        | -1       | Sell     |
        |  0       | Hold     |
        |  1       | Buy      |

        ##

        *Columns*
        >y is the decision value
        >p1-p12 are predictions from the price prediction autoformer
        ```python
        ['y', 'ds', 'unique_id', 'open_price', 'high', 'low', 'close_price',
        'btc_vol', 'usdc_vol', 'ema0', 'ema1', 'ema2', 'ema3', 'ema4', 'ema5',
        'ema6', 'ema7', 'ema8', 'ema9', 'wma0', 'wma1', 'wma2', 'wma3', 'wma4',
        'wma5', 'wma6', 'wma7', 'wma8', 'wma9', 'sma0', 'sma1', 'sma2', 'sma3',
        'sma4', 'sma5', 'sma6', 'sma7', 'sma8', 'sma9', 'p1', 'p2', 'p3', 'p4',
        'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12']
        ```
        *Example Dataframe*
        ```bash
        y                     ds  open_price      high       low  close_price   btc_vol  usdc_vol  ...        p4       p5        p6        p7        p8       p9       p10       p11       p12
        0  1 2017-08-19 00:00:00    0.143153  0.145590  0.142314     0.145074  0.001439  5.925526  ...  0.144832  0.14463  0.144239  0.143678  0.143814  0.14406  0.144468  0.144901  0.142082
        1  1 2017-08-19 00:15:00    0.143633  0.145646  0.142826     0.144943  0.001331  5.491189  ...  0.144832  0.14463  0.144239  0.143678  0.143814  0.14406  0.144468  0.144901  0.142082
        2  1 2017-08-19 00:30:00    0.144113  0.145701  0.143339     0.144813  0.001222  5.056851  ...  0.144832  0.14463  0.144239  0.143678  0.143814  0.14406  0.144468  0.144901  0.142082
        3  1 2017-08-19 00:45:00    0.144594  0.145757  0.143851     0.144683  0.001113  4.622513  ...  0.144832  0.14463  0.144239  0.143678  0.143814  0.14406  0.144468  0.144901  0.142082
        4  1 2017-08-19 01:00:00    0.145074  0.145812  0.144364     0.144552  0.001005  4.188176  ...  0.144832  0.14463  0.144239  0.143678  0.143814  0.14406  0.144468  0.144901  0.142082
        [216285 rows x 51 columns]
        ```

    2. **Train your autoformer**:
        >Optional: Edit and use machine_learning\training\NF_DecisionAutoformer.py according to your dataset

        Save your trained autoformer to: machine_learning\training\saved\DecisionAutoformer\

        >Note: You must convert your autoformer's raw outputs into int decision values

6. **Begin Auto Trading**:

    Example Usage:
    ```python
    from main import AutoTrader

    # Create AutoTrader object, set paper to true to simulate trading
    auto_trader = AutoTrader(paper=True)

    # Run indefinitely
    while True:
        time.sleep(1)
        # Print decision history
        print(auto_trader.predict.decisions)
    ```

## 🎓 Citations
If you have used Bitcoin Trader ML, please cite with the following reference:
```text
  @misc{bitcoin-trader-ml,
    author = {Brady Maki},
    title = {Bitcoin-Trader-ML},
    year = {2024},
    url = {https://github.com/bradym05/Bitcoin-Trader-ML},
    note = {Automated 24/7 bitcoin trader for Coinbase using Transformer Neural Networks}
  }
```

## Authors

| Author      | Contact Info         |
|-------------|----------------------|
| Brady Maki  | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/brady-m-899456230/)    |

## 📜 License

Bitcoin Trader ML is licensed under the MIT License. See the [LICENSE](https://github.com/bradym05/Bitcoin-Trader-ML/blob/main/LICENSE) file for more information.
