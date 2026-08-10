from app.config import APP_TITLE, BASE_DIR
from app.schemas import TransactionCreate,TransactionResponse,BudgetCreate,BudgetResponse,BudgetStatusResponse
from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.postgres_database import get_db
from app.postgres_transaction import post_transaction,select_transactions,select_transactions_by_id,update_trans,delete_trans
from app.postgres_budget import create_budget,select_budgets,get_category_spending,get_budget_status
from datetime import date
from decimal import Decimal


templates = Jinja2Templates(
    directory=BASE_DIR/"app"/"templates"
)

app = FastAPI(
    title= APP_TITLE)

@app.get("/")
def read_root():
    return {"app_title": APP_TITLE}

@app.get("/health")
def get_health():
    return {"status": "healthy"}

## Backend Transactions

@app.post("/transactions",response_model=TransactionResponse)
def create_transaction(transaction:TransactionCreate, db:Session = Depends(get_db)):
    created = post_transaction(db=db,amount=transaction.amount,description=transaction.description,category=transaction.category,transaction_date=transaction.transaction_date)
    return created


@app.get("/transactions", response_model=list[TransactionResponse])
def get_all_transactions(db:Session=Depends(get_db)):
    transactions = select_transactions(db)
    return transactions

@app.get("/transactions/{transaction_id}",response_model=TransactionResponse)
def get_transaction_by_id(transaction_id:int,db:Session=Depends(get_db)):
    transaction = select_transactions_by_id(db,transaction_id)
    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )
    return transaction

@app.put("/transactions/{transaction_id}",response_model=TransactionResponse)
def update_transaction(transaction_id:int,transaction:TransactionCreate,db:Session=Depends(get_db)):
    updated = update_trans(db,transaction_id,amount=transaction.amount,category=transaction.category,description=transaction.description,transaction_date=transaction.transaction_date)
    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )
    return updated

@app.delete("/transactions/{transaction_id}", response_model=TransactionResponse)
def delete_transaction(transaction_id:int,db:Session=Depends(get_db)):
    deleted = delete_trans(db,transaction_id)
    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )
    return deleted

# Backend Budgets

@app.post("/budgets",response_model=BudgetResponse)
def add_budget(budget:BudgetCreate,db:Session=Depends(get_db)):
    budget = create_budget(db,category=budget.category,amount=budget.amount,month=budget.month,year=budget.year,alert_threshold=budget.alert_threshold)
    return budget

@app.get("/budgets",response_model=list[BudgetResponse])
def get_budgets(db:Session=Depends(get_db)):
    budgets = select_budgets(db)
    return budgets

@app.get("/budgets/spending/{category}")
def get_spent_by_category(category:str,month:int,year:int,db:Session=Depends(get_db)):
    spent = get_category_spending(db,category,month,year)
    return {
        "category": category,
        "month": month,
        "year": year,
        "spent": spent
    }

@app.get("/budgets/status",response_model=BudgetStatusResponse)
def get_current_budget_status(category: str,month: int,year: int,db: Session = Depends(get_db)):
    status = get_budget_status(db=db,category=category,month=month,year=year)
    if status is None:
        raise HTTPException(
            status_code=404,
            detail="Budget not found"
        )
    return status

#Front end form 

@app.get("/dashboard",response_class=HTMLResponse)
def get_dashboard(request:Request,db:Session=Depends(get_db)):
    transactions = select_transactions(db)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_title": APP_TITLE,
            "transactions": transactions
        }
    )

@app.post("/transactions/form")
def insert_form_transaction(
    amount : Decimal = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    transaction_date: date = Form(...),
    db:Session=Depends(get_db)
):
    post_transaction(db,amount=amount,category=category,description=description,transaction_date=transaction_date)
    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )

@app.post("/transactions/{transaction_id}/delete")
def delete_form_transaction(transaction_id: int, db:Session=Depends(get_db)):
    deleted = delete_trans(db,transaction_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )
    
@app.get("/transactions/{transaction_id}/edit",response_class=HTMLResponse)
def edit_transaction_form(transaction_id:int,request:Request,db:Session=Depends(get_db)):
    transaction = select_transactions_by_id(db,transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )
    return templates.TemplateResponse(
        request=request,
        name="edit_transaction.html",
        context={
            "transaction":transaction
        }
    )

@app.post("/transactions/{transaction_id}/edit")
def post_edit_transaction_form(
    transaction_id:int,
    amount:Decimal = Form(...),
    category:str = Form(...),
    description:str = Form(...),
    transaction_date:date = Form(...),
    db:Session=Depends(get_db)
):
    updated = update_trans(db,transaction_id=transaction_id,amount=amount,category=category,description=description,transaction_date=transaction_date)
    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )
    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )

