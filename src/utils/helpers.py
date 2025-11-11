"""
Funciones auxiliares y utilidades
Archivo: src/utils/helpers.py
"""

from datetime import datetime
from typing import List, Dict
import calendar


def format_currency(amount: float, symbol: str = "S/") -> str:
    """Formatea un número como moneda"""
    return f"{symbol} {amount:,.2f}"


def format_date(date: datetime, format: str = "%d/%m/%Y") -> str:
    """Formatea una fecha"""
    return date.strftime(format)


def get_month_name(month: int, locale: str = "es") -> str:
    """Retorna el nombre del mes"""
    months_es = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]

    if 1 <= month <= 12:
        return months_es[month - 1]
    return ""


def get_savings_color(savings_rate: float) -> str:
    """Retorna un color según la tasa de ahorro"""
    if savings_rate >= 30:
        return "#22c55e"  # Verde
    elif savings_rate >= 20:
        return "#3b82f6"  # Azul
    elif savings_rate >= 10:
        return "#eab308"  # Amarillo
    else:
        return "#ef4444"  # Rojo


def validate_amount(amount_str: str) -> tuple[bool, float]:
    """
    Valida y convierte un string a monto
    Returns: (is_valid, amount)
    """
    try:
        # Limpiar el string
        cleaned = amount_str.replace(",", "").replace("S/", "").strip()
        amount = float(cleaned)

        if amount <= 0:
            return False, 0.0

        return True, amount
    except:
        return False, 0.0


def get_current_month_range() -> tuple[datetime, datetime]:
    """Retorna el primer y último día del mes actual"""
    now = datetime.now()
    first_day = datetime(now.year, now.month, 1)
    last_day = datetime(
        now.year, now.month, calendar.monthrange(now.year, now.month)[1]
    )
    return first_day, last_day


def group_transactions_by_date(transactions: List) -> Dict[str, List]:
    """Agrupa transacciones por fecha"""
    grouped = {}

    for transaction in transactions:
        date_key = transaction.date.strftime("%Y-%m-%d")
        if date_key not in grouped:
            grouped[date_key] = []
        grouped[date_key].append(transaction)

    return grouped


def calculate_percentage(part: float, total: float) -> float:
    """Calcula el porcentaje"""
    if total == 0:
        return 0.0
    return (part / total) * 100


def truncate_text(text: str, max_length: int = 50) -> str:
    """Trunca un texto si es muy largo"""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
