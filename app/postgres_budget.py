from app.models import Budget,Transaction
from sqlalchemy.orm import Session
from sqlalchemy import select,func,extract
from decimal import Decimal

def create_budget(db:Session,category:str,amount:Decimal,month:int,year:int,alert_threshold:int):
    budget = Budget(category=category,amount=amount,month=month,year=year,alert_threshold=alert_threshold)
    try:
        db.add(budget)
        db.commit()
        db.refresh(budget)
        return budget
    except Exception:
        db.rollback()
        raise

def select_budgets(db:Session):
    x = select(Budget).order_by(Budget.year.desc(),Budget.month.desc())
    budgets = db.scalars(x).all()
    return budgets

def get_category_spending(db:Session,category:str,month:int,year:int):
    statement = select(func.sum(Transaction.amount)).where(
        func.lower(Transaction.category) == category.lower(),
        extract("month",Transaction.transaction_date)==month,
        extract("year",Transaction.transaction_date)==year)
    spent = db.scalar(statement)
    if spent is None:
        spent = Decimal("0.00")
    return spent

def get_budget_status(db: Session,category: str,month: int,year: int):
    statement = select(Budget).where(
        func.lower(Budget.category) == category.lower(),
        Budget.month == month,
        Budget.year == year
    )
    budget = db.scalar(statement)
    if budget is None:
        return None
    spent = get_category_spending(db=db,category=budget.category,month=budget.month,year=budget.year)
    remaining = budget.amount - spent
    if budget.amount == 0:
        percentage_used = Decimal("0.00")
    else:
        percentage_used = (
            spent / budget.amount
        ) * Decimal("100")
    threshold_reached = (
        percentage_used >= budget.alert_threshold
    )
    return {
        "category": budget.category,
        "budget": budget.amount,
        "spent": spent,
        "remaining": remaining,
        "percentage_used": percentage_used,
        "alert_threshold": budget.alert_threshold,
        "threshold_reached": threshold_reached
    }

def update_budget(
    db: Session,
    budget_id: int,
    category: str,
    amount: Decimal,
    month: int,
    year: int,
    alert_threshold: int
):
    budget = db.get(Budget, budget_id)

    if budget is None:
        return None

    try:
        budget.category = category
        budget.amount = amount
        budget.month = month
        budget.year = year
        budget.alert_threshold = alert_threshold

        db.commit()
        db.refresh(budget)

        return budget

    except Exception:
        db.rollback()
        raise


def delete_budget(
    db: Session,
    budget_id: int
):
    budget = db.get(Budget, budget_id)

    if budget is None:
        return None

    try:
        db.delete(budget)
        db.commit()
        return budget

    except Exception:
        db.rollback()
        raise