from pydantic import Field
import random

ORDERS = dict()

SUCCESS_ADD_ITEM_MESSAGE = "ok"
SUCCESS_REMOVE_ITEM_MESSAGE = "ok"
ERROR_NO_ORDER_MESSAGE = "error"
ERROR_NO_ITEM_IN_ORDER_MESSAGE = "error"

def create_order() -> str:
    """Create empty order"""
    order_id = "".join([random.choice("awerstryuyiu124356") for _ in range(4)])
    if order_id in ORDERS:
        order_id ="".join([random.choice("awerstryuyiu124356") for _ in range(4)])
    ORDERS[order_id] = []  
    return order_id

def add_item_to_order(order_id: str = Field(description="Identifier of order"),
                      item_id: str = Field(description="Identifier of item`")) -> str:
    """Add item to order"""
    if order_id not in ORDERS:
         return ERROR_NO_ORDER_MESSAGE
    ORDERS[order_id].append(item_id)
    return SUCCESS_ADD_ITEM_MESSAGE

def remove_item_from_order(order_id: str = Field(description="Identifier of order"),
                      item_id: str = Field(description="Identifier of item`")) -> str:
    """Remove item from order"""
    if order_id not in ORDERS:
        return ERROR_NO_ORDER_MESSAGE
    ORDERS[order_id].remove(item_id)
    return SUCCESS_REMOVE_ITEM_MESSAGE
    
def get_order_items(order_id: str = Field(description="Identifier of order")) -> str|list[str]:
    """Returns items by order identifier"""
    return ORDERS.get(order_id, [])

def get_orders() -> list[str]:
    """Returns orders list"""
    return list(ORDERS.keys())