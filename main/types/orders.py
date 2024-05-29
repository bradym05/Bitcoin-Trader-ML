# Dependencies
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

class OrderStatus(Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP_LIMIT = "STOP_LIMIT"

@dataclass
class SuccessResponse:
    order_id: str
    product_id: str
    side: str
    client_order_id: str

@dataclass
class LimitLimitGtc:
    base_size: str
    limit_price: str
    post_only: bool

@dataclass
class OrderConfiguration:
    limit_limit_gtc: Optional[LimitLimitGtc]

@dataclass
class ErrorResponse:
    error: str
    message: str
    error_details: str
    preview_failure_reason: str

@dataclass
class OrderResponse:
    success: bool
    failure_reason: str
    order_id: str
    order_configuration: Optional[OrderConfiguration]
    success_response: Optional[SuccessResponse] = None
    error_response: Optional[ErrorResponse] = None

@dataclass
class LimitGoodTillCancelled:
    base_size: str
    limit_price: str
    post_only: bool

@dataclass
class Order:
    order_id: str
    product_id: str
    user_id: str
    side: str
    client_order_id: str
    status: str
    time_in_force: str
    created_time: str
    completion_percentage: str
    filled_size: str
    average_filled_price: str
    fee: str
    number_of_fills: str
    filled_value: str
    pending_cancel: bool
    size_in_quote: bool
    total_fees: str
    size_inclusive_of_fees: bool
    total_value_after_fees: str
    trigger_status: str
    order_type: str
    reject_reason: str
    settled: bool
    product_type: str
    reject_message: str
    cancel_message: str
    order_placement_source: str
    outstanding_hold_amount: str
    is_liquidation: bool
    last_fill_time: Optional[str]
    leverage: str
    margin_type: str
    retail_portfolio_id: str
    order_configuration: OrderConfiguration
    edit_history: List[dict] = field(default_factory=list)

@dataclass
class AllOrdersList:
    orders: List[Order]