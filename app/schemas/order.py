from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float


class OrderItem(OrderItemBase):
    product_name: str
    subtotal: float

    class Config:
        from_attributes = False


class OrderCreate(BaseModel):
    items: List[Dict[str, Any]]


class Order(BaseModel):
    id: int
    items: List[Dict[str, Any]]
    total: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
