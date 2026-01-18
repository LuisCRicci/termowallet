"""
Vista de gráficos y análisis - ✅ COMPATIBLE CON ANDROID
Archivo: src/ui/charts_view.py

✅ Adaptado para funcionar correctamente en Android y Desktop
"""

import sys
import flet as ft
import os
from datetime import datetime, timedelta
from .base_view import BaseView
from .widgets import MonthSelector
from src.utils.config import Config
from src.utils.helpers import get_month_name
from src.business.report_generator import ReportGenerator


class ChartsView(BaseView):
    """Vista de gráficos y análisis con generación de reportes"""

    def __init__(self, page: ft.Page, db_manager, show_snackbar_callback,
                 current_month: int, current_year: int,
                 on_month_change: callable):
        super().__init__(page, db_manager, show_snackbar_callback)
        self.current_month = current_month
        self.current_year = current_year
        self.on_month_change = on_month_change
        self.report_generator = ReportGenerator(db_manager, page=self.page)
        
        # Variables de estado
        self.pending_report_type = None
        self.pending_format = None

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
            """Genera el reporte directamente"""
            self.close_dialog()
            
            self.pending_report_type = report_type.value
            self.pending_format = format_type.value
            
            print(f"\n{'='*60}")
            print(f"📋 GENERANDO REPORTE")
            print(f"{'='*60}")
            print(f"   Tipo: {self.pending_report_type}")
            print(f"   Formato: {self.pending_format}")
            print(f"   Plataforma: {'Android' if Config.is_android() else 'Desktop'}")
            print(f"{'='*60}\n")
            
            # Mostrar loading
            self.show_loading("Generando reporte...")
            
            # Generar según tipo
            if self.pending_report_type == "monthly":
                self.report_generator.generate_monthly_report(
                    year=self.current_year,
                    month=self.current_month,
                    format=self.pending_format,
                    callback_success=self._on_report_success,
                    callback_error=self._on_report_error
                )
            else:  # annual
                self.show_snackbar(
                    "Reporte anual en desarrollo",
                    error=False
                )
                self.close_dialog()

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
                                "📱 En Android: Se guardará en Descargas/TermoWallet",
                                size=12,
                                color=ft.Colors.BLUE_700,
                            ) if Config.is_android() else ft.Text(
                                "💻 En Desktop: Podrás elegir dónde guardar",
                                size=12,
                                color=ft.Colors.BLUE_700,
                            ),
                            ft.Text(
                                "• Excel: Incluye múltiples hojas (resumen, transacciones, categorías)",
                                size=11,
                                color=ft.Colors.GREY_600,
                            ),
                            ft.Text(
                                "• CSV: Archivo simple compatible con todo",
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
                    "Generar Reporte",
                    icon=ft.Icons.SAVE,
                    on_click=generate_report,
                    style=ft.ButtonStyle(
                        bgcolor="#667eea",
                        color=ft.Colors.WHITE,
                    ),
                ),
            ],
        )

        self.show_dialog(dialog)
    
    def _on_report_success(self, filepath: str, message: str):
        """Callback cuando el reporte se genera exitosamente"""
        print(f"✅ Reporte generado: {filepath}")
        
        self.close_dialog()  # Cerrar loading
        
        # Mostrar diálogo de éxito
        self.show_success_dialog(filepath, message)
    
    def _on_report_error(self, error_message: str):
        """Callback cuando hay error al generar reporte"""
        print(f"❌ Error: {error_message}")
        
        self.close_dialog()  # Cerrar loading
        self.show_snackbar(error_message, error=True)
    
    def show_success_dialog(self, filepath: str, message: str):
        """Muestra diálogo de éxito con opciones"""
        
        # Determinar si el archivo está en Downloads
        is_in_downloads = "/Download/" in filepath or "/download/" in filepath.lower()
        
        # Contenido del diálogo
        content_items = [
            ft.Text(
                message,
                size=14,
                selectable=True,
            ),
        ]
        
        # Instrucciones adicionales según plataforma
        if Config.is_android():
            if is_in_downloads:
                content_items.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                "📱 Cómo acceder al archivo:",
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_700,
                            ),
                            ft.Text(
                                "1. Abre la app 'Archivos' o 'Mis archivos'",
                                size=12,
                                color=ft.Colors.GREY_700,
                            ),
                            ft.Text(
                                "2. Ve a 'Descargas' o 'Download'",
                                size=12,
                                color=ft.Colors.GREY_700,
                            ),
                            ft.Text(
                                "3. Busca la carpeta 'TermoWallet'",
                                size=12,
                                color=ft.Colors.GREY_700,
                            ),
                            ft.Text(
                                "4. Ahí encontrarás tu reporte",
                                size=12,
                                color=ft.Colors.GREY_700,
                            ),
                        ], spacing=5),
                        padding=15,
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=8,
                        margin=ft.margin.only(top=10),
                    )
                )
            else:
                content_items.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                "⚠️ Archivo en almacenamiento interno",
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.ORANGE_700,
                            ),
                            ft.Text(
                                "• Conecta tu dispositivo por USB al PC",
                                size=12,
                                color=ft.Colors.GREY_700,
                            ),
                            ft.Text(
                                "• Navega a la ruta mostrada arriba",
                                size=12,
                                color=ft.Colors.GREY_700,
                            ),
                            ft.Text(
                                "• Copia el archivo a tu PC",
                                size=12,
                                color=ft.Colors.GREY_700,
                            ),
                        ], spacing=5),
                        padding=15,
                        bgcolor=ft.Colors.ORANGE_50,
                        border_radius=8,
                        margin=ft.margin.only(top=10),
                    )
                )
        else:
            # Desktop
            content_items.append(
                ft.Container(
                    content=ft.Text(
                        "✅ Puedes abrir el archivo directamente desde tu explorador de archivos",
                        size=12,
                        color=ft.Colors.GREY_600,
                        italic=True,
                    ),
                    padding=10,
                    bgcolor=ft.Colors.GREEN_50,
                    border_radius=8,
                    margin=ft.margin.only(top=10),
                )
            )
        
        dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, color="#22c55e", size=32),
                ft.Text("¡Reporte Generado!", size=20, weight=ft.FontWeight.BOLD),
            ], spacing=10),
            content=ft.Container(
                content=ft.Column(
                    content_items,
                    spacing=10,
                    tight=True
                ),
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
                    content=ft.Column([
                        ft.Row([
                            ft.Row([
                                ft.Text(item["icon"], size=20),
                                ft.Text(
                                    item["category"],
                                    size=14,
                                    weight=ft.FontWeight.BOLD
                                ),
                            ], spacing=5),
                            ft.Text(
                                f"{Config.CURRENCY_SYMBOL} {item['total']:.2f}",
                                size=14,
                                color=ft.Colors.GREY_700
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.ProgressBar(
                            value=percentage / 100,
                            color=item["color"],
                            bgcolor="#e5e7eb",
                            height=8
                        ),
                        ft.Text(
                            f"{percentage:.1f}%",
                            size=12,
                            color=ft.Colors.GREY_600
                        ),
                    ], spacing=5),
                    padding=10,
                    margin=ft.margin.only(bottom=10),
                )
            )

        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "💸 Gastos por Categoría",
                    size=18,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Container(height=10),
                ft.Column(bars),
            ], spacing=5),
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
                    content=ft.Row([
                        ft.Text(
                            f"{m['month_name'][:3]}",
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            width=40
                        ),
                        ft.Column([
                            ft.Row([
                                ft.Icon(
                                    ft.Icons.ARROW_UPWARD,
                                    size=14,
                                    color="#22c55e"
                                ),
                                ft.Text(
                                    f"{Config.CURRENCY_SYMBOL} {m['total_income']:.0f}",
                                    size=13
                                ),
                            ], spacing=5),
                            ft.Row([
                                ft.Icon(
                                    ft.Icons.ARROW_DOWNWARD,
                                    size=14,
                                    color="#ef4444"
                                ),
                                ft.Text(
                                    f"{Config.CURRENCY_SYMBOL} {m['total_expenses']:.0f}",
                                    size=13
                                ),
                            ], spacing=5),
                        ], expand=True, spacing=2),
                        ft.Container(
                            content=ft.Text(
                                f"{m['savings_rate']:.0f}%",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=savings_rate_color
                            ),
                            bgcolor=f"{savings_rate_color}20",
                            padding=8,
                            border_radius=8,
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=10,
                    margin=ft.margin.only(bottom=5),
                    bgcolor="#f9fafb",
                    border_radius=8,
                )
            )

        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "📈 Últimos 12 Meses",
                    size=18,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Container(height=10),
                ft.Column(trend_items),
            ], spacing=5),
            padding=15,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
        )

    def _create_total_savings_card(self, total_stats: dict):
        """Crea tarjeta de ahorro total consolidado"""
        total_income = total_stats.get("total_income", 0)
        total_expenses = total_stats.get("total_expenses", 0)
        total_savings = total_income - total_expenses
        savings_rate = (total_savings / total_income * 100) if total_income > 0 else 0
        
        # Determinar color según la tasa de ahorro
        if savings_rate >= 20:
            rate_color = "#22c55e"
            rate_icon = ft.Icons.TRENDING_UP
            rate_text = "Excelente"
        elif savings_rate >= 10:
            rate_color = "#3b82f6"
            rate_icon = ft.Icons.REMOVE
            rate_text = "Bueno"
        elif savings_rate >= 0:
            rate_color = "#f59e0b"
            rate_icon = ft.Icons.TRENDING_DOWN
            rate_text = "Regular"
        else:
            rate_color = "#ef4444"
            rate_icon = ft.Icons.ARROW_DOWNWARD
            rate_text = "Déficit"

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(
                        ft.Icons.ACCOUNT_BALANCE_WALLET,
                        size=28,
                        color="#8b5cf6"
                    ),
                    ft.Text(
                        "💎 Ahorro Total Consolidado",
                        size=18,
                        weight=ft.FontWeight.BOLD
                    ),
                ], spacing=10),
                ft.Divider(height=10),
                
                # Valores principales
                ft.Row([
                    ft.Column([
                        ft.Text(
                            "Total Ingresos",
                            size=12,
                            color=ft.Colors.GREY_600
                        ),
                        ft.Text(
                            f"{Config.CURRENCY_SYMBOL} {total_income:.2f}",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color="#22c55e"
                        ),
                    ], expand=True),
                    ft.Column([
                        ft.Text(
                            "Total Gastos",
                            size=12,
                            color=ft.Colors.GREY_600
                        ),
                        ft.Text(
                            f"{Config.CURRENCY_SYMBOL} {total_expenses:.2f}",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color="#ef4444"
                        ),
                    ], expand=True),
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                
                ft.Divider(height=5),
                
                # Ahorro total
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "Ahorro Neto",
                            size=14,
                            color=ft.Colors.GREY_700,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Text(
                            f"{Config.CURRENCY_SYMBOL} {total_savings:.2f}",
                            size=32,
                            weight=ft.FontWeight.BOLD,
                            color=rate_color,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Row([
                            ft.Icon(rate_icon, size=20, color=rate_color),
                            ft.Text(
                                f"Tasa: {savings_rate:.1f}% - {rate_text}",
                                size=14,
                                color=rate_color,
                                weight=ft.FontWeight.BOLD
                            ),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    bgcolor=f"{rate_color}15",
                    padding=15,
                    border_radius=10,
                ),
                
                # Info adicional
                ft.Row([
                    ft.Icon(
                        ft.Icons.INFO_OUTLINE,
                        size=16,
                        color=ft.Colors.GREY_500
                    ),
                    ft.Text(
                        f"Basado en {total_stats.get('transaction_count', 0)} transacciones totales",
                        size=11,
                        color=ft.Colors.GREY_600,
                        italic=True,
                    ),
                ], spacing=5),
            ], spacing=10),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
        )

    def build(self) -> ft.Control:
        """Construye la vista de gráficos"""
        # Datos del mes actual
        summary = self.db.get_monthly_summary(self.current_year, self.current_month)
        expenses_by_category = self.db.get_expenses_by_category(
            self.current_year,
            self.current_month
        )
        
        # Tendencia dinámica
        monthly_trend = self.db.get_monthly_trend_from_date(
            self.current_year, 
            self.current_month, 
            months=12
        )
        
        # Estadísticas totales consolidadas
        total_stats = self.db.get_total_statistics()

        month_label = get_month_name(self.current_month)
        month_selector = MonthSelector(
            self.current_month,
            self.current_year,
            self.previous_month,
            self.next_month,
            month_label
        )

        # Botón de reportes
        reports_button = ft.Container(
            content=ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.DOWNLOAD, size=20),
                    ft.Text("Generar Reporte", size=15, weight=ft.FontWeight.BOLD),
                ], spacing=10, tight=True),
                on_click=self.show_report_dialog,
                style=ft.ButtonStyle(
                    bgcolor="#667eea",
                    color=ft.Colors.WHITE,
                    padding=15,
                ),
                height=50,
            ),
            margin=ft.margin.only(bottom=15),
        )

        # Tarjeta de resumen del mes
        summary_card = ft.Container(
            content=ft.Column([
                ft.Text(
                    "📊 Resumen del Mes",
                    size=20,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Divider(),
                ft.Text(
                    f"💰 Ingresos: {Config.CURRENCY_SYMBOL} {summary['total_income']:.2f}",
                    size=16
                ),
                ft.Text(
                    f"💸 Gastos: {Config.CURRENCY_SYMBOL} {summary['total_expenses']:.2f}",
                    size=16
                ),
                ft.Text(
                    f"💎 Ahorro: {Config.CURRENCY_SYMBOL} {summary['savings']:.2f}",
                    size=16,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text(
                    f"📈 Tasa de Ahorro: {summary['savings_rate']:.1f}%",
                    size=16
                ),
            ]),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
        )

        charts = [summary_card]

        # Gastos por categoría
        if expenses_by_category:
            charts.append(self._create_category_chart(expenses_by_category))

        # Tendencia mensual dinámica
        if monthly_trend:
            charts.append(self._create_trend_chart(monthly_trend))

        # Tarjeta de ahorro total
        if total_stats and total_stats.get("transaction_count", 0) > 0:
            charts.append(self._create_total_savings_card(total_stats))

        return ft.Column(
            [
                month_selector,
                ft.Container(height=10),
                reports_button,
                *charts
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=15,
        )