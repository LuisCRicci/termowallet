"""
Vista de Presupuestos Mensuales - CORREGIDA
Archivo: src/ui/budget_view.py
"""

import flet as ft
from datetime import datetime
from .base_view import BaseView
from .widgets import (
    MonthSelector,
    BudgetProgressCard,
    BudgetAlertBanner,
    BudgetHistoryTile,
)
from src.utils.config import Config
from src.utils.helpers import get_month_name


class BudgetView(BaseView):
    """Vista de gestión de presupuestos mensuales"""

    def __init__(
        self,
        page: ft.Page,
        db_manager,
        show_snackbar_callback,
        current_month: int,
        current_year: int,
        on_month_change: callable,
    ):
        super().__init__(page, db_manager, show_snackbar_callback)
        self.current_month = current_month
        self.current_year = current_year
        self.on_month_change = on_month_change
        self.is_saving = False  # ⭐ Flag para evitar clics múltiples

    def previous_month(self, e):
        """Navega al mes anterior"""
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.on_month_change(self.current_month, self.current_year)

    def next_month(self, e):
        """Navega al mes siguiente"""
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.on_month_change(self.current_month, self.current_year)

    def show_create_budget_dialog(self, e):
        """Muestra diálogo para crear/editar presupuesto"""
        self.is_saving = False  # ⭐ Reset flag
        
        # Obtener presupuesto existente si hay
        existing_budget = self.db.get_monthly_budget(
            self.current_year, self.current_month
        )

        income_field = ft.TextField(
            label="Meta de Ingresos",
            prefix_text=f"{Config.CURRENCY_SYMBOL} ",
            keyboard_type=ft.KeyboardType.NUMBER,
            value=str(existing_budget.income_goal) if existing_budget else "0",
            bgcolor=ft.Colors.WHITE,
        )

        expense_field = ft.TextField(
            label="Límite de Gastos",
            prefix_text=f"{Config.CURRENCY_SYMBOL} ",
            keyboard_type=ft.KeyboardType.NUMBER,
            value=str(existing_budget.expense_limit) if existing_budget else "0",
            bgcolor=ft.Colors.WHITE,
        )

        savings_field = ft.TextField(
            label="Meta de Ahorro",
            prefix_text=f"{Config.CURRENCY_SYMBOL} ",
            keyboard_type=ft.KeyboardType.NUMBER,
            value=str(existing_budget.savings_goal) if existing_budget else "0",
            bgcolor=ft.Colors.WHITE,
        )

        notes_field = ft.TextField(
            label="Notas (opcional)",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=existing_budget.notes if existing_budget and existing_budget.notes else "",
            bgcolor=ft.Colors.WHITE,
        )

        def save_budget(e):
            # ⭐ Evitar clics múltiples
            if self.is_saving:
                return
            
            try:
                income_goal = float(income_field.value or 0)
                expense_limit = float(expense_field.value or 0)
                savings_goal = float(savings_field.value or 0)

                if expense_limit <= 0 and income_goal <= 0 and savings_goal <= 0:
                    self.show_snackbar(
                        "Debes establecer al menos una meta", error=True
                    )
                    return

                self.is_saving = True  # ⭐ Bloquear

                self.db.create_or_update_budget(
                    year=self.current_year,
                    month=self.current_month,
                    income_goal=income_goal,
                    expense_limit=expense_limit,
                    savings_goal=savings_goal,
                    notes=notes_field.value.strip() if notes_field.value else None,
                )

                self.close_dialog()
                self.show_snackbar("✅ Presupuesto guardado exitosamente")
                
                # ⭐ FORZAR RECARGA usando el callback
                self.on_month_change(self.current_month, self.current_year)

            except ValueError:
                self.show_snackbar("Valores inválidos", error=True)
                self.is_saving = False
            except Exception as ex:
                self.show_snackbar(f"Error: {str(ex)}", error=True)
                self.is_saving = False

        dialog = ft.AlertDialog(
            title=ft.Text(
                f"Presupuesto {get_month_name(self.current_month)} {self.current_year}"
            ),
            # ⭐ CORRECCIÓN: Container con altura
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Establece tus metas financieras para este mes:",
                            size=13,
                            color=ft.Colors.GREY_700,
                        ),
                        ft.Container(height=5),
                        income_field,
                        expense_field,
                        savings_field,
                        notes_field,
                        ft.Container(
                            content=ft.Text(
                                "💡 Consejo: Tu límite de gastos debería ser menor a tus ingresos",
                                size=11,
                                color=ft.Colors.GREY_600,
                                italic=True,
                            ),
                            padding=10,
                            bgcolor=ft.Colors.BLUE_50,
                            border_radius=8,
                        ),
                    ],
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                height=500,  # ⭐ Altura en el Container
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.ElevatedButton(
                    "Guardar",
                    icon=ft.Icons.SAVE,
                    on_click=save_budget,
                ),
            ],
        )

        self.show_dialog(dialog)

    def confirm_delete_budget(self, e):
        """Confirma eliminación del presupuesto"""
        def delete(e):
            if self.db.delete_budget(self.current_year, self.current_month):
                self.close_dialog()
                self.show_snackbar("Presupuesto eliminado")
                
                # ⭐ FORZAR RECARGA usando el callback
                self.on_month_change(self.current_month, self.current_year)
            else:
                self.show_snackbar("Error al eliminar", error=True)

        self.confirm_action(
            "Eliminar Presupuesto",
            "¿Estás seguro de eliminar el presupuesto de este mes?",
            delete,
            "Eliminar",
            "Cancelar",
            is_dangerous=True,
        )

    def build(self) -> ft.Control:
        """Construye la vista de presupuestos"""
        print(f"\n{'='*60}")
        print(f"💰 CARGANDO VISTA PRESUPUESTOS")
        print(f"{'='*60}")

        # Obtener datos
        budget_status = self.db.get_budget_status(
            self.current_year, self.current_month
        )
        alerts = self.db.get_budget_alerts(self.current_year, self.current_month)
        budget_history = self.db.get_budget_history(6)

        # Selector de mes
        month_label = get_month_name(self.current_month)
        month_selector = MonthSelector(
            self.current_month,
            self.current_year,
            self.previous_month,
            self.next_month,
            month_label,
        )

        # Contenido inicial
        content_widgets = [
            month_selector,
            ft.Container(height=10),
        ]

        # Alertas
        if alerts:
            for alert in alerts:
                content_widgets.append(BudgetAlertBanner(alert))
            content_widgets.append(ft.Container(height=10))

        # Verificar si existe presupuesto
        if not budget_status["budget_exists"]:
            # Vista de estado vacío
            empty_section = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(
                            ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
                            size=80,
                            color=ft.Colors.GREY_400,
                        ),
                        ft.Text(
                            "No hay presupuesto configurado",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_600,
                        ),
                        ft.Text(
                            "Establece metas de ingresos, gastos y ahorros para este mes",
                            size=14,
                            color=ft.Colors.GREY_500,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=20),
                        ft.ElevatedButton(
                            "Crear Presupuesto",
                            icon=ft.Icons.ADD,
                            on_click=self.show_create_budget_dialog,
                            style=ft.ButtonStyle(
                                bgcolor=Config.PRIMARY_COLOR,
                                color=ft.Colors.WHITE,
                            ),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=40,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
            )
            content_widgets.append(empty_section)
        else:
            # Botones de acción
            action_buttons = ft.Row(
                [
                    ft.OutlinedButton(
                        "Editar Presupuesto",
                        icon=ft.Icons.EDIT,
                        on_click=self.show_create_budget_dialog,
                        expand=True,
                    ),
                    ft.OutlinedButton(
                        "Eliminar",
                        icon=ft.Icons.DELETE_OUTLINE,
                        on_click=self.confirm_delete_budget,
                        expand=True,
                    ),
                ],
                spacing=10,
            )
            content_widgets.append(action_buttons)
            content_widgets.append(ft.Container(height=15))

            # Tarjetas de progreso
            progress_section = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "📊 Progreso del Mes",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Container(height=10),
                        # Gastos
                        BudgetProgressCard(
                            "Gastos del Mes",
                            budget_status["expense_limit"],
                            budget_status["actual_expenses"],
                            ft.Icons.TRENDING_DOWN,
                            "#ef4444",
                            is_reversed=False,
                        ),
                        ft.Container(height=10),
                        # Ingresos
                        BudgetProgressCard(
                            "Ingresos del Mes",
                            budget_status["income_goal"],
                            budget_status["actual_income"],
                            ft.Icons.TRENDING_UP,
                            "#22c55e",
                            is_reversed=True,
                        ),
                        ft.Container(height=10),
                        # Ahorros
                        BudgetProgressCard(
                            "Meta de Ahorro",
                            budget_status["savings_goal"],
                            budget_status["actual_savings"],
                            ft.Icons.SAVINGS,
                            "#3b82f6",
                            is_reversed=True,
                        ),
                    ],
                ),
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
            )
            content_widgets.append(progress_section)

            # Notas del presupuesto
            if budget_status.get("notes"):
                notes_section = ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.NOTE, size=20, color="#f59e0b"),
                                    ft.Text(
                                        "Notas",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                                spacing=8,
                            ),
                            ft.Text(
                                budget_status["notes"],
                                size=14,
                                color=ft.Colors.GREY_700,
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=15,
                    bgcolor="#fef3c7",
                    border_radius=10,
                    border=ft.border.all(1, "#f59e0b"),
                    margin=ft.margin.only(top=15),
                )
                content_widgets.append(notes_section)

        # Historial de presupuestos
        content_widgets.append(ft.Container(height=20))
        history_section = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "📈 Historial de Presupuestos",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(height=10),
                    *[BudgetHistoryTile(history) for history in budget_history],
                ],
                spacing=5,
            ),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
        )
        content_widgets.append(history_section)
        content_widgets.append(ft.Container(height=30))

        print("✅ Vista PRESUPUESTOS ensamblada")

        return ft.Column(
            content_widgets,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=0,
        )