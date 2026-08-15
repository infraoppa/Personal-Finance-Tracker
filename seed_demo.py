"""Seed (or remove) demo data for the dashboard.

    python seed_demo.py           # insert the demo rows
    python seed_demo.py --clear   # remove them again

Spending is matched to a budget by category + the month/year of
transaction_date (see get_category_spending), so every row here is
dated inside DEMO_MONTH/DEMO_YEAR.

The data deliberately covers all three budget states so the
dashboard has something to show in each:

    Food, Transport  -> on track
    Shopping         -> past its alert threshold, under 100%
    Rent             -> over budget

--clear only removes rows matching these exact descriptions (and
budgets for these categories in the demo month), so it will not
touch transactions you have entered yourself. The one exception:
if you create your own budget for one of these four categories in
the demo month, --clear will remove that too.
"""

import sys
from datetime import date
from decimal import Decimal

from sqlalchemy import extract, func

from app.models import Budget, Transaction
from app.postgres_database import get_db

DEMO_YEAR = 2026
DEMO_MONTH = 8

# (category, amount, alert_threshold)
BUDGETS = [
    ("Food", "600.00", 80),
    ("Rent", "1800.00", 90),
    ("Transport", "150.00", 80),
    ("Shopping", "550.00", 85),
]

# (day, amount, category, description)
TRANSACTIONS = [
    (1, "1899.99", "Rent", "August rent"),
    (2, "321.10", "Food", "Big grocery run"),
    (3, "64.20", "Transport", "Monthly transit pass"),
    (4, "380.01", "Shopping", "Winter coat"),
    (6, "129.99", "Shopping", "Running shoes"),
    (7, "86.40", "Food", "Weekly groceries"),
    (9, "12.50", "Food", "Lunch at the deli"),
]

DESCRIPTIONS = [t[3] for t in TRANSACTIONS]
CATEGORIES = [b[0] for b in BUDGETS]


def clear(db):
    txns = db.query(Transaction).filter(
        Transaction.description.in_(DESCRIPTIONS),
        extract("month", Transaction.transaction_date) == DEMO_MONTH,
        extract("year", Transaction.transaction_date) == DEMO_YEAR,
    ).all()

    budgets = db.query(Budget).filter(
        func.lower(Budget.category).in_([c.lower() for c in CATEGORIES]),
        Budget.month == DEMO_MONTH,
        Budget.year == DEMO_YEAR,
    ).all()

    for row in txns + budgets:
        db.delete(row)

    db.commit()

    return len(txns), len(budgets)


def seed(db):
    existing = db.query(Budget).filter(
        func.lower(Budget.category).in_([c.lower() for c in CATEGORIES]),
        Budget.month == DEMO_MONTH,
        Budget.year == DEMO_YEAR,
    ).count()

    if existing:
        print(
            f"Demo budgets already present ({existing}). "
            "Run with --clear first to reseed."
        )
        return 0, 0

    for category, amount, threshold in BUDGETS:
        db.add(Budget(
            category=category,
            amount=Decimal(amount),
            month=DEMO_MONTH,
            year=DEMO_YEAR,
            alert_threshold=threshold,
        ))

    for day, amount, category, description in TRANSACTIONS:
        db.add(Transaction(
            amount=Decimal(amount),
            category=category,
            description=description,
            transaction_date=date(DEMO_YEAR, DEMO_MONTH, day),
        ))

    db.commit()

    return len(TRANSACTIONS), len(BUDGETS)


def main():
    db = next(get_db())

    if "--clear" in sys.argv:
        txns, budgets = clear(db)
        print(f"Removed {budgets} budget(s) and {txns} transaction(s).")
    else:
        txns, budgets = seed(db)
        if txns or budgets:
            print(f"Added {budgets} budget(s) and {txns} transaction(s).")


if __name__ == "__main__":
    main()
