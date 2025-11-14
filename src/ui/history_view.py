"""
Vista de historial de transacciones
Archivo: src/ui/history_view.py
"""

import flet as ft
from datetime import datetime
from typing import Dict
from .base_view import BaseView
from .widgets import MonthSelector
from src.utils.config import Config
from src.utils.helpers import get_month_name


class HistoryView(BaseView):
    """Vista de historial de transacciones"""

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

    def _create_detailed_transaction_tile(self, transaction):
        """Crea un tile detallado con opciones de edición"""
        category = self.db.get_category_by_id(transaction.category_id)

        if category is None:
            category_name = "Sin categoría"
            category_icon = "❓"
            category_color = "#9e9e9e"
        else:
            category_name = str(category.name) if category.name else "Sin categoría"
            category_icon = str(category.icon) if category.icon else "💰"
            category_color = str(category.color) if category.color else "#3b82f6"

        transaction_type = (
            str(transaction.transaction_type)
            if transaction.transaction_type
            else "expense"
        )
        is_income = transaction_type == "income"

        description = (
            str(transaction.description)
            if transaction.description
            else "Sin descripción"
        )
        amount = float(transaction.amount) if transaction.amount else 0.0
        notes = str(transaction.notes) if transaction.notes else ""
        has_notes = bool(notes.strip())

        def delete_transaction(e):
            def confirm_delete(e):
                self.db.delete_transaction(transaction.id)
                self.close_dialog()
                self.show_snackbar("Transacción eliminada")
                self.refresh()
                self.page.update()

            dialog = ft.AlertDialog(
                title=ft.Text("Confirmar eliminación"),
                content=ft.Text("¿Estás seguro de eliminar esta transacción?"),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                    ft.TextButton("Eliminar", on_click=confirm_delete),
                ],
            )
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()

        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text(category_icon, size=28),
                        width=55,
                        height=55,
                        border_radius=27,
                        bgcolor=f"{category_color}30",
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        [
                            ft.Text(description, weight=ft.FontWeight.BOLD, size=15),
                            ft.Text(category_name, size=12, color=ft.Colors.GREY_600),
                            (
                                ft.Text(
                                    notes,
                                    size=11,
                                    italic=True,
                                    color=ft.Colors.GREY_500,
                                )
                                if has_notes
                                else ft.Container()
                            ),
                        ],
                        expand=True,
                        spacing=2,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                f"{'+ ' if is_income else '- '}{Config.CURRENCY_SYMBOL} {amount:.2f}",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color="#22c55e" if is_income else "#ef4444",
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_size=18,
                                on_click=delete_transaction,
                                tooltip="Eliminar",
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=12,
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            margin=ft.margin.only(bottom=8, left=5, right=5),
        )

    def build(self) -> ft.Control:
        """Construye la vista de historial"""
        transactions = self.db.get_transactions_by_month(
            self.current_year, self.current_month
        )

        month_label = get_month_name(self.current_month)
        month_selector = MonthSelector(
            self.current_month,
            self.current_year,
            self.previous_month,
            self.next_month,
            month_label
        )

        if not transactions:
            content = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.INBOX, size=64, color=ft.Colors.GREY_400),
                        ft.Text(
                            "No hay transacciones", size=18, color=ft.Colors.GREY_600
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=40,
            )
        else:
            grouped = {}
            for t in transactions:
                date_key = t.date.strftime("%Y-%m-%d")
                if date_key not in grouped:
                    grouped[date_key] = []
                grouped[date_key].append(t)

            transaction_tiles = []
            for date_key in sorted(grouped.keys(), reverse=True):
                transaction_tiles.append(
                    ft.Container(
                        content=ft.Text(
                            datetime.strptime(date_key, "%Y-%m-%d").strftime(
                                "%d de %B, %Y"
                            ),
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_700,
                        ),
                        padding=ft.padding.only(left=10, top=15, bottom=5),
                    )
                )

                for t in grouped[date_key]:
                    transaction_tiles.append(self._create_detailed_transaction_tile(t))

            content = ft.Column(
                transaction_tiles, scroll=ft.ScrollMode.AUTO, expand=True
            )

        return ft.Column(
            [month_selector, ft.Divider(height=10), content], expand=True
        )

