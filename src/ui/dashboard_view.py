"""
Vista de Dashboard con Gráficos
Archivo: src/ui/dashboard_view.py
"""

import flet as ft
from datetime import datetime
from src.utils.config import Config


class DashboardView:
    """Vista de gráficos y análisis"""

    def __init__(self, db_manager):
        self.db = db_manager
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year

    def build(self) -> ft.Container:
        """Construye la vista"""

        # Obtener datos
        summary = self.db.get_monthly_summary(self.current_year, self.current_month)
        expenses_by_cat = self.db.get_expenses_by_category(
            self.current_year, self.current_month
        )
        income_by_cat = self.db.get_income_by_category(
            self.current_year, self.current_month
        )
        monthly_trend = self.db.get_monthly_trend(6)

        # Selector de mes
        month_selector = ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=self._previous_month,
                    tooltip="Mes anterior",
                ),
                ft.Text(
                    f"{summary['month_name']} {self.current_year}",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    expand=True,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.IconButton(
                    icon=ft.Icons.ARROW_FORWARD,
                    on_click=self._next_month,
                    tooltip="Mes siguiente",
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        # Tarjetas de resumen
        summary_cards = ft.Row(
            [
                self._create_stat_card(
                    "💰 Ingresos",
                    f"{Config.CURRENCY_SYMBOL} {summary['total_income']:.2f}",
                    Config.SUCCESS_COLOR,
                ),
                self._create_stat_card(
                    "💸 Gastos",
                    f"{Config.CURRENCY_SYMBOL} {summary['total_expenses']:.2f}",
                    Config.ERROR_COLOR,
                ),
                self._create_stat_card(
                    "💎 Ahorro",
                    f"{Config.CURRENCY_SYMBOL} {summary['savings']:.2f}",
                    (
                        Config.PRIMARY_COLOR
                        if summary["savings"] >= 0
                        else Config.WARNING_COLOR
                    ),
                ),
            ],
            wrap=True,
            spacing=10,
        )

        # Gráfico de gastos por categoría
        expenses_chart = self._create_category_chart(
            expenses_by_cat, "📊 Gastos por Categoría"
        )

        # Gráfico de ingresos por categoría
        income_chart = self._create_category_chart(
            income_by_cat, "💵 Ingresos por Categoría"
        )

        # Gráfico de tendencia mensual
        trend_chart = self._create_trend_chart(monthly_trend)

        # Contenedor principal
        return ft.Container(
            content=ft.Column(
                [
                    month_selector,
                    summary_cards,
                    ft.Divider(height=20),
                    expenses_chart,
                    income_chart,
                    trend_chart,
                    ft.Container(
                        content=ft.Text(
                            "💡 Los gráficos se actualizan automáticamente al cambiar de mes",
                            size=12,
                            italic=True,
                            color=ft.Colors.GREY_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        padding=10,
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=15,
            ),
            expand=True,
            padding=10,
        )

    def _create_stat_card(self, title: str, value: str, color: str):
        """Crea una tarjeta de estadística"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(title, size=14, color=ft.Colors.GREY_700),
                    ft.Text(value, size=20, weight=ft.FontWeight.BOLD, color=color),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.SURFACE,
            expand=True,
        )

    def _create_category_chart(self, data: list, title: str):
        """Crea un gráfico de categorías con barras"""
        if not data:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
                        ft.Icon(
                            ft.Icons.PIE_CHART_OUTLINE,
                            size=48,
                            color=ft.Colors.GREY_400,
                        ),
                        ft.Text(
                            "No hay datos para mostrar",
                            color=ft.Colors.GREY_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
                padding=20,
                border_radius=10,
                bgcolor=ft.Colors.SURFACE,
            )

        total = sum(item["total"] for item in data)

        # Crear barras
        bars = []
        for item in sorted(data, key=lambda x: x["total"], reverse=True):
            percentage = (item["total"] / total * 100) if total > 0 else 0

            # Fila de información
            bars.append(
                ft.Row(
                    [
                        ft.Text(item["icon"], size=20),
                        ft.Column(
                            [
                                ft.Text(
                                    item["category"], size=14, weight=ft.FontWeight.BOLD
                                ),
                                ft.Text(
                                    f"{Config.CURRENCY_SYMBOL} {item['total']:.2f} ({percentage:.1f}%)",
                                    size=12,
                                    color=ft.Colors.GREY_600,
                                ),
                            ],
                            expand=True,
                            spacing=2,
                        ),
                    ],
                    spacing=8,
                )
            )

            # Barra de progreso
            bars.append(
                ft.ProgressBar(
                    value=percentage / 100,
                    color=item["color"],
                    bgcolor=ft.Colors.GREY_200,
                    height=10,
                )
            )

            bars.append(ft.Container(height=10))  # Espaciado

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=10),
                    ft.Column(bars, spacing=5),
                ],
                spacing=10,
            ),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.SURFACE,
        )

    def _create_trend_chart(self, history: list):
        """Crea gráfico de tendencia mensual"""
        if not history or len(history) == 0:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "📈 Tendencia Mensual", size=18, weight=ft.FontWeight.BOLD
                        ),
                        ft.Text("No hay suficientes datos", color=ft.Colors.GREY_600),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
                border_radius=10,
                bgcolor=ft.Colors.SURFACE,
            )

        # Calcular valor máximo para escalar
        max_value = max(
            [h["total_income"] for h in history]
            + [h["total_expenses"] for h in history]
        )

        if max_value == 0:
            max_value = 1

        # Crear barras para cada mes
        bars = []
        for h in history:
            income_height = (
                (h["total_income"] / max_value * 120) if max_value > 0 else 0
            )
            expense_height = (
                (h["total_expenses"] / max_value * 120) if max_value > 0 else 0
            )

            month_col = ft.Column(
                [
                    ft.Container(height=130 - income_height),  # Espaciador
                    ft.Container(
                        width=35,
                        height=max(income_height, 5),
                        bgcolor=Config.SUCCESS_COLOR,
                        border_radius=ft.border_radius.only(top_left=5, top_right=5),
                        tooltip=f"Ingresos: {Config.CURRENCY_SYMBOL} {h['total_income']:.2f}",
                    ),
                    ft.Container(height=2),
                    ft.Container(
                        width=35,
                        height=max(expense_height, 5),
                        bgcolor=Config.ERROR_COLOR,
                        border_radius=ft.border_radius.only(
                            bottom_left=5, bottom_right=5
                        ),
                        tooltip=f"Gastos: {Config.CURRENCY_SYMBOL} {h['total_expenses']:.2f}",
                    ),
                    ft.Text(
                        h["month_name"][:3],
                        size=10,
                        text_align=ft.TextAlign.CENTER,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            )

            bars.append(month_col)

        # Leyenda
        legend = ft.Row(
            [
                ft.Row(
                    [
                        ft.Container(
                            width=15,
                            height=15,
                            bgcolor=Config.SUCCESS_COLOR,
                            border_radius=3,
                        ),
                        ft.Text("Ingresos", size=12),
                    ],
                    spacing=5,
                ),
                ft.Row(
                    [
                        ft.Container(
                            width=15,
                            height=15,
                            bgcolor=Config.ERROR_COLOR,
                            border_radius=3,
                        ),
                        ft.Text("Gastos", size=12),
                    ],
                    spacing=5,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "📈 Tendencia de los Últimos 6 Meses",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Divider(height=10),
                    legend,
                    ft.Container(
                        content=ft.Row(
                            bars, alignment=ft.MainAxisAlignment.SPACE_EVENLY, spacing=5
                        ),
                        height=180,
                    ),
                ],
                spacing=10,
            ),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.SURFACE,
        )

    def _previous_month(self, e):
        """Navega al mes anterior"""
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.refresh()

    def _next_month(self, e):
        """Navega al mes siguiente"""
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.refresh()

    def refresh(self):
        """Refresca la vista (debe ser implementado por el controlador)"""
        pass  # Será manejado por main.py

    def set_month(self, month: int, year: int):
        """Establece el mes y año actual"""
        self.current_month = month
        self.current_year = year
