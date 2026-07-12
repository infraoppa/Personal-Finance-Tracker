from app.config import APP_TITLE
from app.database import create_tables
from fastapi import FastAPI
from contextlib import asynccontextmanager


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
