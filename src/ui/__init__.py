"""
Módulo de Interfaz de Usuario
Archivo: src/ui/__init__.py
"""

from src.ui.components import (
    SummaryCard,
    TransactionTile,
    CategoryTile,
    MonthSelector,
    EmptyState,
    LoadingIndicator,
    StatisticCard,
    ProgressIndicator,
    ChipButton,
)

from src.ui.home_view import HomeView
from src.ui.upload_view import UploadView
from src.ui.dashboard_view import DashboardView

__all__ = [
    # Componentes
    "SummaryCard",
    "TransactionTile",
    "CategoryTile",
    "MonthSelector",
    "EmptyState",
    "LoadingIndicator",
    "StatisticCard",
    "ProgressIndicator",
    "ChipButton",
    # Vistas
    "HomeView",
    "UploadView",
    "DashboardView",
]
