# Dependencies
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class OrderEvent:
    order_id: str
    client_order_id: str
    cumulative_quantity: str
    leaves_quantity: str
    avg_price: str
    total_fees: str
    status: str
    product_id: str
    creation_time: str
    order_side: str
    order_type: str
    limit_price: Optional[str] = "0"
    stop_price: Optional[str] = "0"

@dataclass()
class TickerEvent:
    type: str
    product_id: str
    price: str
    volume_24_h: str
    low_24_h: str
    high_24_h: str
    low_52_w: str
    high_52_w: str
    price_percent_chg_24_h: str
    best_bid: str
    best_bid_quantity: str
    best_ask: str
    best_ask_quantity: str

@dataclass
class WebsocketEvent:
    type: Optional[str]
    orders: Optional[List[OrderEvent]] = field(default_factory=list)
    tickers: Optional[List[TickerEvent]] = field(default_factory=list)

@dataclass
class WebsocketMessage:
    channel: str
    client_id: str
    timestamp: str
    sequence_num: int
    events: List[WebsocketEvent]