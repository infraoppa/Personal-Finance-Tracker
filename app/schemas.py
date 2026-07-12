from datetime import date
from decimal import Decimal
from pydantic import BaseModel

class TransactionCreate(BaseModel):
    amount: Decimal
    category: str
    description: str
    transaction_date: date