"""
Vista HOME - Dashboard principal - ✅ CORREGIDO
Archivo: src/ui/home_view.py

CORRECCIÓN: mini_cards era una tupla, ahora se desempaqueta correctamente
"""

import flet as ft
from datetime import datetime
from .base_view import BaseView
from .widgets import (
    MonthSelector,
    MiniStatCard,
    TopExpenseTile,
    CompactCategoryBar,
    CompactTransactionTile,
    ProjectionCard,
    BudgetSummaryCard,
    CategoryBudgetAlertWidget,
)
from src.utils.config import Config
from src.utils.helpers import get_month_name


class HomeView(BaseView):
    """Vista principal de la aplicación"""

    def __init__(self, page: ft.Page, db_manager, show_snackbar_callback, 
                 current_month: int, current_year: int, 
                 on_month_change: callable, on_nav_change: callable):
        super().__init__(page, db_manager, show_snackbar_callback)
        self.current_month = current_month
        self.current_year = current_year
        self.on_month_change = on_month_change
        self.on_nav_change = on_nav_change

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

    def build(self) -> ft.Control:
        """Construye la vista HOME"""
        print("\n" + "=" * 60)
        print("🏠 CARGANDO VISTA HOME")
        print("=" * 60)

        # Obtener datos
        try:
            print(f"📅 Consultando datos para: {self.current_month}/{self.current_year}")

            summary = self.db.get_monthly_summary(self.current_year, self.current_month)
            expenses_by_category = self.db.get_expenses_by_category(
                self.current_year, self.current_month
            )
            budget_status = self.db.get_budget_status(
                self.current_year, self.current_month
            )
            top_expenses = self.db.get_top_expenses(
                self.current_year, self.current_month, limit=3
            )
            daily_stats = self.db.get_daily_average(
                self.current_year, self.current_month
            )
            week_comparison = self.db.get_week_comparison(
                self.current_year, self.current_month
            )
            recent_transactions = self.db.get_transactions_by_month(
                self.current_year, self.current_month
            )[:3]
            
            # ✅ NUEVO: Obtener alertas de presupuesto
            now = datetime.now()
            category_alerts = self.db.get_all_category_budget_alerts(
                now.year, 
                now.month
            )

        except Exception as e:
            print(f"❌ ERROR al obtener datos: {e}")
            summary = {
                "total_income": 0,
                "total_expenses": 0,
                "savings": 0,
                "savings_rate": 0,
            }
            expenses_by_category = []
            budget_status = {"budget_exists": False}
            top_expenses = []
            daily_stats = {
                "daily_average": 0,
                "projected_monthly": 0,
                "days_in_month": 30,
                "days_passed": 1,
                "total_expenses": 0,
            }
            week_comparison = {
                "current_week": 0,
                "previous_week": 0,
                "change_percentage": 0,
                "is_increasing": False,
            }
            recent_transactions = []
            category_alerts = []

        # Selector de mes
        month_label = get_month_name(self.current_month)
        month_selector = MonthSelector(
            self.current_month,
            self.current_year,
            self.previous_month,
            self.next_month,
            month_label
        )

        # Tarjeta principal de balance
        savings = summary.get("savings", 0)
        savings_card = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.ACCOUNT_BALANCE_WALLET,
                                size=40,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        "Balance del Mes",
                                        size=14,
                                        color=ft.Colors.WHITE70,
                                    ),
                                    ft.Text(
                                        f"{Config.CURRENCY_SYMBOL} {savings:.2f}",
                                        size=32,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE,
                                    ),
                                ],
                                expand=True,
                                spacing=2,
                            ),
                        ],
                        spacing=15,
                    ),
                    ft.Divider(color=ft.Colors.WHITE30, height=20),
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(
                                        "Ingresos", size=12, color=ft.Colors.WHITE70
                                    ),
                                    ft.Text(
                                        f"{Config.CURRENCY_SYMBOL} {summary.get('total_income', 0):.2f}",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE,
                                    ),
                                ],
                                expand=True,
                            ),
                            ft.Container(width=1, bgcolor=ft.Colors.WHITE30, height=40),
                            ft.Column(
                                [
                                    ft.Text("Gastos", size=12, color=ft.Colors.WHITE70),
                                    ft.Text(
                                        f"{Config.CURRENCY_SYMBOL} {summary.get('total_expenses', 0):.2f}",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE,
                                    ),
                                ],
                                expand=True,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    ),
                ],
                spacing=10,
            ),
            padding=25,
            border_radius=15,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=(
                    ["#667eea", "#764ba2"] if savings >= 0 else ["#f093fb", "#f5576c"]
                ),
            ),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.3, "#667eea"),
                offset=ft.Offset(0, 5),
            ),
        )

        # ✅ CORRECCIÓN: Mini cards como ft.Row directamente, no como tupla
        mini_cards = ft.Row(
            [
                MiniStatCard(
                    "Gasto Diario",
                    f"{Config.CURRENCY_SYMBOL} {daily_stats.get('daily_average', 0):.2f}",
                    ft.Icons.CALENDAR_TODAY,
                    "#3b82f6"
                ),
                MiniStatCard(
                    "Esta Semana",
                    f"{week_comparison.get('change_percentage', 0):+.1f}%",
                    (
                        ft.Icons.TRENDING_UP
                        if not week_comparison.get("is_increasing", False)
                        else ft.Icons.TRENDING_DOWN
                    ),
                    (
                        "#22c55e"
                        if not week_comparison.get("is_increasing", False)
                        else "#ef4444"
                    )
                ),
            ],
            spacing=10,
        )

        # ✅ Ensamblar componentes correctamente
        content_widgets = [
            month_selector,
            ft.Container(height=10),
            savings_card,
            ft.Container(height=15),
            mini_cards,  # ✅ Ya no es tupla
            ft.Container(height=15),
        ]
        
        # ✅ NUEVO: Widget de alertas (si hay alertas)
        if category_alerts:
            content_widgets.append(
                CategoryBudgetAlertWidget(
                    category_alerts,
                    on_click=lambda e: self.show_alerts_detail()
                )
            )
            content_widgets.append(ft.Container(height=15))
        
        # Widget de presupuesto
        content_widgets.append(BudgetSummaryCard(budget_status))

        # Top 3 gastos
        if top_expenses:
            top_section = ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.WORKSPACE_PREMIUM, size=22, color="#f59e0b"
                                ),
                                ft.Text(
                                    "🏆 Top 3 Gastos",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                            spacing=8,
                        ),
                        ft.Container(height=5),
                        *[
                            TopExpenseTile(exp, idx + 1)
                            for idx, exp in enumerate(top_expenses)
                        ],
                    ],
                    spacing=8,
                ),
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
            )
            content_widgets.extend([ft.Container(height=15), top_section])

        # Proyección
        projection_section = ProjectionCard(daily_stats, summary)
        content_widgets.extend([ft.Container(height=15), projection_section])

        # Categorías
        if expenses_by_category:
            category_section = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "📊 Distribución de Gastos",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Container(height=5),
                        *[
                            CompactCategoryBar(cat)
                            for cat in expenses_by_category[:4]
                        ],
                        (
                            ft.TextButton(
                                f"Ver todas ({len(expenses_by_category)})",
                                on_click=lambda _: self.on_nav_change(3),
                                icon=ft.Icons.ARROW_FORWARD,
                            )
                            if len(expenses_by_category) > 4
                            else ft.Container()
                        ),
                    ],
                    spacing=10,
                ),
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
            )
            content_widgets.extend([ft.Container(height=15), category_section])

        # Transacciones recientes
        if recent_transactions:
            recent_section = ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    "🕒 Actividad Reciente",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.TextButton(
                                    "Ver todo",
                                    on_click=lambda _: self.on_nav_change(2),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        *[
                            CompactTransactionTile(t, self.db.get_category_by_id(t.category_id))
                            for t in recent_transactions
                        ],
                    ],
                    spacing=10,
                ),
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
            )
        else:
            recent_section = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(
                            ft.Icons.RECEIPT_LONG_OUTLINED,
                            size=64,
                            color=ft.Colors.GREY_400,
                        ),
                        ft.Text(
                            "No hay transacciones este mes",
                            size=16,
                            color=ft.Colors.GREY_600,
                        ),
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            "Agregar primera transacción",
                            icon=ft.Icons.ADD,
                            on_click=lambda _: self.on_nav_change(1),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=40,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
            )

        content_widgets.extend([ft.Container(height=15), recent_section])
        content_widgets.append(ft.Container(height=30))

        print("✅ Vista HOME ensamblada correctamente")

        return ft.Column(
            content_widgets,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=0,
        )

    def show_alerts_detail(self):
        """
        ✅ NUEVO: Muestra diálogo con detalle de todas las alertas
        """
        from datetime import datetime
        
        now = datetime.now()
        alerts = self.db.get_all_category_budget_alerts(now.year, now.month)
        
        if not alerts:
            self.show_snackbar("✅ No hay alertas de presupuesto")
            return
        
        alert_details = []
        for alert in alerts:
            # Color según severidad
            if alert["alert_type"] == "over_budget":
                theme_color = "#ef4444"
            elif alert["alert_type"] == "danger":
                theme_color = "#f59e0b"
            else:
                theme_color = "#3b82f6"
            
            alert_details.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(alert["icon"], size=24),
                                    ft.Column(
                                        [
                                            ft.Text(
                                                alert["category_name"],
                                                size=15,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                            ft.Text(
                                                f"{alert['percentage_used']:.1f}% usado",
                                                size=12,
                                                color=theme_color,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                        ],
                                        spacing=2,
                                        expand=True,
                                    ),
                                ],
                                spacing=10,
                            ),
                            ft.ProgressBar(
                                value=min(alert["percentage_used"] / 100, 1.0),
                                color=theme_color,
                                bgcolor=ft.Colors.GREY_200,
                                height=6,
                            ),
                            ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text("Presupuesto", size=10, color=ft.Colors.GREY_600),
                                            ft.Text(
                                                f"{Config.CURRENCY_SYMBOL} {alert['assigned_amount']:.2f}",
                                                size=12,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                        ],
                                        spacing=2,
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text("Gastado", size=10, color=ft.Colors.GREY_600),
                                            ft.Text(
                                                f"{Config.CURRENCY_SYMBOL} {alert['spent_amount']:.2f}",
                                                size=12,
                                                weight=ft.FontWeight.BOLD,
                                                color=theme_color,
                                            ),
                                        ],
                                        spacing=2,
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text(
                                                "Disponible" if alert['remaining'] >= 0 else "Excedido",
                                                size=10,
                                                color=ft.Colors.GREY_600
                                            ),
                                            ft.Text(
                                                f"{Config.CURRENCY_SYMBOL} {abs(alert['remaining']):.2f}",
                                                size=12,
                                                weight=ft.FontWeight.BOLD,
                                                color="#22c55e" if alert['remaining'] >= 0 else "#ef4444",
                                            ),
                                        ],
                                        spacing=2,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                            ),
                        ],
                        spacing=10,
                    ),
                    padding=15,
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=10,
                    margin=ft.margin.only(bottom=10),
                )
            )
        
        dialog = ft.AlertDialog(
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.WARNING_AMBER, color="#f59e0b", size=28),
                    ft.Text(
                        f"Alertas de Presupuesto ({len(alerts)})",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                spacing=10,
            ),
            content=ft.Container(
                content=ft.Column(
                    alert_details,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=450,
                height=400,
            ),
            actions=[
                ft.TextButton(
                    "Ir a Categorías",
                    on_click=lambda e: [
                        self.close_dialog(),
                        self.on_nav_change(4)  # Navegar a categorías
                    ],
                ),
                ft.TextButton("Cerrar", on_click=lambda _: self.close_dialog()),
            ],
        )
        
        self.show_dialog(dialog)