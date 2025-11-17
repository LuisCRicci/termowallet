"""
Vista de historial de transacciones - CORRECCIÓN ELIMINACIÓN
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

    def show_edit_dialog(self, transaction):
        """Muestra el diálogo de edición de transacción"""
        # Obtener información actual
        category = self.db.get_category_by_id(transaction.category_id)
        transaction_type = transaction.transaction_type

        # Campos del formulario
        amount_field = ft.TextField(
            label="Monto",
            prefix_text=f"{Config.CURRENCY_SYMBOL} ",
            keyboard_type=ft.KeyboardType.NUMBER,
            value=str(transaction.amount),
            bgcolor=ft.Colors.WHITE,
            border_color=Config.PRIMARY_COLOR,
        )

        description_field = ft.TextField(
            label="Descripción",
            value=transaction.description,
            max_length=200,
            bgcolor=ft.Colors.WHITE,
            border_color=Config.PRIMARY_COLOR,
        )

        date_field = ft.TextField(
            label="Fecha",
            value=transaction.date.strftime("%Y-%m-%d"),
            read_only=True,
            bgcolor=ft.Colors.WHITE,
            border_color=Config.PRIMARY_COLOR,
            suffix_icon=ft.Icons.CALENDAR_TODAY,
        )

        # Selector de fecha
        def pick_date(e):
            def on_date_change(e):
                if e.control.value:
                    date_field.value = e.control.value.strftime("%Y-%m-%d")
                    self.page.update()

            date_picker = ft.DatePicker(
                on_change=on_date_change,
                first_date=datetime(2020, 1, 1),
                last_date=datetime(2030, 12, 31),
            )
            self.page.overlay.append(date_picker)
            date_picker.open = True
            self.page.update()

        date_field.on_click = pick_date

        # Dropdown de categorías (según el tipo)
        categories = self.db.get_all_categories(transaction_type)
        category_dropdown = ft.Dropdown(
            label="Categoría",
            value=str(transaction.category_id),
            options=[
                ft.dropdown.Option(
                    key=str(cat.id),
                    text=f"{cat.icon} {cat.name}"
                )
                for cat in categories
            ],
            bgcolor=ft.Colors.WHITE,
            border_color=Config.PRIMARY_COLOR,
        )

        notes_field = ft.TextField(
            label="Notas (opcional)",
            value=transaction.notes or "",
            multiline=True,
            min_lines=2,
            max_lines=4,
            max_length=500,
            bgcolor=ft.Colors.WHITE,
            border_color=Config.PRIMARY_COLOR,
        )

        # Función para guardar cambios
        def save_changes(e):
            try:
                # Validaciones
                if not amount_field.value or float(amount_field.value) <= 0:
                    self.show_snackbar("⚠️ El monto debe ser mayor a 0", error=True)
                    return

                if not description_field.value.strip():
                    self.show_snackbar("⚠️ La descripción es obligatoria", error=True)
                    return

                if not category_dropdown.value:
                    self.show_snackbar("⚠️ Debes seleccionar una categoría", error=True)
                    return

                # ⭐ ORDEN CORRECTO:
                # 1. Actualizar en la base de datos
                success = self.db.update_transaction(
                    transaction_id=transaction.id,
                    date=datetime.strptime(date_field.value, "%Y-%m-%d"),
                    description=description_field.value.strip(),
                    amount=float(amount_field.value),
                    category_id=int(category_dropdown.value),
                    notes=notes_field.value.strip() if notes_field.value else ""
                )

                if success:
                    # 2. Recargar vista usando el callback
                    self.on_month_change(self.current_month, self.current_year)
                    
                    # 3. Mostrar mensaje de éxito
                    self.show_snackbar("✅ Transacción actualizada exitosamente")
                    
                    # 4. Cerrar diálogo AL FINAL
                    self.close_dialog()
                else:
                    self.show_snackbar("❌ Error al actualizar la transacción", error=True)

            except ValueError:
                self.show_snackbar("⚠️ El monto debe ser un número válido", error=True)
            except Exception as ex:
                print(f"Error al editar transacción: {ex}")
                self.show_snackbar(f"❌ Error: {str(ex)}", error=True)

        # Crear el diálogo
        dialog = ft.AlertDialog(
            title=ft.Row(
                [
                    ft.Icon(
                        ft.Icons.EDIT,
                        color=Config.PRIMARY_COLOR,
                        size=28
                    ),
                    ft.Text(
                        "Editar Transacción",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),
                ],
                spacing=10,
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        # Tipo de transacción (solo informativo)
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Icon(
                                        ft.Icons.INFO_OUTLINE,
                                        size=16,
                                        color=ft.Colors.BLUE_700
                                    ),
                                    ft.Text(
                                        f"Tipo: {'Ingreso' if transaction_type == 'income' else 'Gasto'}",
                                        size=12,
                                        color=ft.Colors.BLUE_700,
                                        italic=True,
                                    ),
                                ],
                                spacing=5,
                            ),
                            padding=10,
                            bgcolor=ft.Colors.BLUE_50,
                            border_radius=8,
                        ),
                        ft.Divider(height=10),
                        amount_field,
                        description_field,
                        category_dropdown,
                        date_field,
                        notes_field,
                    ],
                    spacing=15,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=500,
                height=500,
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda _: self.close_dialog()
                ),
                ft.ElevatedButton(
                    "Guardar Cambios",
                    icon=ft.Icons.SAVE,
                    on_click=save_changes,
                    style=ft.ButtonStyle(
                        bgcolor=Config.PRIMARY_COLOR,
                        color=ft.Colors.WHITE,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.show_dialog(dialog)

    def _create_detailed_transaction_tile(self, transaction):
        """Crea un tile detallado con opciones de edición y eliminación"""
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
            """⭐ CORRECCIÓN: Elimina la transacción y recarga la vista"""
            def confirm_delete(e):
                try:
                    # ⭐ ORDEN CORRECTO:
                    # 1. Eliminar de la base de datos
                    success = self.db.delete_transaction(transaction.id)
                    
                    if success:
                        # 2. Recargar vista usando el callback
                        self.on_month_change(self.current_month, self.current_year)
                        
                        # 3. Mostrar mensaje de éxito
                        self.show_snackbar("✅ Transacción eliminada")
                        
                        # 4. Cerrar diálogo AL FINAL
                        self.close_dialog()
                    else:
                        self.show_snackbar("❌ Error al eliminar la transacción", error=True)
                        
                except Exception as ex:
                    self.show_snackbar(f"❌ Error: {str(ex)}", error=True)

            dialog = ft.AlertDialog(
                title=ft.Text("⚠️ Confirmar eliminación"),
                content=ft.Column(
                    [
                        ft.Text(
                            "¿Estás seguro de eliminar esta transacción?\n"
                            "Esta acción no se puede deshacer.",
                            size=14,
                        ),
                        ft.Container(height=10),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        description,
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        f"{Config.CURRENCY_SYMBOL} {amount:.2f}",
                                        size=14,
                                        color="#ef4444" if not is_income else "#22c55e",
                                    ),
                                ],
                                spacing=5,
                            ),
                            padding=15,
                            bgcolor=ft.Colors.GREY_100,
                            border_radius=8,
                        ),
                    ],
                    tight=True,
                    spacing=5,
                ),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                    ft.ElevatedButton(
                        "Eliminar",
                        on_click=confirm_delete,
                        style=ft.ButtonStyle(
                            bgcolor="#ef4444",
                            color=ft.Colors.WHITE,
                        ),
                    ),
                ],
            )
            self.show_dialog(dialog)

        def edit_transaction(e):
            """Abre el diálogo de edición"""
            self.show_edit_dialog(transaction)

        return ft.Container(
            content=ft.Row(
                [
                    # Icono de categoría
                    ft.Container(
                        content=ft.Text(category_icon, size=28),
                        width=55,
                        height=55,
                        border_radius=27,
                        bgcolor=f"{category_color}30",
                        alignment=ft.alignment.center,
                    ),
                    # Información de la transacción
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
                    # Monto y botones de acción
                    ft.Column(
                        [
                            ft.Text(
                                f"{'+ ' if is_income else '- '}{Config.CURRENCY_SYMBOL} {amount:.2f}",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color="#22c55e" if is_income else "#ef4444",
                            ),
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT,
                                        icon_size=18,
                                        icon_color="#3b82f6",
                                        on_click=edit_transaction,
                                        tooltip="Editar transacción",
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        icon_size=18,
                                        icon_color="#ef4444",
                                        on_click=delete_transaction,
                                        tooltip="Eliminar transacción",
                                    ),
                                ],
                                spacing=0,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=5,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=12,
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            margin=ft.margin.only(bottom=8, left=5, right=5),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=4,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )

    def build(self) -> ft.Control:
        """Construye la vista de historial"""
        print(f"\n📜 CARGANDO HISTORIAL: {self.current_month}/{self.current_year}")
        
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

        # Resumen del mes
        summary = self.db.get_monthly_summary(self.current_year, self.current_month)
        
        summary_card = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text("Ingresos", size=12, color=ft.Colors.GREY_600),
                            ft.Text(
                                f"{Config.CURRENCY_SYMBOL} {summary['total_income']:.2f}",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color="#22c55e"
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True,
                    ),
                    ft.Container(width=1, bgcolor=ft.Colors.GREY_300, height=40),
                    ft.Column(
                        [
                            ft.Text("Gastos", size=12, color=ft.Colors.GREY_600),
                            ft.Text(
                                f"{Config.CURRENCY_SYMBOL} {summary['total_expenses']:.2f}",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color="#ef4444"
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True,
                    ),
                    ft.Container(width=1, bgcolor=ft.Colors.GREY_300, height=40),
                    ft.Column(
                        [
                            ft.Text("Balance", size=12, color=ft.Colors.GREY_600),
                            ft.Text(
                                f"{Config.CURRENCY_SYMBOL} {summary['savings']:.2f}",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color="#3b82f6"
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            ),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            margin=ft.margin.only(bottom=15),
        )

        if not transactions:
            content = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.INBOX, size=64, color=ft.Colors.GREY_400),
                        ft.Text(
                            "No hay transacciones este mes",
                            size=18,
                            color=ft.Colors.GREY_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=10),
                        ft.Text(
                            "Agrega tu primera transacción",
                            size=14,
                            color=ft.Colors.GREY_500,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=40,
                alignment=ft.alignment.center,
            )
        else:
            # Agrupar por fecha
            grouped = {}
            for t in transactions:
                date_key = t.date.strftime("%Y-%m-%d")
                if date_key not in grouped:
                    grouped[date_key] = []
                grouped[date_key].append(t)

            transaction_tiles = []
            
            # Encabezado de lista
            transaction_tiles.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(
                                f"📋 Transacciones ({len(transactions)})",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                    ),
                    padding=ft.padding.only(left=10, top=10, bottom=10),
                )
            )
            
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
                transaction_tiles,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                spacing=0,
            )

        return ft.Column(
            [
                month_selector,
                ft.Container(height=10),
                summary_card,
                content,
                ft.Container(height=20),
            ],
            expand=True,
            spacing=0,
        )