# Dependencies
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class CurrencyValue:
    value: str
    currency: str

@dataclass
class Portfolio:
    name: str
    uuid: str
    type: str
    deleted: bool

@dataclass
class Portfolios:
    portfolios: List[Portfolio]

@dataclass
class PortfolioBalances:
    total_balance: CurrencyValue
    total_futures_balance: CurrencyValue
    total_cash_equivalent_balance: CurrencyValue
    total_crypto_balance: CurrencyValue
    futures_unrealized_pnl: CurrencyValue
    perp_unrealized_pnl: CurrencyValue

@dataclass
class SpotPosition:
    asset: str
    account_uuid: str
    total_balance_fiat: float
    total_balance_crypto: float
    available_to_trade_fiat: float
    allocation: float
    cost_basis: CurrencyValue
    asset_img_url: str
    is_cash: bool
    average_entry_price: Optional[float]
    asset_uuid: str
    available_to_trade_crypto: float
    unrealized_pnl: float

@dataclass
class Breakdown:
    portfolio: Portfolio
    portfolio_balances: PortfolioBalances
    spot_positions: List[SpotPosition]
    perp_positions: List
    futures_positions: List

@dataclass
class PortfolioBreakdown:
    breakdown: Breakdown