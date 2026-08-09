from datetime import date,datetime
from decimal import Decimal
from pydantic import BaseModel,ConfigDict

class TransactionCreate(BaseModel):
    amount: Decimal
    category: str
    description: str
    transaction_date: date

class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:int
    amount:Decimal
    category:str
    description:str
    transaction_date:date
    created_at:datetime