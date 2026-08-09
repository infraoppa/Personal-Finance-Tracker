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

class BudgetCreate(BaseModel):
    category:str
    amount:Decimal
    month:int
    year:int
    alert_theshold:int

class BudgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:int
    category:str
    amount:Decimal
    month:int
    year:int
    alert_threshold:int
    created_at:datetime