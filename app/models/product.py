from sqlalchemy import Column, Integer, String, Float, Text
from app.models.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    image_url = Column(String(500))

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
