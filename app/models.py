from datetime import date,datetime
from decimal import Decimal
from sqlalchemy import Date,DateTime,Numeric,String,func
from sqlalchemy.orm import Mapped,mapped_column
from app.postgres_database import Base

class Transaction(Base):
    __tablename__="transactions"

    id: Mapped[int] = mapped_column(primary_key=True)

    amount:Mapped[Decimal] = mapped_column(
        Numeric(10,2),
        nullable=False   
    )

    category:Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    description:Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    transaction_date:Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    created_at:Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False   
    )

class Budget(Base):

    __tablename__ = "budget"

    id:Mapped[int] = mapped_column(
        primary_key=True
    )
    category:Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    amount:Mapped[Decimal] = mapped_column(
        Numeric(10,2),
        nullable=False
    )
    month:Mapped[int] = mapped_column(
        nullable=False
    )
    year:Mapped[int] = mapped_column(
        nullable=False
    )

    alert_threshold:Mapped[int] = mapped_column(
        nullable=False
    )

    created_on:Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )