# Dependencies
import uuid

from typing import Tuple, Optional, Dict
from main.private import portfolio_uuid
from main.types import Order, OrderSide, OrderStatus, LimitLimitGtc
from main.services import SingletonBase

# Declare paper client service
class PaperClientService(SingletonBase):
    def __init__(self, balance:float=500.00):
        # Initialize variables
        self._paper_bal = balance
        self._orders = {}
        self._client_orders = {}
    # Create order dictionary
    def _order_dict(self):
        return {
            'order_id':"",
            'product_id':"",
            'user_id':portfolio_uuid,
            'client_order_id':"",
            'time_in_force':"0",
            'side':"",
            'status':OrderStatus.PENDING.value,
            'average_filled_price':"0",
            'fee':"0",
            'number_of_fills':"0",
            'filled_size':"0",
            'filled_value':"0",
            'total_fees':"0",
            'total_value_after_fees':"0",
            'order_configuration':{
                'limit_limit_gtc':{
                    'base_size':"",
                    'limit_price':"",
                    'post_only':False
                }
            },
            'created_time':"0",
            'completion_percentage':"0",
            'pending_cancel':False,
            'size_in_quote':False,
            'total_fees':"0",
            'size_inclusive_of_fees':False,
            'total_value_after_fees':"0",
            'trigger_status':"",
            'order_type':"",
            'reject_reason':"",
            'settled':False,
            'product_type':"",
            'reject_message':"",
            'cancel_message':"",
            'order_placement_source':"",
            'outstanding_hold_amount':"",
            'is_liquidation':False,
            'leverage':"",
            'margin_type':"",
            'retail_portfolio_id':"",
            'success':True
        }
    # Mimic rest client methods
    def limit_order_gtc_buy(self, client_order_id: str, product_id: str, base_size: str, limit_price: str) -> Dict[str, any]:
        if client_order_id in self._client_orders:
            return {}
        order_id = str(uuid.uuid4())
        order_dict = self._order_dict()
        order_dict['order_id'] = order_id
        order_dict['product_id'] = product_id
        order_dict['side'] = "BUY"
        order_dict['order_configuration']['limit_limit_gtc'] = {
                'base_size':base_size,
                'limit_price':limit_price,
                'post_only':False
            }
        self._orders[order_id] = order_dict
        self._client_orders[client_order_id] = order_id
        return order_dict
    def limit_order_gtc_sell(self, client_order_id: str, product_id: str, base_size: str, limit_price: str) -> Dict[str, any]:
        if client_order_id in self._client_orders:
            return {}
        order_id = str(uuid.uuid4())
        order_dict = self._order_dict()
        order_dict['order_id'] = order_id
        order_dict['product_id'] = product_id
        order_dict['side'] = "SELL"
        order_dict['order_configuration']['limit_limit_gtc'] = {
                'base_size':base_size,
                'limit_price':limit_price,
                'post_only':False
            }
        self._orders[order_id] = order_dict
        self._client_orders[client_order_id] = order_id
        return order_dict
    def get_order(self, order_id: str) -> Dict[str, any]:
        if order_id in self._orders:
            order = self._orders[order_id]
            config = order['order_configuration']['limit_limit_gtc']
            order['average_filled_price'] = config['limit_price']
            order['completion_percentage'] = "100"
            order['filled_size'] = config['base_size']
            filled_value = float(order['filled_size']) * float(config['limit_price'])
            order['filled_value'] = str(filled_value)
            order['fee'] = str(filled_value * 0.035)
            order['number_of_fills'] = "1"
            order['status'] = "FILLED"
            return {'order':order}
        else:
            return {}