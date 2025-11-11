"""
Gestor de Base de Datos - VERSIÓN COMPLETA
Archivo: src/data/database.py
"""

from sqlalchemy import create_engine, func, extract
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import List, Optional, Dict
import os

from src.data.models import Base, Category, Transaction, MonthlyBudget


class DatabaseManager:
    """Gestor principal de la base de datos"""

    def __init__(self, db_path: str = "termowallet.db"):
        """Inicializa la conexión a la base de datos"""
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # Inicializar categorías por defecto si es primera vez
        self._initialize_default_categories()

    def _initialize_default_categories(self):
        """Crea categorías predeterminadas si no existen"""
        if self.session.query(Category).count() == 0:
            default_categories = [
                # Categorías de Gastos
                Category(
                    name="Alimentación",
                    icon="🍔",
                    color="#ef4444",
                    category_type="expense",
                    is_default=True,
                    description="Comida, restaurantes, supermercado",
                ),
                Category(
                    name="Transporte",
                    icon="🚗",
                    color="#f97316",
                    category_type="expense",
                    is_default=True,
                    description="Uber, gasolina, taxi, bus",
                ),
                Category(
                    name="Entretenimiento",
                    icon="🎮",
                    color="#a855f7",
                    category_type="expense",
                    is_default=True,
                    description="Cine, streaming, juegos",
                ),
                Category(
                    name="Servicios",
                    icon="💡",
                    color="#eab308",
                    category_type="expense",
                    is_default=True,
                    description="Luz, agua, internet, teléfono",
                ),
                Category(
                    name="Salud",
                    icon="⚕️",
                    color="#22c55e",
                    category_type="expense",
                    is_default=True,
                    description="Farmacia, doctor, clínica",
                ),
                Category(
                    name="Educación",
                    icon="📚",
                    color="#3b82f6",
                    category_type="expense",
                    is_default=True,
                    description="Cursos, libros, universidad",
                ),
                Category(
                    name="Vivienda",
                    icon="🏠",
                    color="#84cc16",
                    category_type="expense",
                    is_default=True,
                    description="Alquiler, reparaciones, mantenimiento",
                ),
                Category(
                    name="Compras",
                    icon="🛍️",
                    color="#ec4899",
                    category_type="expense",
                    is_default=True,
                    description="Ropa, zapatos, accesorios",
                ),
                Category(
                    name="Otros Gastos",
                    icon="💸",
                    color="#6b7280",
                    category_type="expense",
                    is_default=True,
                    description="Gastos varios",
                ),
                # Categorías de Ingresos
                Category(
                    name="Salario",
                    icon="💰",
                    color="#10b981",
                    category_type="income",
                    is_default=True,
                    description="Sueldo mensual",
                ),
                Category(
                    name="Freelance",
                    icon="💼",
                    color="#06b6d4",
                    category_type="income",
                    is_default=True,
                    description="Trabajos independientes",
                ),
                Category(
                    name="Inversiones",
                    icon="📈",
                    color="#8b5cf6",
                    category_type="income",
                    is_default=True,
                    description="Dividendos, intereses",
                ),
                Category(
                    name="Otros Ingresos",
                    icon="💵",
                    color="#14b8a6",
                    category_type="income",
                    is_default=True,
                    description="Ingresos varios",
                ),
            ]

            self.session.add_all(default_categories)
            self.session.commit()

    # ========== TRANSACCIONES ==========

    def add_transaction(
        self,
        date: datetime,
        description: str,
        amount: float,
        category_id: int,
        transaction_type: str,
        notes: Optional[str] = None,
        source: str = "manual",
        original_description: Optional[str] = None,
    ) -> Transaction:
        """Añade una nueva transacción"""
        transaction = Transaction(
            date=date,
            description=description,
            amount=amount,
            category_id=category_id,
            transaction_type=transaction_type,
            notes=notes,
            source=source,
            original_description=original_description,
        )

        self.session.add(transaction)
        self.session.commit()
        return transaction

    def add_transactions_bulk(self, transactions_data: List[Dict]) -> int:
        """Añade múltiples transacciones de una vez"""
        count = 0
        for data in transactions_data:
            try:
                self.add_transaction(**data)
                count += 1
            except Exception as e:
                print(f"Error al añadir transacción: {e}")
                continue

        return count

    def get_all_transactions(self) -> List[Transaction]:
        """Obtiene todas las transacciones ordenadas por fecha descendente"""
        return self.session.query(Transaction).order_by(Transaction.date.desc()).all()

    def get_transactions_by_month(self, year: int, month: int) -> List[Transaction]:
        """Obtiene transacciones de un mes específico"""
        return (
            self.session.query(Transaction)
            .filter(
                extract("year", Transaction.date) == year,
                extract("month", Transaction.date) == month,
            )
            .order_by(Transaction.date.desc())
            .all()
        )

    def get_transactions_by_type(
        self,
        transaction_type: str,
        year: Optional[int] = None,
        month: Optional[int] = None,
    ) -> List[Transaction]:
        """Obtiene transacciones por tipo (expense/income)"""
        query = self.session.query(Transaction).filter(
            Transaction.transaction_type == transaction_type
        )

        if year and month:
            query = query.filter(
                extract("year", Transaction.date) == year,
                extract("month", Transaction.date) == month,
            )

        return query.order_by(Transaction.date.desc()).all()

    def delete_transaction(self, transaction_id: int) -> bool:
        """Elimina una transacción"""
        transaction = (
            self.session.query(Transaction)
            .filter(Transaction.id == transaction_id)
            .first()
        )

        if transaction:
            self.session.delete(transaction)
            self.session.commit()
            return True
        return False

    def update_transaction(
        self, transaction_id: int, **kwargs
    ) -> Optional[Transaction]:
        """Actualiza una transacción"""
        transaction = (
            self.session.query(Transaction)
            .filter(Transaction.id == transaction_id)
            .first()
        )

        if transaction:
            for key, value in kwargs.items():
                if hasattr(transaction, key):
                    setattr(transaction, key, value)

            setattr(transaction, "updated_at", datetime.now())
            self.session.commit()
            return transaction
        return None

    # ========== CATEGORÍAS ==========

    def get_all_categories(self, category_type: Optional[str] = None) -> List[Category]:
        """Obtiene todas las categorías, opcionalmente filtradas por tipo"""
        query = self.session.query(Category)

        if category_type:
            query = query.filter(Category.category_type == category_type)

        return query.order_by(Category.name).all()

    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Obtiene una categoría por ID"""
        return self.session.query(Category).filter(Category.id == category_id).first()

    def get_category_by_name(
        self, name: str, category_type: str = "expense"
    ) -> Optional[Category]:
        """Obtiene una categoría por nombre"""
        return (
            self.session.query(Category)
            .filter(Category.name == name, Category.category_type == category_type)
            .first()
        )

    def add_category(
        self,
        name: str,
        icon: str,
        color: str,
        category_type: str = "expense",
        description: Optional[str] = None,
    ) -> Category:
        """Añade una nueva categoría"""
        category = Category(
            name=name,
            icon=icon,
            color=color,
            category_type=category_type,
            description=description,
            is_default=False,
        )

        self.session.add(category)
        self.session.commit()
        return category

    def update_category(self, category_id: int, **kwargs) -> Optional[Category]:
        """Actualiza una categoría y deja que el modelo maneje updated_at"""

        category = self.get_category_by_id(category_id)

        if category:
            # 1. Aplicar las actualizaciones dinámicas
            for key, value in kwargs.items():
                if hasattr(category, key):
                    setattr(category, key, value)

            # LÍNEA ELIMINADA: Ya no se necesita asignar updated_at
            # category.updated_at = datetime.now()

            # 2. El commit() activa el onupdate=datetime.now en el modelo Category
            self.session.commit()
            return category

        return None

    def delete_category(self, category_id: int) -> bool:
        """Elimina una categoría (solo si no es predeterminada)"""
        category = self.get_category_by_id(category_id)

        if category and category.is_default is False:
            self.session.delete(category)
            self.session.commit()
            return True
        return False

    # ========== ANÁLISIS Y REPORTES ==========

    def get_monthly_summary(self, year: int, month: int) -> Dict:
        """Obtiene resumen financiero del mes"""
        # Ingresos totales
        total_income = (
            self.session.query(func.sum(Transaction.amount))
            .filter(
                Transaction.transaction_type == "income",
                extract("year", Transaction.date) == year,
                extract("month", Transaction.date) == month,
            )
            .scalar()
            or 0.0
        )

        # Gastos totales
        total_expenses = (
            self.session.query(func.sum(Transaction.amount))
            .filter(
                Transaction.transaction_type == "expense",
                extract("year", Transaction.date) == year,
                extract("month", Transaction.date) == month,
            )
            .scalar()
            or 0.0
        )

        # Cálculos
        savings = total_income - total_expenses
        savings_rate = (savings / total_income * 100) if total_income > 0 else 0

        return {
            "year": year,
            "month": month,
            "month_name": datetime(year, month, 1).strftime("%B"),
            "total_income": total_income,
            "total_expenses": total_expenses,
            "savings": savings,
            "savings_rate": savings_rate,
            "transaction_count": self.session.query(Transaction)
            .filter(
                extract("year", Transaction.date) == year,
                extract("month", Transaction.date) == month,
            )
            .count(),
        }

    def get_expenses_by_category(self, year: int, month: int) -> List[Dict]:
        """Obtiene gastos agrupados por categoría"""
        results = (
            self.session.query(
                Category.name,
                Category.icon,
                Category.color,
                func.sum(Transaction.amount).label("total"),
            )
            .join(Transaction)
            .filter(
                Transaction.transaction_type == "expense",
                extract("year", Transaction.date) == year,
                extract("month", Transaction.date) == month,
            )
            .group_by(Category.id)
            .order_by(func.sum(Transaction.amount).desc())
            .all()
        )

        return [
            {
                "category": r.name,
                "icon": r.icon,
                "color": r.color,
                "total": float(r.total),
            }
            for r in results
        ]

    def get_income_by_category(self, year: int, month: int) -> List[Dict]:
        """Obtiene ingresos agrupados por categoría"""
        results = (
            self.session.query(
                Category.name,
                Category.icon,
                Category.color,
                func.sum(Transaction.amount).label("total"),
            )
            .join(Transaction)
            .filter(
                Transaction.transaction_type == "income",
                extract("year", Transaction.date) == year,
                extract("month", Transaction.date) == month,
            )
            .group_by(Category.id)
            .order_by(func.sum(Transaction.amount).desc())
            .all()
        )

        return [
            {
                "category": r.name,
                "icon": r.icon,
                "color": r.color,
                "total": float(r.total),
            }
            for r in results
        ]

    def get_monthly_trend(self, months: int = 6) -> List[Dict]:
        """Obtiene tendencia de ingresos/gastos de los últimos N meses"""
        # Esta es una implementación simplificada
        # En producción, usarías una consulta más sofisticada
        results = []
        current_date = datetime.now()

        for i in range(months):
            year = current_date.year
            month = current_date.month - i

            if month <= 0:
                month += 12
                year -= 1

            summary = self.get_monthly_summary(year, month)
            results.append(summary)

        return list(reversed(results))

    def close(self):
        """Cierra la conexión a la base de datos"""
        self.session.close()
