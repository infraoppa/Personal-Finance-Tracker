from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models import Transaction
from sqlalchemy import select


def post_transaction(db:Session,amount:Decimal,category:str,description:str,transaction_date:date):
    transaction = Transaction(amount=amount,category=category,description=description,transaction_date=transaction_date)
    try:
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction
    
    except Exception:
        db.rollback()
        raise 

def select_transactions(db:Session):
    statement = select(Transaction).order_by(Transaction.id.desc(),Transaction.transaction_date.desc())
    transactions = db.scalars(statement).all()
    return transactions

def select_transactions_by_id(db:Session,transaction_id:int):
    transaction = db.get(Transaction,transaction_id)
    if transaction is None:
        return None
    return transaction

def update_trans(db:Session,transaction_id:int,amount:Decimal,category:str,description:str,transaction_date:date):
    transaction = db.get(Transaction,transaction_id)
    if transaction is None:
        return None
    try:
        transaction.amount = amount
        transaction.category = category
        transaction.description = description
        transaction.transaction_date = transaction_date

        db.commit()
        db.refresh(transaction)
        return transaction
    except Exception:
        db.rollback()
        raise

def delete_trans(db:Session,transaction_id:int):
    transaction = db.get(Transaction,transaction_id)
    if transaction is None:
        return None
    try:
        db.delete(transaction)
        db.commit()
        return transaction
    except Exception:
        db.rollback()
        raise