"""
Modelos de Base de Datos usando SQLAlchemy 2.0 - con tipado estático
Archivo: src/data/models.py
"""

import os
import sys

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Boolean,
    Column,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Category(Base):
    """Modelo de Categorías - Para Gastos e Ingresos"""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(255), default=None)
    color: Mapped[str] = mapped_column(String(7), default="#3b82f6")
    icon: Mapped[str] = mapped_column(String(50), default="💰")
    category_type: Mapped[str] = mapped_column(String(20), default="expense")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    # Relación
    transactions: Mapped[List["Transaction"]] = relationship(
        back_populates="category", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Category(name='{self.name}', type='{self.category_type}')>"


class Transaction(Base):
    """Modelo de Transacciones - Gastos e Ingresos"""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(DateTime, index=True)
    description: Mapped[str] = mapped_column(String(255))
    amount: Mapped[float] = mapped_column(Float)
    transaction_type: Mapped[str] = mapped_column(String(20), index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    notes: Mapped[Optional[str]] = mapped_column(String(500), default=None)
    source: Mapped[str] = mapped_column(String(50), default="manual")
    original_description: Mapped[Optional[str]] = mapped_column(
        String(255), default=None
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    # Relación
    category: Mapped["Category"] = relationship(back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(date='{self.date}', type='{self.transaction_type}', amount={self.amount})>"


class MonthlyBudget(Base):
    """Modelo para presupuestos y metas de ahorro mensuales"""

    __tablename__ = "monthly_budgets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    year: Mapped[int] = mapped_column(Integer)
    month: Mapped[int] = mapped_column(Integer)
    income_goal: Mapped[float] = mapped_column(Float, default=0.0)
    expense_limit: Mapped[float] = mapped_column(Float, default=0.0)
    savings_goal: Mapped[float] = mapped_column(Float, default=0.0)
    notes: Mapped[Optional[str]] = mapped_column(String(500), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    def __repr__(self):
        return f"<MonthlyBudget(year={self.year}, month={self.month})>"
