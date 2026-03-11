from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.order import Order as OrderModel
from app.models.product import Product as ProductModel
from app.schemas.order import Order, OrderCreate
from app.services.cart_service import cart_service

router = APIRouter(prefix="/orders", tags=["orders"])


def get_session_id(request: Request) -> str:
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        session_id = request.client.host
    return session_id


@router.post("/", response_model=Order)
def create_order(request: Request, order_data: OrderCreate, db: Session = Depends(get_db)):
    session_id = get_session_id(request)
    cart = cart_service.get_cart(session_id)
    
    if not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    total = 0.0
    order_items = []
    
    for item in cart.items:
        product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for product {product.name}")
        
        product.stock -= item.quantity
        db.commit()
        
        item_total = item.quantity * item.unit_price
        total += item_total
        
        order_items.append({
            "product_id": item.product_id,
            "product_name": item.product_name,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "subtotal": item_total
        })
    
    db_order = OrderModel(
        items=order_items,
        total=total,
        status="pending"
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    cart_service.clear_cart(session_id)
    
    return db_order


@router.get("/{order_id}", response_model=Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/", response_model=List[Order])
def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    orders = db.query(OrderModel).order_by(OrderModel.created_at.desc()).offset(skip).limit(limit).all()
    return orders


@router.put("/{order_id}/status")
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    valid_statuses = ["pending", "confirmed", "preparing", "ready", "completed", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    order.status = status
    db.commit()
    db.refresh(order)
    
    return {"message": f"Order {order_id} status updated to {status}", "order": order}
