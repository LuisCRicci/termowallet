"""
Vista de gráficos y análisis - CON GENERACIÓN DE REPORTES
Archivo: src/ui/charts_view.py

✅ AGREGADO: Botón flotante para generar reportes en Excel/CSV
"""

import flet as ft
from .base_view import BaseView
from .widgets import MonthSelector
from src.utils.config import Config
from src.utils.helpers import get_month_name
from src.business.report_generator import ReportGenerator  # ✅ NUEVO


class ChartsView(BaseView):
    """Vista de gráficos y análisis con generación de reportes"""

    def __init__(self, page: ft.Page, db_manager, show_snackbar_callback,
                 current_month: int, current_year: int,
                 on_month_change: callable):
        super().__init__(page, db_manager, show_snackbar_callback)
        self.current_month = current_month
        self.current_year = current_year
        self.on_month_change = on_month_change
        self.report_generator = ReportGenerator(db_manager)  # ✅ NUEVO

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

    # ✅ NUEVO: Método para mostrar diálogo de generación de reportes
    def show_report_dialog(self, e):
        """Muestra diálogo para seleccionar tipo de reporte"""
        report_type = ft.RadioGroup(
            value="monthly",
            content=ft.Column([
                ft.Radio(value="monthly", label="Reporte Mensual (mes actual)"),
                ft.Radio(value="annual", label="Reporte Anual (año actual)"),
            ])
        )

        format_type = ft.RadioGroup(
            value="xlsx",
            content=ft.Column([
                ft.Radio(value="xlsx", label="📊 Excel (.xlsx) - Recomendado"),
                ft.Radio(value="csv", label="📄 CSV (.csv) - Compatible con todo"),
            ])
        )

        def generate_report(e):
            self.close_dialog()
            self.show_loading("Generando reporte...")

            try:
                if report_type.value == "monthly":
                    result = self.report_generator.generate_monthly_report(
                        year=self.current_year,
                        month=self.current_month,
                        format=format_type.value
                    )
                else:  # annual
                    result = self.report_generator.generate_annual_report(
                        year=self.current_year,
                        format=format_type.value
                    )

                self.close_dialog()  # Cerrar loading

                if result["success"]:
                    self.show_success_dialog(result["filepath"])
                else:
                    self.show_snackbar(result["message"], error=True)

            except Exception as ex:
                self.close_dialog()
                self.show_snackbar(f"Error al generar reporte: {str(ex)}", error=True)

        dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.DESCRIPTION, color="#667eea", size=28),
                ft.Text("Generar Reporte", size=20, weight=ft.FontWeight.BOLD),
            ], spacing=10),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Tipo de Reporte", size=16, weight=ft.FontWeight.BOLD),
                    report_type,
                    ft.Divider(height=20),
                    ft.Text("Formato de Archivo", size=16, weight=ft.FontWeight.BOLD),
                    format_type,
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                "💡 Tip: Los reportes se guardan en tu carpeta de Descargas",
                                size=12,
                                color=ft.Colors.BLUE_700,
                            ),
                            ft.Text(
                                "• Excel: Incluye múltiples hojas (resumen, transacciones, categorías)",
                                size=11,
                                color=ft.Colors.GREY_600,
                            ),
                            ft.Text(
                                "• CSV: Archivos separados para cada sección",
                                size=11,
                                color=ft.Colors.GREY_600,
                            ),
                        ], spacing=5),
                        padding=10,
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=8,
                        margin=ft.margin.only(top=10),
                    ),
                ], spacing=10, tight=True),
                width=450,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.ElevatedButton(
                    "Generar",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=generate_report,
                    style=ft.ButtonStyle(
                        bgcolor="#667eea",
                        color=ft.Colors.WHITE,
                    ),
                ),
            ],
        )

        self.show_dialog(dialog)

    # ✅ NUEVO: Diálogo de éxito con ruta del archivo
    def show_success_dialog(self, filepath: str):
        """Muestra diálogo de éxito con ubicación del archivo"""
        import os

        dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, color="#22c55e", size=32),
                ft.Text("¡Reporte Generado!", size=20, weight=ft.FontWeight.BOLD),
            ], spacing=10),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "El reporte se ha generado exitosamente:",
                        size=14,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                "📁 Ubicación:",
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREY_700,
                            ),
                            ft.Text(
                                filepath,
                                size=12,
                                color=ft.Colors.BLUE_700,
                                selectable=True,
                            ),
                        ], spacing=5),
                        padding=15,
                        bgcolor=ft.Colors.GREY_50,
                        border_radius=8,
                        margin=ft.margin.only(top=10),
                    ),
                    ft.Text(
                        "✅ Puedes abrir el archivo desde tu aplicación de hojas de cálculo favorita",
                        size=12,
                        color=ft.Colors.GREY_600,
                        italic=True,
                    ),
                ], spacing=10, tight=True),
                width=500,
            ),
            actions=[
                ft.ElevatedButton(
                    "Entendido",
                    on_click=lambda _: self.close_dialog(),
                    style=ft.ButtonStyle(
                        bgcolor="#22c55e",
                        color=ft.Colors.WHITE,
                    ),
                ),
            ],
        )

        self.show_dialog(dialog)

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

        # ✅ NUEVO: Configurar FAB en la página
        # Esto se hace en main.py al cargar la vista
        # Pero podemos exponerlo como atributo
        self.fab_config = {
            "icon": ft.Icons.DOWNLOAD,
            "tooltip": "Generar Reporte",
            "on_click": self.show_report_dialog,
            "bgcolor": "#667eea",
        }

        return ft.Column(
            [month_selector, ft.Container(height=10), *charts],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=15,
        )