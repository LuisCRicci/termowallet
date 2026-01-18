"""
Vista de gráficos y análisis - ✅ CON RANGO DE FECHAS FUNCIONAL
Archivo: src/ui/charts_view.py
"""

import flet as ft
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
        
        # Variables de estado para el reporte
        self.pending_report_type = None
        self.pending_format = None
        self.custom_start_date = None
        self.custom_end_date = None

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
        """Muestra diálogo para seleccionar tipo de reporte con rango de fechas"""
        
        # ✅ Variables para almacenar las fechas seleccionadas
        selected_start_date = [None]
        selected_end_date = [None]
        
        # ✅ Textos que mostrarán las fechas seleccionadas
        start_date_text = ft.Text(
            "Selecciona fecha",
            size=14,
            color=ft.Colors.GREY_500,
        )
        
        end_date_text = ft.Text(
            "Selecciona fecha",
            size=14,
            color=ft.Colors.GREY_500,
        )
        
        # ✅ CORRECCIÓN: Funciones para manejar la selección
        def on_start_date_change(ev):
            """Callback cuando cambia la fecha de inicio"""
            if ev.control.value:
                selected_start_date[0] = ev.control.value
                start_date_text.value = ev.control.value.strftime("%d/%m/%Y")
                start_date_text.color = ft.Colors.BLACK
                start_date_text.update()
                print(f"📅 Fecha inicio: {start_date_text.value}")
        
        def on_end_date_change(ev):
            """Callback cuando cambia la fecha de fin"""
            if ev.control.value:
                selected_end_date[0] = ev.control.value
                end_date_text.value = ev.control.value.strftime("%d/%m/%Y")
                end_date_text.color = ft.Colors.BLACK
                end_date_text.update()
                print(f"📅 Fecha fin: {end_date_text.value}")
        
        # ✅ CORRECCIÓN: DatePickers en ESPAÑOL
        start_date_picker = ft.DatePicker(
            on_change=on_start_date_change,
            first_date=datetime(2020, 1, 1),
            last_date=datetime.now() + timedelta(days=365),
            # 🌐 Configuración en español
            cancel_text="Cancelar",
            confirm_text="Aceptar",
            help_text="Selecciona la fecha de inicio",
            field_label_text="Fecha",
        )
        
        end_date_picker = ft.DatePicker(
            on_change=on_end_date_change,
            first_date=datetime(2020, 1, 1),
            last_date=datetime.now() + timedelta(days=365),
            # 🌐 Configuración en español
            cancel_text="Cancelar",
            confirm_text="Aceptar",
            help_text="Selecciona la fecha de fin",
            field_label_text="Fecha",
        )
        
        # ✅ CORRECCIÓN: Funciones para abrir los pickers
        def open_start_picker(e):
            """Abre el picker de fecha de inicio"""
            start_date_picker.open = True
            self.page.update()
        
        def open_end_picker(e):
            """Abre el picker de fecha de fin"""
            end_date_picker.open = True
            self.page.update()
        
        # Agregar DatePickers al overlay
        self.page.overlay.append(start_date_picker)
        self.page.overlay.append(end_date_picker)
        self.page.update()
        
        # ✅ Botones para abrir los DatePickers
        start_date_button = ft.OutlinedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.CALENDAR_TODAY, size=20),
                start_date_text,
            ], spacing=10),
            on_click=open_start_picker,  # ✅ Usar función sin paréntesis
            width=200,
            height=50,
        )
        
        end_date_button = ft.OutlinedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.CALENDAR_TODAY, size=20),
                end_date_text,
            ], spacing=10),
            on_click=open_end_picker,  # ✅ Usar función sin paréntesis
            width=200,
            height=50,
        )
        
        # Contenedor para el rango de fechas (inicialmente oculto)
        date_range_container = ft.Container(
            content=ft.Column([
                ft.Text("Fecha de inicio", size=12, color=ft.Colors.GREY_700, weight=ft.FontWeight.BOLD),
                start_date_button,
                ft.Container(height=10),
                ft.Text("Fecha de fin", size=12, color=ft.Colors.GREY_700, weight=ft.FontWeight.BOLD),
                end_date_button,
                ft.Container(
                    content=ft.Text(
                        "💡 Toca los botones para seleccionar las fechas",
                        size=11,
                        color=ft.Colors.GREY_600,
                        italic=True,
                    ),
                    padding=ft.padding.only(top=5),
                ),
            ], spacing=5),
            visible=False,
            padding=ft.padding.only(top=10, bottom=10),
        )
        
        def on_report_type_change(e):
            """Muestra/oculta el selector de fechas según el tipo de reporte"""
            date_range_container.visible = (report_type.value == "custom")
            date_range_container.update()
        
        report_type = ft.RadioGroup(
            value="monthly",
            on_change=on_report_type_change,
            content=ft.Column([
                ft.Radio(
                    value="monthly", 
                    label=f"📅 Mes actual ({get_month_name(self.current_month)} {self.current_year})"
                ),
                ft.Radio(
                    value="annual", 
                    label=f"📆 Año actual ({self.current_year})"
                ),
                ft.Radio(
                    value="custom",
                    label="📊 Rango personalizado"
                ),
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
            """Genera el reporte con validación de fechas"""
            
            # Validar rango personalizado si está seleccionado
            if report_type.value == "custom":
                if not selected_start_date[0] or not selected_end_date[0]:
                    self.show_snackbar(
                        "❌ Por favor selecciona ambas fechas",
                        error=True
                    )
                    return
                
                # Validar que la fecha de inicio sea menor que la de fin
                if selected_start_date[0] > selected_end_date[0]:
                    self.show_snackbar(
                        "❌ La fecha de inicio debe ser anterior a la fecha de fin",
                        error=True
                    )
                    return
                
                # Guardar fechas
                self.custom_start_date = selected_start_date[0]
                self.custom_end_date = selected_end_date[0]
            
            # Cerrar diálogo y limpiar DatePickers
            try:
                self.page.overlay.remove(start_date_picker)
                self.page.overlay.remove(end_date_picker)
            except:
                pass
            
            self.close_dialog()
            
            self.pending_report_type = report_type.value
            self.pending_format = format_type.value
            
            print(f"\n{'='*60}")
            print(f"📋 GENERANDO REPORTE")
            print(f"{'='*60}")
            print(f"   Tipo: {self.pending_report_type}")
            print(f"   Formato: {self.pending_format}")
            if self.pending_report_type == "custom":
                print(f"   Desde: {self.custom_start_date.strftime('%d/%m/%Y')}")
                print(f"   Hasta: {self.custom_end_date.strftime('%d/%m/%Y')}")
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
            elif self.pending_report_type == "annual":
                self.report_generator.generate_annual_report(
                    year=self.current_year,
                    format=self.pending_format,
                    callback_success=self._on_report_success,
                    callback_error=self._on_report_error
                )
            elif self.pending_report_type == "custom":
                self.report_generator.generate_custom_range_report(
                    start_date=self.custom_start_date,
                    end_date=self.custom_end_date,
                    format=self.pending_format,
                    callback_success=self._on_report_success,
                    callback_error=self._on_report_error
                )

        def close_dialog_and_cleanup(e):
            """Cierra el diálogo y limpia los DatePickers"""
            try:
                self.page.overlay.remove(start_date_picker)
                self.page.overlay.remove(end_date_picker)
            except:
                pass
            self.close_dialog()

        dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.DESCRIPTION, color="#667eea", size=28),
                ft.Text("Generar Reporte", size=20, weight=ft.FontWeight.BOLD),
            ], spacing=10),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Selecciona el período", size=16, weight=ft.FontWeight.BOLD),
                    report_type,
                    date_range_container,
                    ft.Divider(height=20),
                    ft.Text("Formato de archivo", size=16, weight=ft.FontWeight.BOLD),
                    format_type,
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                "📱 En Desktop: Podrás elegir dónde guardar",
                                size=12,
                                color=ft.Colors.BLUE_700,
                            ) if not Config.is_android() else ft.Text(
                                "💻 En Android: Podrás elegir dónde guardar",
                                size=12,
                                color=ft.Colors.BLUE_700,
                            ),
                            ft.Text(
                                "• Excel: Incluye múltiples hojas con análisis detallado",
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
                ], spacing=10, tight=True, scroll=ft.ScrollMode.AUTO),
                width=480,
                height=600,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog_and_cleanup),
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
        
        self.close_dialog()
        self.show_success_dialog(filepath, message)
    
    def _on_report_error(self, error_message: str):
        """Callback cuando hay error al generar reporte"""
        print(f"❌ Error: {error_message}")
        
        self.close_dialog()
        self.show_snackbar(error_message, error=True)
    
    def show_success_dialog(self, filepath: str, message: str):
        """Muestra diálogo de éxito con opciones"""
        
        is_in_downloads = "/Download/" in filepath or "/download/" in filepath.lower()
        
        content_items = [
            ft.Text(message, size=14, selectable=True),
        ]
        
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
                            ft.Text("1. Abre la app 'Archivos' o 'Mis archivos'", size=12, color=ft.Colors.GREY_700),
                            ft.Text("2. Ve a 'Descargas' o 'Download'", size=12, color=ft.Colors.GREY_700),
                            ft.Text("3. Busca tu reporte", size=12, color=ft.Colors.GREY_700),
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
                    content=ft.Text(
                        "✅ Puedes abrir el archivo directamente desde tu explorador",
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
                content=ft.Column(content_items, spacing=10, tight=True),
                width=500,
            ),
            actions=[
                ft.ElevatedButton(
                    "Entendido",
                    on_click=lambda _: self.close_dialog(),
                    style=ft.ButtonStyle(bgcolor="#22c55e", color=ft.Colors.WHITE),
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
                                ft.Text(item["category"], size=14, weight=ft.FontWeight.BOLD),
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
                        ft.Text(f"{percentage:.1f}%", size=12, color=ft.Colors.GREY_600),
                    ], spacing=5),
                    padding=10,
                    margin=ft.margin.only(bottom=10),
                )
            )

        return ft.Container(
            content=ft.Column([
                ft.Text("💸 Gastos por Categoría", size=18, weight=ft.FontWeight.BOLD),
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
                        ft.Text(f"{m['month_name'][:3]}", size=12, weight=ft.FontWeight.BOLD, width=40),
                        ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.ARROW_UPWARD, size=14, color="#22c55e"),
                                ft.Text(f"{Config.CURRENCY_SYMBOL} {m['total_income']:.0f}", size=13),
                            ], spacing=5),
                            ft.Row([
                                ft.Icon(ft.Icons.ARROW_DOWNWARD, size=14, color="#ef4444"),
                                ft.Text(f"{Config.CURRENCY_SYMBOL} {m['total_expenses']:.0f}", size=13),
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
                ft.Text("📈 Últimos 12 Meses", size=18, weight=ft.FontWeight.BOLD),
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
                    ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, size=28, color="#8b5cf6"),
                    ft.Text("💎 Ahorro Total Consolidado", size=18, weight=ft.FontWeight.BOLD),
                ], spacing=10),
                ft.Divider(height=10),
                ft.Row([
                    ft.Column([
                        ft.Text("Total Ingresos", size=12, color=ft.Colors.GREY_600),
                        ft.Text(
                            f"{Config.CURRENCY_SYMBOL} {total_income:.2f}",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color="#22c55e"
                        ),
                    ], expand=True),
                    ft.Column([
                        ft.Text("Total Gastos", size=12, color=ft.Colors.GREY_600),
                        ft.Text(
                            f"{Config.CURRENCY_SYMBOL} {total_expenses:.2f}",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color="#ef4444"
                        ),
                    ], expand=True),
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                ft.Divider(height=5),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Ahorro Neto", size=14, color=ft.Colors.GREY_700, text_align=ft.TextAlign.CENTER),
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
                ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=ft.Colors.GREY_500),
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
        summary = self.db.get_monthly_summary(self.current_year, self.current_month)
        expenses_by_category = self.db.get_expenses_by_category(self.current_year, self.current_month)
        monthly_trend = self.db.get_monthly_trend_from_date(self.current_year, self.current_month, months=12)
        total_stats = self.db.get_total_statistics()

        month_label = get_month_name(self.current_month)
        month_selector = MonthSelector(
            self.current_month,
            self.current_year,
            self.previous_month,
            self.next_month,
            month_label
        )

        reports_button = ft.Container(
            content=ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.DOWNLOAD, size=20),
                    ft.Text("Generar Reporte", size=15, weight=ft.FontWeight.BOLD),
                ], spacing=10, tight=True),
                on_click=self.show_report_dialog,
                style=ft.ButtonStyle(bgcolor="#667eea", color=ft.Colors.WHITE, padding=15),
                height=50,
            ),
            margin=ft.margin.only(bottom=15),
        )

        summary_card = ft.Container(
            content=ft.Column([
                ft.Text("📊 Resumen del Mes", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text(f"💰 Ingresos: {Config.CURRENCY_SYMBOL} {summary['total_income']:.2f}", size=16),
                ft.Text(f"💸 Gastos: {Config.CURRENCY_SYMBOL} {summary['total_expenses']:.2f}", size=16),
                ft.Text(
                    f"💎 Ahorro: {Config.CURRENCY_SYMBOL} {summary['savings']:.2f}",
                    size=16,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text(f"📈 Tasa de Ahorro: {summary['savings_rate']:.1f}%", size=16),
            ]),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
        )

        charts = [summary_card]

        if expenses_by_category:
            charts.append(self._create_category_chart(expenses_by_category))

        if monthly_trend:
            charts.append(self._create_trend_chart(monthly_trend))

        if total_stats and total_stats.get("transaction_count", 0) > 0:
            charts.append(self._create_total_savings_card(total_stats))

        return ft.Column(
            [month_selector, ft.Container(height=10), reports_button, *charts],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=15,
        )