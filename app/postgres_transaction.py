from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models import Transaction


def create_transaction(db:Session,amount:Decimal,category:str,description:str,transaction_date:date):
    transaction = Transaction(amount=amount,category=category,description=description,transaction_date=transaction_date)
    try:
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction
    
    except Exception:
        db.rollback()
        raise 

