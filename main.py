from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import create_tables
from app.routers import products, cart, orders

app = FastAPI(
    title="Totem API",
    description="Backend API for self-service kiosk system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)


@app.on_event("startup")
def startup_event():
    create_tables()


@app.get("/")
def root():
    return {"message": "Totem API is running", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
