from pydantic import BaseModel
from typing import List, Dict, Any


class CartItem(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float
    image_url: str = None

    class Config:
        from_attributes = False


class Cart(BaseModel):
    items: List[CartItem]
    total: float
    total_items: int

    class Config:
        from_attributes = False


class CartAddRequest(BaseModel):
    product_id: int
    quantity: int = 1


class CartRemoveRequest(BaseModel):
    product_id: int
    quantity: int = 1
