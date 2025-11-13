"""
Gestor de Base de Datos - VERSIÓN COMPLETA CON LIMPIEZA
Archivo: src/data/database.py
"""

from sqlalchemy import create_engine, func, extract
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import List, Optional, Dict
import os
import sys

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.data.models import Base, Category, Transaction, MonthlyBudget
from src.utils.config import Config


class DatabaseManager:
    """Gestor principal de la base de datos"""

    def __init__(self, db_path: Optional[str] = None):
        """Inicializa la conexión a la base de datos"""
        self.db_path = db_path or Config.get_db_path()
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

    # ========== LIMPIEZA DE BASE DE DATOS ==========

    def clear_all_transactions(self) -> bool:
        """Elimina TODAS las transacciones de la base de datos"""
        try:
            self.session.query(Transaction).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error al limpiar transacciones: {e}")
            return False

    def clear_custom_categories(self) -> bool:
        """Elimina SOLO las categorías personalizadas (mantiene las predeterminadas)"""
        try:
            self.session.query(Category).filter(Category.is_default == False).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error al limpiar categorías personalizadas: {e}")
            return False

    def reset_database(self) -> bool:
        """Resetea completamente la base de datos (transacciones + categorías personalizadas)"""
        try:
            # Eliminar transacciones
            self.session.query(Transaction).delete()
            # Eliminar categorías personalizadas
            self.session.query(Category).filter(Category.is_default == False).delete()
            # Eliminar presupuestos
            self.session.query(MonthlyBudget).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error al resetear base de datos: {e}")
            return False

    def get_database_stats(self) -> Dict:
        """Obtiene estadísticas de la base de datos"""
        try:
            return {
                "total_transactions": self.session.query(Transaction).count(),
                "total_categories": self.session.query(Category).count(),
                "custom_categories": self.session.query(Category)
                .filter(Category.is_default == False)
                .count(),
                "default_categories": self.session.query(Category)
                .filter(Category.is_default == True)
                .count(),
                "total_expenses": self.session.query(func.sum(Transaction.amount))
                .filter(Transaction.transaction_type == "expense")
                .scalar()
                or 0.0,
                "total_income": self.session.query(func.sum(Transaction.amount))
                .filter(Transaction.transaction_type == "income")
                .scalar()
                or 0.0,
            }
        except Exception as e:
            print(f"Error al obtener estadísticas: {e}")
            return {}

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
        """Actualiza una categoría"""
        category = self.get_category_by_id(category_id)

        if category:
            for key, value in kwargs.items():
                if hasattr(category, key):
                    setattr(category, key, value)

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

    """
    NUEVOS MÉTODOS PARA AGREGAR A: src/data/database.py
    Agregar estos métodos dentro de la clase DatabaseManager, 
    justo antes del método close() al final del archivo
    """

    def get_top_expenses(self, year: int, month: int, limit: int = 5) -> List[Dict]:
        """Obtiene los gastos más grandes del mes"""
        results = (
            self.session.query(Transaction, Category)
            .join(Category)
            .filter(
                Transaction.transaction_type == "expense",
                extract("year", Transaction.date) == year,
                extract("month", Transaction.date) == month,
            )
            .order_by(Transaction.amount.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "description": t.description,
                "amount": float(t.amount),
                "date": t.date,
                "category_name": c.name,
                "category_icon": c.icon,
                "category_color": c.color,
            }
            for t, c in results
        ]

    def get_daily_average(self, year: int, month: int) -> Dict:
        """Calcula el promedio de gasto diario del mes"""
        from calendar import monthrange

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

        # Obtener días del mes
        days_in_month = monthrange(year, month)[1]

        # Obtener día actual si es el mes actual
        now = datetime.now()
        if year == now.year and month == now.month:
            days_passed = now.day
        else:
            days_passed = days_in_month

        daily_avg = total_expenses / days_passed if days_passed > 0 else 0
        projected_total = daily_avg * days_in_month

        return {
            "total_expenses": total_expenses,
            "days_passed": days_passed,
            "days_in_month": days_in_month,
            "daily_average": daily_avg,
            "projected_monthly": projected_total,
        }

    def get_week_comparison(self, year: int, month: int) -> Dict:
        """Compara el gasto de esta semana con la semana pasada"""
        from datetime import timedelta

        now = datetime.now()

        # Semana actual (últimos 7 días)
        week_start = now - timedelta(days=7)
        current_week_total = (
            self.session.query(func.sum(Transaction.amount))
            .filter(
                Transaction.transaction_type == "expense",
                Transaction.date >= week_start,
                Transaction.date <= now,
            )
            .scalar()
            or 0.0
        )

        # Semana anterior (días 8-14 atrás)
        prev_week_start = now - timedelta(days=14)
        prev_week_end = now - timedelta(days=7)
        previous_week_total = (
            self.session.query(func.sum(Transaction.amount))
            .filter(
                Transaction.transaction_type == "expense",
                Transaction.date >= prev_week_start,
                Transaction.date < prev_week_end,
            )
            .scalar()
            or 0.0
        )

        # Calcular cambio porcentual
        if previous_week_total > 0:
            change_pct = (
                (current_week_total - previous_week_total) / previous_week_total
            ) * 100
        else:
            change_pct = 0 if current_week_total == 0 else 100

        return {
            "current_week": current_week_total,
            "previous_week": previous_week_total,
            "change_amount": current_week_total - previous_week_total,
            "change_percentage": change_pct,
            "is_increasing": current_week_total > previous_week_total,
        }

    def get_category_budget_status(self, year: int, month: int) -> List[Dict]:
        """Obtiene el estado de gasto por categoría con límites sugeridos"""
        expenses = self.get_expenses_by_category(year, month)

        # Límites sugeridos por categoría (% del total)
        suggested_limits = {
            "Alimentación": 30,
            "Transporte": 15,
            "Vivienda": 30,
            "Entretenimiento": 10,
            "Servicios": 10,
            "Salud": 5,
            "Educación": 10,
            "Compras": 15,
            "Otros Gastos": 5,
        }

        if not expenses:
            return []

        total = sum(e["total"] for e in expenses)

        result = []
        for expense in expenses:
            cat_name = expense["category"]
            suggested_pct = suggested_limits.get(cat_name, 10)
            suggested_amount = total * (suggested_pct / 100)
            actual_pct = (expense["total"] / total * 100) if total > 0 else 0

            result.append(
                {
                    "category": cat_name,
                    "icon": expense["icon"],
                    "color": expense["color"],
                    "spent": expense["total"],
                    "suggested_limit": suggested_amount,
                    "percentage": actual_pct,
                    "suggested_percentage": suggested_pct,
                    "is_over_budget": actual_pct
                    > (suggested_pct * 1.1),  # 10% de margen
                    "budget_health": (
                        "good"
                        if actual_pct <= suggested_pct
                        else (
                            "warning" if actual_pct <= suggested_pct * 1.2 else "danger"
                        )
                    ),
                }
            )

        return result

    def get_spending_trend_last_days(self, days: int = 7) -> List[Dict]:
        """Obtiene el gasto de los últimos N días para graficar tendencia"""
        from datetime import timedelta

        now = datetime.now()
        results = []

        for i in range(days):
            target_date = now - timedelta(days=days - i - 1)

            daily_total = (
                self.session.query(func.sum(Transaction.amount))
                .filter(
                    Transaction.transaction_type == "expense",
                    func.date(Transaction.date) == target_date.date(),
                )
                .scalar()
                or 0.0
            )

            results.append(
                {
                    "date": target_date.date(),
                    "day_name": target_date.strftime("%a"),
                    "amount": float(daily_total),
                }
            )

        return results

    def get_transaction_count_by_type(self, year: int, month: int) -> Dict:
        """Obtiene el conteo de transacciones por tipo"""
        expense_count = (
            self.session.query(func.count(Transaction.id))
            .filter(
                Transaction.transaction_type == "expense",
                extract("year", Transaction.date) == year,
                extract("month", Transaction.date) == month,
            )
            .scalar()
            or 0
        )

        income_count = (
            self.session.query(func.count(Transaction.id))
            .filter(
                Transaction.transaction_type == "income",
                extract("year", Transaction.date) == year,
                extract("month", Transaction.date) == month,
            )
            .scalar()
            or 0
        )

        return {
            "total": expense_count + income_count,
            "expenses": expense_count,
            "income": income_count,
        }

    def close(self):
        """Cierra la conexión a la base de datos"""
        self.session.close()
