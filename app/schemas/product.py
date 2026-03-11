from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional


class ProductBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    image_url: Optional[str] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v < 0:
            raise ValueError('Price must be non-negative')
        return v
    
    @field_validator('stock')
    @classmethod
    def validate_stock(cls, v):
        if v < 0:
            raise ValueError('Stock must be non-negative')
        return v


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    image_url: Optional[str] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Name cannot be empty')
        return v.strip() if v else v
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v is not None and v < 0:
            raise ValueError('Price must be non-negative')
        return v
    
    @field_validator('stock')
    @classmethod
    def validate_stock(cls, v):
        if v is not None and v < 0:
            raise ValueError('Stock must be non-negative')
        return v


class Product(ProductBase):
    id: int
