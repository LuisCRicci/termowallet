"""
Vista Principal (Home)
Archivo: src/ui/home_view.py
"""

import flet as ft
from datetime import datetime
from src.utils.config import Config


class HomeView:
    """Vista principal con resumen mensual"""

    def __init__(self, db_manager, on_navigate):
        self.db = db_manager
        self.on_navigate = on_navigate
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year

    def build(self) -> ft.Container:
        """Construye la vista"""
        # Obtener datos
        summary = self.db.get_monthly_summary(self.current_year, self.current_month)

        # Tarjetas de resumen
        cards_row = ft.Row(
            [
                self._create_summary_card(
                    "Ingresos",
                    f"{Config.CURRENCY_SYMBOL} {summary['total_income']:.2f}",
                    ft.Icons.TRENDING_UP,
                    Config.SUCCESS_COLOR,
                ),
                self._create_summary_card(
                    "Gastos",
                    f"{Config.CURRENCY_SYMBOL} {summary['total_expenses']:.2f}",
                    ft.Icons.TRENDING_DOWN,
                    Config.ERROR_COLOR,
                ),
                self._create_summary_card(
                    "Ahorro",
                    f"{Config.CURRENCY_SYMBOL} {summary['savings']:.2f}",
                    ft.Icons.SAVINGS,
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

        # Indicador de tasa de ahorro
        savings_rate = summary["savings_rate"]
        savings_indicator = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Tasa de Ahorro", size=16, weight=ft.FontWeight.BOLD),
                    ft.ProgressBar(
                        value=max(0, min(savings_rate / 100, 1)),
                        color=(
                            Config.SUCCESS_COLOR
                            if savings_rate > 20
                            else Config.WARNING_COLOR
                        ),
                        bgcolor=ft.Colors.GREY_300,
                        height=10,
                    ),
                    ft.Text(
                        f"{savings_rate:.1f}%",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=(
                            Config.SUCCESS_COLOR
                            if savings_rate > 20
                            else Config.WARNING_COLOR
                        ),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            padding=20,
            border_radius=10,
            bgcolor=ft.Colors.SURFACE,
        )

        # Últimas transacciones
        recent_transactions = self.db.get_transactions_by_month(
            self.current_year, self.current_month
        )[:5]

        if recent_transactions:
            transactions_list = ft.Column(
                [
                    ft.Text(
                        "Transacciones Recientes", size=18, weight=ft.FontWeight.BOLD
                    ),
                    *[self._create_transaction_tile(t) for t in recent_transactions],
                    ft.TextButton(
                        "Ver todas →",
                        on_click=lambda _: self.on_navigate(2),  # Navegar a historial
                    ),
                ],
                spacing=5,
            )
        else:
            transactions_list = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.INBOX, size=48, color=ft.Colors.GREY_400),
                        ft.Text(
                            "No hay transacciones este mes",
                            size=14,
                            color=ft.Colors.GREY_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.ElevatedButton(
                            "Añadir transacción",
                            icon=ft.Icons.ADD,
                            on_click=lambda _: self.on_navigate(1),
                            style=ft.ButtonStyle(
                                bgcolor=Config.PRIMARY_COLOR, color=ft.Colors.WHITE
                            ),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
                padding=30,
            )

        # Contenedor principal
        return ft.Container(
            content=ft.Column(
                [
                    month_selector,
                    cards_row,
                    savings_indicator,
                    ft.Divider(height=20),
                    transactions_list,
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=15,
            ),
            expand=True,
            padding=10,
        )

    def _create_summary_card(self, title: str, value: str, icon, color):
        """Crea una tarjeta de resumen"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=40, color=color),
                    ft.Text(title, size=14, color=ft.Colors.GREY_700),
                    ft.Text(value, size=18, weight=ft.FontWeight.BOLD),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.SURFACE,
            expand=True,
            height=120,
        )

    def _create_transaction_tile(self, transaction):
        """Crea un tile para una transacción"""
        category = self.db.get_category_by_id(transaction.category_id)
        is_income = transaction.transaction_type == "income"

        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text(category.icon, size=24),
                        width=50,
                        height=50,
                        border_radius=25,
                        bgcolor=category.color + "30",
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                transaction.description,
                                weight=ft.FontWeight.BOLD,
                                size=14,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                f"{category.name} • {transaction.date.strftime(Config.DATE_FORMAT)}",
                                size=12,
                                color=ft.Colors.GREY_700,
                            ),
                        ],
                        expand=True,
                        spacing=2,
                    ),
                    ft.Text(
                        f"{'+ ' if is_income else '- '}{Config.CURRENCY_SYMBOL} {transaction.amount:.2f}",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=Config.SUCCESS_COLOR if is_income else Config.ERROR_COLOR,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=10,
            border_radius=10,
            bgcolor=ft.Colors.SURFACE,
            margin=ft.margin.only(bottom=5),
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
