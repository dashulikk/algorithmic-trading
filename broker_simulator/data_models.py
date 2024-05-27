from pydantic import BaseModel


class Order(BaseModel):
    id: int
    username: str
    stock: str
    order_type: str
    trigger_price: float
    amount: float


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class BuyStockRequest(BaseModel):
    stock: str
    amount: float


class SellStockRequest(BaseModel):
    stock: str
    amount: float


class TopUpRequest(BaseModel):
    amount: float


class StockPriceRequest(BaseModel):
    stock: str
