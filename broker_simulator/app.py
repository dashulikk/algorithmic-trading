import os

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from broker_simulator.data_models import UserCreate, UserLogin, BuyStockRequest, SellStockRequest, TopUpRequest, StockPriceRequest, \
    SubmitOrderRequest
from broker_simulator.database import Database
from broker_simulator.salted_password import SaltedPassword
from broker_simulator.service import Service

load_dotenv()

app = FastAPI()
db = Database()
service = Service(db)

JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
JWT_ALGORITHM = "HS256"

# Define the OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Utility function to create access token
def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


# Utility function to get current user
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return username
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


@app.post("/create_user", status_code=200)
async def create_user(user: UserCreate):
    try:
        password_object = SaltedPassword(user.password)
        service.create_user(user.username, password_object.password_hash, password_object.salt)
        return {"message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Exception: {e}")


@app.post("/delete_user", status_code=200)
async def delete_user(username: str = Depends(get_current_user)):
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    try:
        service.delete_user(username)
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Exception: {e}")


@app.post("/login", status_code=200)
async def login(user: UserLogin):
    username = user.username
    password = user.password
    try:
        stored_password_hash, salt = service.get_user_password_and_salt(username)
        if SaltedPassword.check_password(password, stored_password_hash, salt):
            access_token = create_access_token(data={"sub": username})
            return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Exception: {e}")


@app.get("/get_balance", status_code=200)
async def get_balance(token: str = Depends(oauth2_scheme)):
    username: str = get_current_user(token)
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    try:
        return {"balance": f"{service.get_balance(username)}"}
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Exception: {e}")


@app.put("/topup", status_code=200)
async def topup(topup_request: TopUpRequest, token: str = Depends(oauth2_scheme)):
    username: str = get_current_user(token)
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    try:
        service.topup(username, topup_request.amount)
        return {"message": "Operation was successful"}
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Exception: {e}")


@app.get("/get_stock_price", status_code=200)
async def get_stock_price(stock_request: StockPriceRequest):
    try:
        return {"stock_price": Service.stock_price(stock_request.stock)}
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Exception: {e}")


@app.put("/buy", status_code=200)
async def buy_stock(buy_stock_request: BuyStockRequest, token: str = Depends(oauth2_scheme)):
    username: str = get_current_user(token)
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    try:
        service.buy_stock(username, buy_stock_request.stock, buy_stock_request.amount)
        return {"message": "Operation was successful"}
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Exception: {e}")


@app.put("/sell", status_code=200)
async def sell_stock(sell_stock_request: SellStockRequest, token: str = Depends(oauth2_scheme)):
    username: str = get_current_user(token)
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    try:
        service.sell_stock(username, sell_stock_request.stock, sell_stock_request.amount)
        return {"message": "Operation was successful"}
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Exception: {e}")


@app.get("/get_portfolio", status_code=200)
async def get_portfolio(token: str = Depends(oauth2_scheme)):
    username: str = get_current_user(token)
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    try:
        portfolio = service.get_portfolio(username)
        return {"portfolio": f"{portfolio}"}
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Exception: {e}")


@app.get("/get_net_worth", status_code=200)
async def get_net_worth(token: str = Depends(oauth2_scheme)):
    username: str = get_current_user(token)
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    try:
        net_worth = service.get_net_worth(username)
        return {"net_worth": f"{net_worth}"}
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Exception: {e}")


@app.put("/submit_order", status_code=200)
async def submit_order(submit_order_request: SubmitOrderRequest, token: str = Depends(oauth2_scheme)):
    username: str = get_current_user(token)
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    try:
        service.submit_order(username, submit_order_request.order_type,
                             submit_order_request.stock,
                             submit_order_request.amount,
                             submit_order_request.trigger_price)

        return {"Order submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Exception: {e}")


@app.get("/get_order_book", status_code=200)
async def get_order_book():
    try:
        return {"order_book": service.get_order_book()}
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Exception: {e}")