"""
Modelos de Base de Datos usando SQLAlchemy 2.0 - CON PALABRAS CLAVE
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
    Text,  # ✅ NUEVO: Para almacenar keywords como JSON/texto
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import UniqueConstraint

class Base(DeclarativeBase):
    pass


class Category(Base):
    """Modelo de Categorías - Para Gastos e Ingresos CON PALABRAS CLAVE"""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(255), default=None)
    color: Mapped[str] = mapped_column(String(7), default="#3b82f6")
    icon: Mapped[str] = mapped_column(String(50), default="💰")
    category_type: Mapped[str] = mapped_column(String(20), default="expense")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # ✅ NUEVO: Palabras clave para categorización automática
    keywords: Mapped[Optional[str]] = mapped_column(Text, default=None)
    # Se almacenan como JSON string: '["palabra1", "palabra2", "palabra3"]'
    
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
    
    # ✅ NUEVO: Métodos helper para manejar keywords
    def get_keywords_list(self) -> List[str]:
        """Retorna las palabras clave como lista"""
        if not self.keywords:
            return []
        try:
            import json
            return json.loads(self.keywords)
        except:
            return []
    
    def set_keywords_list(self, keywords_list: List[str]):
        """Establece las palabras clave desde una lista"""
        import json
        # Limpiar y convertir a minúsculas
        clean_keywords = [k.lower().strip() for k in keywords_list if k.strip()]
        self.keywords = json.dumps(clean_keywords, ensure_ascii=False)


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
    
    
    
    
    
class CategoryBudget(Base):
    """
    Modelo para distribución porcentual del presupuesto por categoría
    
    Permite asignar un porcentaje del presupuesto mensual a cada categoría.
    La suma de todos los porcentajes debe ser 100%.
    """
    
    __tablename__ = "category_budgets"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    year: Mapped[int] = mapped_column(Integer, index=True)
    month: Mapped[int] = mapped_column(Integer, index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    
    # Porcentaje asignado (0-100)
    percentage: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Monto sugerido (calculado automáticamente)
    suggested_amount: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    
    # Notas específicas para esta categoría en este mes
    notes: Mapped[Optional[str]] = mapped_column(String(500), default=None)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )
    
    # Relación con categoría
    category: Mapped["Category"] = relationship("Category")
    
    # Constraint: Una categoría solo puede tener un porcentaje por mes
    __table_args__ = (
        UniqueConstraint('year', 'month', 'category_id', name='unique_category_month'),
    )
    
    def __repr__(self):
        return f"<CategoryBudget(year={self.year}, month={self.month}, category_id={self.category_id}, percentage={self.percentage}%)>"
