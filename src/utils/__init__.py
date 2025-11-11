"""
Módulo de utilidades - Helpers y configuración
"""

from src.utils.config import Config, CATEGORY_COLORS, CATEGORY_ICONS
from src.utils.helpers import (
    format_currency,
    format_date,
    get_month_name,
    get_savings_color,
    validate_amount,
    get_current_month_range,
    group_transactions_by_date,
    calculate_percentage,
    truncate_text,
)

__all__ = [
    "Config",
    "CATEGORY_COLORS",
    "CATEGORY_ICONS",
    "format_currency",
    "format_date",
    "get_month_name",
    "get_savings_color",
    "validate_amount",
    "get_current_month_range",
    "group_transactions_by_date",
    "calculate_percentage",
    "truncate_text",
]
# Nota: Asegúrate de que los módulos 'config' y 'helpers' existen en el directorio 'src/utils/'
# y contienen las funciones y variables mencionadas en los imports.
