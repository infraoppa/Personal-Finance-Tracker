from datetime import date
from decimal import Decimal
from app.models import Transaction
from app.postgres_database import SessionLocal

db = SessionLocal()

try:
    transaction = Transaction(
        amount=Decimal("25.50"),
        category="Food",
        description="Lunch",
        transaction_date=date.today()
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    print(f"Created transaction with ID: {transaction.id}")

except Exception:
    db.rollback()
    raise

finally:
    db.close()