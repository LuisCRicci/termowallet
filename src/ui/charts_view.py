"""
Vista de gráficos y análisis
Archivo: src/ui/charts_view.py
"""

import flet as ft
from .base_view import BaseView
from .widgets import MonthSelector
from src.utils.config import Config
from src.utils.helpers import get_month_name

class ChartsView(BaseView):
    """Vista de gráficos y análisis"""

    def __init__(self, page: ft.Page, db_manager, show_snackbar_callback,
                 current_month: int, current_year: int,
                 on_month_change: callable):
        super().__init__(page, db_manager, show_snackbar_callback)
        self.current_month = current_month
        self.current_year = current_year
        self.on_month_change = on_month_change

    def previous_month(self, e):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.on_month_change(self.current_month, self.current_year)

    def next_month(self, e):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.on_month_change(self.current_month, self.current_year)

    def _create_category_chart(self, expenses_data: list):
        """Crea gráfico de gastos por categoría"""
        total = sum(item["total"] for item in expenses_data)

        bars = []
        for item in expenses_data:
            percentage = (item["total"] / total * 100) if total > 0 else 0

            bars.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Row(
                                        [
                                            ft.Text(item["icon"], size=20),
                                            ft.Text(
                                                item["category"],
                                                size=14,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                        ],
                                        spacing=5,
                                    ),
                                    ft.Text(
                                        f"{Config.CURRENCY_SYMBOL} {item['total']:.2f}",
                                        size=14,
                                        color=ft.Colors.GREY_700,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.ProgressBar(
                                value=percentage / 100,
                                color=item["color"],
                                bgcolor="#e5e7eb",
                                height=8,
                            ),
                            ft.Text(
                                f"{percentage:.1f}%", size=12, color=ft.Colors.GREY_600
                            ),
                        ],
                        spacing=5,
                    ),
                    padding=10,
                    margin=ft.margin.only(bottom=10),
                )
            )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "💸 Gastos por Categoría", size=18, weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=10),
                    ft.Column(bars),
                ],
                spacing=5,
            ),
            padding=15,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
        )

    def _create_trend_chart(self, monthly_data: list):
        """Crea gráfico de tendencia mensual"""
        trend_items = []

        for m in monthly_data:
            savings_rate_color = "#22c55e" if m["savings_rate"] > 20 else "#f97316"

            trend_items.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(
                                f"{m['month_name'][:3]}",
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                width=40,
                            ),
                            ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Icon(
                                                ft.Icons.ARROW_UPWARD,
                                                size=14,
                                                color="#22c55e",
                                            ),
                                            ft.Text(
                                                f"{Config.CURRENCY_SYMBOL} {m['total_income']:.0f}",
                                                size=13,
                                            ),
                                        ],
                                        spacing=5,
                                    ),
                                    ft.Row(
                                        [
                                            ft.Icon(
                                                ft.Icons.ARROW_DOWNWARD,
                                                size=14,
                                                color="#ef4444",
                                            ),
                                            ft.Text(
                                                f"{Config.CURRENCY_SYMBOL} {m['total_expenses']:.0f}",
                                                size=13,
                                            ),
                                        ],
                                        spacing=5,
                                    ),
                                ],
                                expand=True,
                                spacing=2,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    f"{m['savings_rate']:.0f}%",
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color=savings_rate_color,
                                ),
                                bgcolor=f"{savings_rate_color}20",
                                padding=8,
                                border_radius=8,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=10,
                    margin=ft.margin.only(bottom=5),
                    bgcolor="#f9fafb",
                    border_radius=8,
                )
            )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "📈 Tendencia Mensual",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(height=10),
                    ft.Column(trend_items),
                ],
                spacing=5,
            ),
            padding=15,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
        )

    def build(self) -> ft.Control:
        """Construye la vista de gráficos"""
        summary = self.db.get_monthly_summary(self.current_year, self.current_month)
        expenses_by_category = self.db.get_expenses_by_category(
            self.current_year, self.current_month
        )
        monthly_trend = self.db.get_monthly_trend(6)

        month_label = get_month_name(self.current_month)
        month_selector = MonthSelector(
            self.current_month,
            self.current_year,
            self.previous_month,
            self.next_month,
            month_label
        )

        summary_card = ft.Container(
            content=ft.Column(
                [
                    ft.Text("📊 Resumen del Mes", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text(
                        f"💰 Ingresos: {Config.CURRENCY_SYMBOL} {summary['total_income']:.2f}",
                        size=16,
                    ),
                    ft.Text(
                        f"💸 Gastos: {Config.CURRENCY_SYMBOL} {summary['total_expenses']:.2f}",
                        size=16,
                    ),
                    ft.Text(
                        f"💎 Ahorro: {Config.CURRENCY_SYMBOL} {summary['savings']:.2f}",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        f"📈 Tasa de Ahorro: {summary['savings_rate']:.1f}%", size=16
                    ),
                ]
            ),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
        )

        charts = [summary_card]

        if expenses_by_category:
            category_chart = self._create_category_chart(expenses_by_category)
            charts.append(category_chart)

        if monthly_trend:
            trend_chart = self._create_trend_chart(monthly_trend)
            charts.append(trend_chart)

        return ft.Column(
            [month_selector, ft.Container(height=10), *charts],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=15,
        )