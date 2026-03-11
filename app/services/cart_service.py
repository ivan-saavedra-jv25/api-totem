from typing import Dict, List, Optional
from app.schemas.cart import Cart, CartItem


class CartService:
    def __init__(self):
        self.carts: Dict[str, Dict[int, Dict]] = {}

    def get_cart(self, session_id: str) -> Cart:
        cart_data = self.carts.get(session_id, {})
        items = []
        total = 0.0
        total_items = 0

        for product_id, item_data in cart_data.items():
            item = CartItem(
                product_id=product_id,
                product_name=item_data["name"],
                quantity=item_data["quantity"],
                unit_price=item_data["price"],
                subtotal=item_data["price"] * item_data["quantity"],
                image_url=item_data.get("image_url")
            )
            items.append(item)
            total += item.subtotal
            total_items += item.quantity

        return Cart(items=items, total=total, total_items=total_items)

    def add_item(
        self, 
        session_id: str, 
        product_id: int, 
        name: str, 
        price: float, 
        quantity: int = 1,
        image_url: Optional[str] = None
    ) -> Cart:
        if session_id not in self.carts:
            self.carts[session_id] = {}

        if product_id in self.carts[session_id]:
            self.carts[session_id][product_id]["quantity"] += quantity
        else:
            self.carts[session_id][product_id] = {
                "name": name,
                "price": price,
                "quantity": quantity,
                "image_url": image_url
            }

        return self.get_cart(session_id)

    def remove_item(self, session_id: str, product_id: int, quantity: int = 1) -> Cart:
        if session_id not in self.carts:
            return self.get_cart(session_id)

        if product_id in self.carts[session_id]:
            current_quantity = self.carts[session_id][product_id]["quantity"]
            if current_quantity <= quantity:
                del self.carts[session_id][product_id]
            else:
                self.carts[session_id][product_id]["quantity"] -= quantity

        return self.get_cart(session_id)

    def clear_cart(self, session_id: str) -> Cart:
        if session_id in self.carts:
            del self.carts[session_id]
        return self.get_cart(session_id)


cart_service = CartService()
