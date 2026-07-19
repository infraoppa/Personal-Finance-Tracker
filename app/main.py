from app.config import APP_TITLE, BASE_DIR
from app.database import create_tables
from app.transaction import add_transaction, get_transaction, get_transactions, update_transaction, delete_transaction
from app.schemas import TransactionCreate
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from datetime import date
from decimal import Decimal


templates = Jinja2Templates(
    directory=BASE_DIR/"app"/"templates"
)

@asynccontextmanager
async def lifespan(app:FastAPI):
    create_tables()
    yield

app = FastAPI(
    title= APP_TITLE,
    lifespan=lifespan)

@app.get("/")
def read_root():
    return {"app_title": APP_TITLE}

@app.get("/health")
def get_health():
    return {"status": "healthy"}

@app.post("/transactions")
def insert_transaction(transaction: TransactionCreate):
    new_id = add_transaction(amount=transaction.amount,category=transaction.category,description=transaction.description,transaction_date=transaction.transaction_date)
    return {
        "new_id": new_id,
        "added": transaction
    }

@app.get("/transactions")
def get_all_transactions():
    transactions = get_transactions()
    return transactions
    
@app.get("/transactions/{transaction_id}")
def get_transaction_by_id(transaction_id:int):
    transaction = get_transaction(transaction_id)
    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction Not Found"
        )
    return {"transaction": transaction}

@app.put("/transactions/{transaction_id}")
def update_transaction_by_id(transaction_id:int, transaction: TransactionCreate):
    updated = update_transaction(transaction_id,transaction.amount,transaction.category,transaction.description,transaction.transaction_date)
    if not updated:
        raise HTTPException(
            status_code= 404,
            detail="Transaction not found"
        )
    return {"updated": get_transaction(transaction_id)}


@app.delete("/transactions/{transaction_id}")
def delete_transaction_by_id(transaction_id:int):
    transaction = get_transaction(transaction_id)
    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )
    deleted = delete_transaction(transaction_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )
    return {"deleted":transaction}

@app.get("/dashboard",response_class=HTMLResponse)
def get_dashboard(request:Request):
    transactions = get_transactions()
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
    transaction_date: date = Form(...)
):
    add_transaction(amount=amount,category=category,description=description,transaction_date=transaction_date)
    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )

@app.post("/transactions/{transaction_id}/delete")
def delete_form_transaction(transaction_id: int):
    deleted = delete_transaction(transaction_id)

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
def edit_transaction_form(transaction_id:int,request:Request):
    transaction = get_transaction(transaction_id)
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
