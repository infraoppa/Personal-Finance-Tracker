from app.config import APP_TITLE
from app.database import create_tables
from app.transaction import add_transaction, get_transaction, get_transactions
from app.schemas import TransactionCreate
from fastapi import FastAPI
from contextlib import asynccontextmanager
from datetime import date
from decimal import Decimal


@asynccontextmanager
async def lifespan(app:FastAPI):
    create_tables()
    yield

app = FastAPI(
    title= APP_TITLE,
    lifespan=lifespan)

@app.get("/")
def read_root():
    return {"app_title": APP_TITLE}

@app.get("/health")
def get_health():
    return {"status": "healthy"}

@app.post("/transactions")
def insert_transaction(transaction: TransactionCreate):
    new_id = add_transaction(amount=transaction.amount,category=transaction.category,description=transaction.description,transaction_date=transaction.transaction_date)
    return {
        "new_id": new_id,
        "added": transaction
    }
    