from datetime import date
from decimal import Decimal

from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    Form,
    Depends,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.config import APP_TITLE, BASE_DIR

from app.schemas import (
    TransactionCreate,
    TransactionResponse,
    BudgetCreate,
    BudgetResponse,
    BudgetStatusResponse,
)

from app.models import Budget

from app.postgres_database import get_db

from app.postgres_transaction import (
    post_transaction,
    select_transactions,
    select_transactions_by_id,
    update_trans,
    delete_trans,
)

from app.postgres_budget import (
    create_budget,
    select_budgets,
    get_category_spending,
    get_budget_status,
    update_budget,
    delete_budget,
)


# =========================================================
# FASTAPI SETUP
# =========================================================

templates = Jinja2Templates(
    directory=BASE_DIR / "app" / "templates"
)


def _currency(value) -> str:
    """Render a money value as $1,234.56 for the templates.

    Negatives render as -$50.00 rather than $-50.00.
    """
    amount = Decimal(value or 0)
    sign = "-" if amount < 0 else ""

    return f"{sign}${abs(amount):,.2f}"


templates.env.filters["currency"] = _currency


def _static_version() -> str:
    """Modification time of the stylesheet, in seconds.

    Appended to the stylesheet URL as ?v=... so the browser
    fetches a fresh copy whenever the file changes. Without it
    a cached copy can survive edits - uvicorn --reload restarts
    on .py changes but not on .css ones, so the stale sheet is
    served against freshly rendered markup.

    Called per request rather than at import so edits are picked
    up without a restart.
    """
    stylesheet = BASE_DIR / "app" / "static" / "styles.css"

    try:
        return str(int(stylesheet.stat().st_mtime))
    except OSError:
        return "0"


templates.env.globals["static_version"] = _static_version

app = FastAPI(
    title=APP_TITLE
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "app" / "static"),
    name="static"
)


# =========================================================
# BASIC ROUTES
# =========================================================

@app.get("/")
def read_root():
    return {
        "app_title": APP_TITLE
    }


@app.get("/health")
def get_health():
    return {
        "status": "healthy"
    }


# =========================================================
# TRANSACTION API
# =========================================================

@app.post(
    "/transactions",
    response_model=TransactionResponse
)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    created = post_transaction(
        db=db,
        amount=transaction.amount,
        description=transaction.description,
        category=transaction.category,
        transaction_date=transaction.transaction_date
    )

    return created


@app.get(
    "/transactions",
    response_model=list[TransactionResponse]
)
def get_all_transactions(
    db: Session = Depends(get_db)
):
    transactions = select_transactions(db)

    return transactions


@app.get(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse
)
def get_transaction_by_id(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    transaction = select_transactions_by_id(
        db,
        transaction_id
    )

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return transaction


@app.put(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse
)
def update_transaction(
    transaction_id: int,
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    updated = update_trans(
        db=db,
        transaction_id=transaction_id,
        amount=transaction.amount,
        category=transaction.category,
        description=transaction.description,
        transaction_date=transaction.transaction_date
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return updated


@app.delete(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse
)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    deleted = delete_trans(
        db,
        transaction_id
    )

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return deleted


# =========================================================
# BUDGET API
# =========================================================

@app.post(
    "/budgets",
    response_model=BudgetResponse
)
def add_budget(
    budget: BudgetCreate,
    db: Session = Depends(get_db)
):
    created_budget = create_budget(
        db=db,
        category=budget.category,
        amount=budget.amount,
        month=budget.month,
        year=budget.year,
        alert_threshold=budget.alert_threshold
    )

    return created_budget


@app.get(
    "/budgets",
    response_model=list[BudgetResponse]
)
def get_budgets(
    db: Session = Depends(get_db)
):
    budgets = select_budgets(db)

    return budgets


@app.get("/budgets/spending/{category}")
def get_spent_by_category(
    category: str,
    month: int,
    year: int,
    db: Session = Depends(get_db)
):
    spent = get_category_spending(
        db=db,
        category=category,
        month=month,
        year=year
    )

    return {
        "category": category,
        "month": month,
        "year": year,
        "spent": spent
    }


@app.get(
    "/budgets/status",
    response_model=BudgetStatusResponse
)
def get_current_budget_status(
    category: str,
    month: int,
    year: int,
    db: Session = Depends(get_db)
):
    status = get_budget_status(
        db=db,
        category=category,
        month=month,
        year=year
    )

    if status is None:
        raise HTTPException(
            status_code=404,
            detail="Budget not found"
        )

    return status


@app.put(
    "/budgets/{budget_id}",
    response_model=BudgetResponse
)
def update_budget_by_id(
    budget_id: int,
    budget: BudgetCreate,
    db: Session = Depends(get_db)
):
    updated = update_budget(
        db=db,
        budget_id=budget_id,
        category=budget.category,
        amount=budget.amount,
        month=budget.month,
        year=budget.year,
        alert_threshold=budget.alert_threshold
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Budget not found"
        )

    return updated


@app.delete(
    "/budgets/{budget_id}",
    response_model=BudgetResponse
)
def delete_budget_by_id(
    budget_id: int,
    db: Session = Depends(get_db)
):
    deleted = delete_budget(
        db=db,
        budget_id=budget_id
    )

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Budget not found"
        )

    return deleted


# =========================================================
# DASHBOARD
# =========================================================

@app.get(
    "/dashboard",
    response_class=HTMLResponse
)
def get_dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    transactions = select_transactions(db)

    budgets = select_budgets(db)

    budget_statuses = []

    for budget in budgets:

        status = get_budget_status(
            db=db,
            category=budget.category,
            month=budget.month,
            year=budget.year
        )

        if status is not None:
            # Allows the HTML to use status.id
            # for edit/delete buttons.
            status["id"] = budget.id

            budget_statuses.append(status)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_title": APP_TITLE,
            "transactions": transactions,
            "budgets": budgets,
            "budget_statuses": budget_statuses
        }
    )


# =========================================================
# TRANSACTION HTML FORMS
# =========================================================

@app.post("/transactions/form")
def insert_form_transaction(
    amount: Decimal = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    transaction_date: date = Form(...),
    db: Session = Depends(get_db)
):
    post_transaction(
        db=db,
        amount=amount,
        category=category,
        description=description,
        transaction_date=transaction_date
    )

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )


@app.post("/transactions/{transaction_id}/delete")
def delete_form_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    deleted = delete_trans(
        db,
        transaction_id
    )

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )


@app.get(
    "/transactions/{transaction_id}/edit",
    response_class=HTMLResponse
)
def edit_transaction_form(
    transaction_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    transaction = select_transactions_by_id(
        db,
        transaction_id
    )

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return templates.TemplateResponse(
        request=request,
        name="edit_transaction.html",
        context={
            "app_title": APP_TITLE,
            "transaction": transaction
        }
    )


@app.post("/transactions/{transaction_id}/edit")
def post_edit_transaction_form(
    transaction_id: int,
    amount: Decimal = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    transaction_date: date = Form(...),
    db: Session = Depends(get_db)
):
    updated = update_trans(
        db=db,
        transaction_id=transaction_id,
        amount=amount,
        category=category,
        description=description,
        transaction_date=transaction_date
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )


# =========================================================
# BUDGET HTML FORMS
# =========================================================

@app.post("/budgets/form")
def insert_form_budget(
    category: str = Form(...),
    amount: Decimal = Form(...),
    month: int = Form(...),
    year: int = Form(...),
    alert_threshold: int = Form(...),
    db: Session = Depends(get_db)
):
    create_budget(
        db=db,
        category=category,
        amount=amount,
        month=month,
        year=year,
        alert_threshold=alert_threshold
    )

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )


@app.post("/budgets/{budget_id}/delete")
def delete_form_budget(
    budget_id: int,
    db: Session = Depends(get_db)
):
    deleted = delete_budget(
        db=db,
        budget_id=budget_id
    )

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Budget not found"
        )

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )


@app.get(
    "/budgets/{budget_id}/edit",
    response_class=HTMLResponse
)
def edit_budget_form(
    budget_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    budget = db.get(
        Budget,
        budget_id
    )

    if budget is None:
        raise HTTPException(
            status_code=404,
            detail="Budget not found"
        )

    return templates.TemplateResponse(
        request=request,
        name="edit_budget.html",
        context={
            "app_title": APP_TITLE,
            "budget": budget
        }
    )


@app.post("/budgets/{budget_id}/edit")
def post_edit_budget_form(
    budget_id: int,
    category: str = Form(...),
    amount: Decimal = Form(...),
    month: int = Form(...),
    year: int = Form(...),
    alert_threshold: int = Form(...),
    db: Session = Depends(get_db)
):
    updated = update_budget(
        db=db,
        budget_id=budget_id,
        category=category,
        amount=amount,
        month=month,
        year=year,
        alert_threshold=alert_threshold
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Budget not found"
        )

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )