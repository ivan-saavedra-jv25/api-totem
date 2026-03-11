from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.product import Product as ProductModel
from app.schemas.cart import Cart, CartAddRequest, CartRemoveRequest
from app.services.cart_service import cart_service

router = APIRouter(prefix="/cart", tags=["cart"])


def get_session_id(request: Request) -> str:
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        session_id = request.client.host
    return session_id


@router.get("/", response_model=Cart)
def get_cart(request: Request):
    session_id = get_session_id(request)
    return cart_service.get_cart(session_id)


@router.post("/add", response_model=Cart)
def add_to_cart(
    request: Request, 
    cart_item: CartAddRequest, 
    db: Session = Depends(get_db)
):
    session_id = get_session_id(request)
    
    product = db.query(ProductModel).filter(ProductModel.id == cart_item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.stock < cart_item.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    return cart_service.add_item(
        session_id=session_id,
        product_id=product.id,
        name=product.name,
        price=product.price,
        quantity=cart_item.quantity,
        image_url=product.image_url
    )


@router.post("/remove", response_model=Cart)
def remove_from_cart(
    request: Request, 
    cart_item: CartRemoveRequest
):
    session_id = get_session_id(request)
    return cart_service.remove_item(
        session_id=session_id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity
    )


@router.delete("/", response_model=Cart)
def clear_cart(request: Request):
    session_id = get_session_id(request)
    return cart_service.clear_cart(session_id)
