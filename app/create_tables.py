from app.models import Transaction,Budget
from app.postgres_database import Base,engine

Base.metadata.create_all(bind=engine)

print("Tables created sucessfully")