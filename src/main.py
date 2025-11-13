"""
Aplicación Principal - Dashboard de Gastos Personales
Archivo: src/main.py

Ejecutar con: flet run src/main.py
VERSIÓN CON LIMPIEZA DE BASE DE DATOS
"""

import sys
import os

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import flet as ft
from datetime import datetime
from src.data.database import DatabaseManager
from src.business.processor import TransactionProcessor
from src.utils.config import Config


class ExpenseTrackerApp:
    def __init__(self, page: ft.Page):
        self.page = page

        print("🚀 Inicializando TermoWallet...")

        # self.db = DatabaseManager()

        try:
            self.db = DatabaseManager(Config.get_db_path())
            print("✅ Base de datos inicializada")
        except Exception as e:
            print(f"❌ Error inicializando BD: {e}")
            import traceback

            traceback.print_exc()

        self.processor = TransactionProcessor()

        # Configuración de la página
        self.page.title = Config.APP_NAME
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.bgcolor = "#f5f5f5"

        # Estado actual
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        self.current_view = "home"

        # Inicializar UI
        self.setup_ui()
        self.load_home_view()

    def setup_ui(self):
        """Configura la estructura principal de la UI"""
        # App Bar
        self.page.appbar = ft.AppBar(
            title=ft.Text(f"💰 {Config.APP_NAME}", size=20, weight=ft.FontWeight.BOLD),
            center_title=True,
            bgcolor=Config.PRIMARY_COLOR,
            color=ft.Colors.WHITE,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    icon_color=ft.Colors.WHITE,
                    on_click=lambda _: self.refresh_current_view(),
                    tooltip="Actualizar",
                )
            ],
        )

        # Contenedor principal
        self.main_container = ft.Container(
            content=ft.Column([]),
            expand=True,
            padding=10,
            bgcolor="#f5f5f5",
        )

        # Navigation Bar con ícono de configuración
        self.nav_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Inicio"),
                ft.NavigationBarDestination(icon=ft.Icons.ADD_CIRCLE, label="Añadir"),
                ft.NavigationBarDestination(icon=ft.Icons.LIST, label="Historial"),
                ft.NavigationBarDestination(icon=ft.Icons.PIE_CHART, label="Gráficos"),
                ft.NavigationBarDestination(icon=ft.Icons.CATEGORY, label="Categorías"),
                ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Ajustes"),
            ],
            on_change=self.on_nav_change,
            selected_index=0,
        )

        # Layout principal
        self.page.add(
            ft.Column([self.main_container, self.nav_bar], expand=True, spacing=0)
        )

    def on_nav_change(self, e):
        """Maneja el cambio de navegación"""
        selected = e.control.selected_index

        if selected == 0:
            self.load_home_view()
        elif selected == 1:
            self.load_add_transaction_view()
        elif selected == 2:
            self.load_history_view()
        elif selected == 3:
            self.load_charts_view()
        elif selected == 4:
            self.load_categories_view()
        elif selected == 5:
            self.load_settings_view()

    # ========== VISTA: HOME ==========
    def load_home_view(self):
        """Vista principal con resumen mensual"""
        print("\n" + "=" * 60)
        print("🏠 CARGANDO VISTA HOME")
        print("=" * 60)

        self.current_view = "home"
        self.page.floating_action_button = None  # Remover FAB si existe

        summary = self.db.get_monthly_summary(self.current_year, self.current_month)
        expenses_by_category = self.db.get_expenses_by_category(
            self.current_year, self.current_month
        )
        monthly_trend = self.db.get_monthly_trend(6)

        # Selector de mes
        month_selector = ft.Row(
            [
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=self.previous_month),
                ft.Text(
                    f"{datetime(self.current_year, self.current_month, 1).strftime('%B %Y')}",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    expand=True,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.IconButton(icon=ft.Icons.ARROW_FORWARD, on_click=self.next_month),
            ]
        )

        # Resumen del mes
        summary_card = ft.Container(
            content=ft.Column(
                [
                    ft.Text("📊 Resumen del Mes", size=30, weight=ft.FontWeight.BOLD),
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

        # Gráfico de gastos por categoría
        if expenses_by_category:
            category_chart = self._create_category_chart(expenses_by_category)
            charts.append(category_chart)

        # Tendencia mensual
        if monthly_trend:
            trend_chart = self._create_trend_chart(monthly_trend)
            charts.append(trend_chart)

        self.main_container.content = ft.Column(
            [month_selector, ft.Container(height=10), *charts],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=15,
        )

        self.page.update()

        """ solucion tem,poral
        try:
            print(
                f"📊 Obteniendo resumen para {self.current_month}/{self.current_year}"
            )
            summary = self.db.get_monthly_summary(self.current_year, self.current_month)

            print(f"✅ Summary obtenido: {summary}")
            # Validar que summary no sea None
            if summary is None:
                summary = {
                    "total_income": 0.0,
                    "total_expenses": 0.0,
                    "savings": 0.0,
                    "savings_rate": 0.0,
                    "month_name": datetime(
                        self.current_year, self.current_month, 1
                    ).strftime("%B"),
                    "transaction_count": 0,
                }

            print(f"💰 Ingresos: {summary.get('total_income', 0)}")
            print(f"💸 Gastos: {summary.get('total_expenses', 0)}")
            print(f"💎 Ahorro: {summary.get('savings', 0)}")

            # Tarjetas de resumen
            income_card = self._create_summary_card(
                "Ingresos",
                f"{Config.CURRENCY_SYMBOL} {summary.get('total_income', 0.0):.2f}",
                ft.Icons.TRENDING_UP,
                "#22c55e",
            )

            expense_card = self._create_summary_card(
                "Gastos",
                f"{Config.CURRENCY_SYMBOL} {summary.get('total_expenses', 0.0):.2f}",
                ft.Icons.TRENDING_DOWN,
                "#ef4444",
            )

            savings_card = self._create_summary_card(
                "Ahorro",
                f"{Config.CURRENCY_SYMBOL} {summary.get('savings', 0.0):.2f}",
                ft.Icons.SAVINGS,
                "#3b82f6" if summary.get("savings", 0.0) >= 0 else "#f97316",
            )

            # Selector de mes
            month_selector = ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK, on_click=self.previous_month
                    ),
                    ft.Text(
                        f"{datetime(self.current_year, self.current_month, 1).strftime('%B %Y')}",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        expand=True,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ARROW_FORWARD, on_click=self.next_month
                    ),
                ]
            )

            # Indicador de tasa de ahorro
            savings_rate = summary.get("savings_rate", 0.0)
            savings_color = "#22c55e" if savings_rate > 20 else "#f97316"

            savings_indicator = ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Tasa de Ahorro", size=16, weight=ft.FontWeight.BOLD),
                        ft.ProgressBar(
                            value=max(0, min(savings_rate / 100, 1)),
                            color=savings_color,
                            bgcolor="#e5e7eb",
                            height=10,
                        ),
                        ft.Text(
                            f"{savings_rate:.1f}%",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=savings_color,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
                border_radius=10,
                bgcolor=ft.Colors.WHITE,
            )

            
            print("📋 Obteniendo transacciones recientes...")
            
            # Últimas transacciones - CON MEJOR MANEJO DE ERRORES
            try:
                recent_transactions = self.db.get_transactions_by_month(
                    self.current_year, self.current_month
                )[:5]

                print(f"✅ {len(recent_transactions)} transacciones encontradas")

            except Exception as e:
                print(f"Error obteniendo transacciones: {e}")
                recent_transactions = []

            if recent_transactions:
                print("📝 Creando lista de transacciones...")
                transaction_tiles = []
                for i, t in enumerate(recent_transactions):
                    if t is not None:
                        try:
                            tile = self._create_transaction_tile(t)
                            transaction_tiles.append(tile)
                            print(f"  ✓ Tile {i+1} creado")
                        except Exception as e:
                            print(f"  ✗ Error en tile {i+1}: {e}")

                transactions_list = ft.Column(
                    [
                        ft.Text(
                            "Transacciones Recientes",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),
                        *transaction_tiles,
                    ],
                    spacing=5,
                )
            else:
                print("📭 No hay transacciones, mostrando mensaje vacío")
                transactions_list = ft.Container(
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
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    padding=40,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                )

            # Actualizar contenedor principal
            print("🎨 Actualizando contenedor principal...")
            self.main_container.content = ft.Column(
                [
                    month_selector,
                    ft.Container(height=10),
                    ft.Row(
                        [income_card, expense_card, savings_card], wrap=True, spacing=10
                    ),
                    ft.Container(height=10),
                    savings_indicator,
                    ft.Divider(height=20),
                    transactions_list,
                ],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            )

            print("🔄 Actualizando página...")
            self.page.update()
            print("✅ Vista Home cargada exitosamente")
            print("=" * 60 + "\n")

        except Exception as e:
            print(f"\n❌ ERROR CRÍTICO EN LOAD_HOME_VIEW:")
            print(f"   Tipo: {type(e).__name__}")
            print(f"   Mensaje: {str(e)}")
            import traceback

            print("\n📍 TRACEBACK COMPLETO:")
            traceback.print_exc()
            print("=" * 60 + "\n")

            # Mostrar mensaje de error al usuario
            self.main_container.content = ft.Column(
                [
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=64, color=ft.Colors.RED),
                    ft.Text(
                        "Error al cargar la vista",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.RED,
                    ),
                    ft.Text(
                        str(e),
                        size=14,
                        color=ft.Colors.GREY_700,
                    ),
                    # PARA VER DETALLES EN CONSOLA
                    ft.ElevatedButton(
                        "Ver detalles en consola",
                        on_click=lambda _: print(traceback.format_exc()),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
            )
            self.page.update()
        
        """

    def _create_summary_card(self, title: str, value: str, icon, color: str):
        """Crea una tarjeta de resumen"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=40, color=color),
                    ft.Text(title, size=14, color=ft.Colors.WHITE),
                    ft.Text(value, size=18, weight=ft.FontWeight.BOLD),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.INDIGO_300,
            expand=True,
            height=130,
        )

    def _create_transaction_tile(self, transaction):
        """Crea un tile para una transacción - MEJORADO CON MANEJO DE NONE"""
        try:
            # Validar que transaction no sea None
            if transaction is None:
                print("  ⚠️  Transaction es None")
                return ft.Container()

            print(f"  📌 Procesando transacción ID: {transaction.id}")

            category = self.db.get_category_by_id(transaction.category_id)

            # Valores por defecto seguros
            if category is None:
                print(f"  ⚠️  Categoría {transaction.category_id} no encontrada")
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

            try:
                date_str = transaction.date.strftime(Config.DATE_FORMAT)
            except:
                date_str = "Fecha inválida"

            return ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Text(category_icon, size=24),
                            width=50,
                            height=50,
                            border_radius=25,
                            bgcolor=f"{category_color}30",
                            alignment=ft.alignment.center,
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    description,
                                    weight=ft.FontWeight.BOLD,
                                    size=14,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Text(
                                    f"{category_name} • {date_str}",
                                    size=12,
                                    color=ft.Colors.GREY_700,
                                ),
                            ],
                            expand=True,
                            spacing=2,
                        ),
                        ft.Text(
                            f"{'+ ' if is_income else '- '}{Config.CURRENCY_SYMBOL} {amount:.2f}",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color="#22c55e" if is_income else "#ef4444",
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=10,
                border_radius=10,
                bgcolor=ft.Colors.WHITE,
                margin=ft.margin.only(bottom=5),
            )
        except Exception as e:
            print(f"  ❌ Error creando tile: {e}")
            import traceback

            traceback.print_exc()
            return ft.Container()

    def previous_month(self, e):
        """Navega al mes anterior"""
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.refresh_current_view()

    def next_month(self, e):
        """Navega al mes siguiente"""
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.refresh_current_view()

    # ========== VISTA: AÑADIR TRANSACCIÓN ==========
    def load_add_transaction_view(self):
        """Vista para añadir transacciones manualmente"""
        self.current_view = "add"
        self.page.floating_action_button = None  # Remover FAB si existe

        # Tipo de transacción
        self.transaction_type_tabs = ft.Tabs(
            selected_index=0,
            on_change=self.on_transaction_type_change,
            tabs=[
                ft.Tab(text="Gasto", icon=ft.Icons.REMOVE_CIRCLE),
                ft.Tab(text="Ingreso", icon=ft.Icons.ADD_CIRCLE),
            ],
        )

        # Campos del formulario
        self.amount_field = ft.TextField(
            label="Monto",
            prefix_text=f"{Config.CURRENCY_SYMBOL} ",
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text="0.00",
            bgcolor=ft.Colors.WHITE,
        )

        self.description_field = ft.TextField(
            label="Descripción",
            hint_text="¿En qué gastaste/ganaste?",
            max_length=Config.MAX_DESCRIPTION_LENGTH,
            bgcolor=ft.Colors.WHITE,
        )

        self.date_field = ft.TextField(
            label="Fecha",
            value=datetime.now().strftime("%Y-%m-%d"),
            read_only=True,
            on_click=self.pick_date,
            bgcolor=ft.Colors.WHITE,
        )

        # Categorías
        self.category_dropdown = ft.Dropdown(
            label="Categoría",
            options=[],
            bgcolor=ft.Colors.WHITE,
        )
        self.update_category_dropdown("expense")

        self.notes_field = ft.TextField(
            label="Notas (opcional)",
            multiline=True,
            min_lines=2,
            max_lines=4,
            hint_text="Información adicional...",
            max_length=Config.MAX_NOTES_LENGTH,
            bgcolor=ft.Colors.WHITE,
        )

        # Botones de acción
        save_button = ft.ElevatedButton(
            "Guardar Transacción",
            icon=ft.Icons.SAVE,
            on_click=self.save_transaction,
            style=ft.ButtonStyle(
                bgcolor=Config.PRIMARY_COLOR,
                color=ft.Colors.WHITE,
            ),
            expand=True,
        )

        import_button = ft.OutlinedButton(
            "Importar desde archivo",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=self.show_import_dialog,
            expand=True,
        )

        # Layout
        self.main_container.content = ft.Column(
            [
                ft.Text("Nueva Transacción", size=24, weight=ft.FontWeight.BOLD),
                self.transaction_type_tabs,
                ft.Divider(height=20),
                self.amount_field,
                self.description_field,
                self.category_dropdown,
                self.date_field,
                self.notes_field,
                ft.Row([save_button, import_button], spacing=10),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=15,
        )

        self.page.update()

    def on_transaction_type_change(self, e):
        """Cambia las categorías según el tipo de transacción"""
        transaction_type = "expense" if e.control.selected_index == 0 else "income"
        self.update_category_dropdown(transaction_type)
        self.page.update()

    def update_category_dropdown(self, transaction_type: str):
        """Actualiza el dropdown de categorías"""
        categories = self.db.get_all_categories(transaction_type)
        self.category_dropdown.options = [
            ft.dropdown.Option(key=str(cat.id), text=f"{cat.icon} {cat.name}")
            for cat in categories
        ]
        if categories:
            self.category_dropdown.value = str(categories[0].id)

    def pick_date(self, e):
        """Abre selector de fecha"""

        def on_date_change(e):
            if e.control.value:
                self.date_field.value = e.control.value.strftime("%Y-%m-%d")
            date_picker.open = False
            self.page.update()

        date_picker = ft.DatePicker(
            on_change=on_date_change,
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31),
        )
        self.page.overlay.append(date_picker)
        date_picker.open = True
        self.page.update()

    def save_transaction(self, e):
        """Guarda la transacción en la base de datos"""
        if not self.amount_field.value or float(self.amount_field.value or 0) <= 0:
            self.show_snackbar("El monto debe ser mayor a 0", error=True)
            return

        if not self.description_field.value:
            self.show_snackbar("La descripción es obligatoria", error=True)
            return

        try:
            transaction_type = (
                "expense"
                if self.transaction_type_tabs.selected_index == 0
                else "income"
            )

            if not self.category_dropdown.value:
                self.show_snackbar("Debes seleccionar una categoría", error=True)
                return
            date_str = self.date_field.value or ""

            self.db.add_transaction(
                date=datetime.strptime(date_str, "%Y-%m-%d"),
                description=self.description_field.value.strip(),
                amount=float(self.amount_field.value),
                category_id=int(self.category_dropdown.value),
                transaction_type=transaction_type,
                notes=self.notes_field.value.strip() if self.notes_field.value else "",
                source="manual",
            )

            self.show_snackbar("✅ Transacción guardada exitosamente")

            # Limpiar formulario
            self.amount_field.value = ""
            self.description_field.value = ""
            self.notes_field.value = ""
            self.date_field.value = datetime.now().strftime("%Y-%m-%d")
            self.page.update()

        except Exception as ex:
            self.show_snackbar(f"Error al guardar: {str(ex)}", error=True)

    def show_import_dialog(self, e):
        """Muestra diálogo para importar archivo"""

        def pick_file(e):
            file_picker.pick_files(
                allow_multiple=False, allowed_extensions=["csv", "xlsx", "xls"]
            )

        def on_file_result(e: ft.FilePickerResultEvent):
            if e.files:
                self.process_import_file(e.files[0].path)

        file_picker = ft.FilePicker(on_result=on_file_result)
        self.page.overlay.append(file_picker)

        dialog = ft.AlertDialog(
            title=ft.Text("Importar Transacciones"),
            content=ft.Column(
                [
                    ft.Text("Selecciona un archivo CSV o Excel con tus transacciones."),
                    ft.Text(
                        "Formato esperado: fecha, descripcion, monto",
                        size=12,
                        italic=True,
                    ),
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.ElevatedButton("Seleccionar Archivo", on_click=pick_file),
            ],
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def process_import_file(self, file_path: str):
        """Procesa el archivo importado"""
        self.close_dialog()
        self.show_snackbar("Procesando archivo...")

        try:
            success, message = self.processor.load_file(file_path)
            if not success:
                self.show_snackbar(message, error=True)
                return

            success, message = self.processor.validate_columns()
            if not success:
                self.show_snackbar(message, error=True)
                return

            success, message = self.processor.clean_data()
            if not success:
                self.show_snackbar(message, error=True)
                return

            categories = self.db.get_all_categories("expense")
            categories_map = {}
            for cat in categories:
                try:
                    safe_id = int(cat.id) if cat.id is not None else 0
                    safe_name = (
                        str(cat.name) if cat.name is not None else "Sin categoría"
                    )
                    categories_map[safe_id] = safe_name
                except Exception as e:
                    print(f"⚠️ Error al procesar categoría: {e}")
                    continue

            self.processor.categorize_transactions(categories_map)
            processed_data = self.processor.get_processed_data()
            count = self.db.add_transactions_bulk(processed_data)

            self.show_snackbar(f"✅ {count} transacciones importadas exitosamente")

        except Exception as ex:
            self.show_snackbar(f"Error al importar: {str(ex)}", error=True)

    # ========== VISTA: HISTORIAL ==========
    def load_history_view(self):
        """Vista de historial de transacciones"""
        self.current_view = "history"
        self.page.floating_action_button = None  # Remover FAB si existe

        transactions = self.db.get_transactions_by_month(
            self.current_year, self.current_month
        )

        month_selector = ft.Row(
            [
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=self.previous_month),
                ft.Text(
                    f"{datetime(self.current_year, self.current_month, 1).strftime('%B %Y')}",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    expand=True,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.IconButton(icon=ft.Icons.ARROW_FORWARD, on_click=self.next_month),
            ]
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

        self.main_container.content = ft.Column(
            [month_selector, ft.Divider(height=10), content], expand=True
        )

        self.page.update()

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
                self.load_history_view()

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

    # ========== VISTA: GRÁFICOS ==========
    def load_charts_view(self):
        """Vista de gráficos y análisis"""
        self.current_view = "charts"
        self.page.floating_action_button = None  # Remover FAB si existe

        summary = self.db.get_monthly_summary(self.current_year, self.current_month)
        expenses_by_category = self.db.get_expenses_by_category(
            self.current_year, self.current_month
        )
        monthly_trend = self.db.get_monthly_trend(6)

        # Selector de mes
        month_selector = ft.Row(
            [
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=self.previous_month),
                ft.Text(
                    f"{datetime(self.current_year, self.current_month, 1).strftime('%B %Y')}",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    expand=True,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.IconButton(icon=ft.Icons.ARROW_FORWARD, on_click=self.next_month),
            ]
        )

        # Resumen del mes
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

        # Gráfico de gastos por categoría
        if expenses_by_category:
            category_chart = self._create_category_chart(expenses_by_category)
            charts.append(category_chart)

        # Tendencia mensual
        if monthly_trend:
            trend_chart = self._create_trend_chart(monthly_trend)
            charts.append(trend_chart)

        self.main_container.content = ft.Column(
            [month_selector, ft.Container(height=10), *charts],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=15,
        )

        self.page.update()

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
                        "📈 Tendencia Mensual (6 meses)",
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

    # ========== VISTA: CATEGORÍAS ==========
    def load_categories_view(self):
        """Vista de gestión de categorías"""
        self.current_view = "categories"

        expense_cats = self.db.get_all_categories("expense")
        income_cats = self.db.get_all_categories("income")

        tabs_content = []

        # Tab de gastos
        expense_tiles = [self._create_category_tile(cat) for cat in expense_cats]
        tabs_content.append(
            ft.Tab(
                text="Gastos",
                icon=ft.Icons.TRENDING_DOWN,
                content=ft.Column(expense_tiles, scroll=ft.ScrollMode.AUTO),
            )
        )

        # Tab de ingresos
        income_tiles = [self._create_category_tile(cat) for cat in income_cats]
        tabs_content.append(
            ft.Tab(
                text="Ingresos",
                icon=ft.Icons.TRENDING_UP,
                content=ft.Column(income_tiles, scroll=ft.ScrollMode.AUTO),
            )
        )

        category_tabs = ft.Tabs(tabs=tabs_content, expand=True)

        add_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            on_click=self.show_add_category_dialog,
            tooltip="Añadir categoría",
            bgcolor=Config.PRIMARY_COLOR,
        )

        self.main_container.content = ft.Column(
            [
                ft.Text("🏷️ Categorías", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                category_tabs,
            ],
            expand=True,
            spacing=10,
        )

        self.page.floating_action_button = add_button
        self.page.update()

    def _create_category_tile(self, category):
        """Crea un tile para una categoría"""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text(category.icon, size=32),
                        width=60,
                        height=60,
                        border_radius=30,
                        bgcolor=f"{category.color}30",
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                category.name if category.name else "Sin categoría",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                (
                                    category.description
                                    if category.description
                                    else "Sin descripción"
                                ),
                                size=12,
                                color=ft.Colors.GREY_600,
                            ),
                        ],
                        expand=True,
                        spacing=2,
                    ),
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_size=20,
                                tooltip="Editar",
                                on_click=lambda e, cat=category: self.show_edit_category_dialog(
                                    cat
                                ),
                                disabled=category.is_default,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_size=20,
                                tooltip="Eliminar",
                                on_click=lambda e, cat=category: self.delete_category(
                                    cat
                                ),
                                disabled=category.is_default,
                            ),
                        ]
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            margin=ft.margin.only(bottom=10),
        )

    def show_add_category_dialog(self, e):
        """Muestra diálogo para añadir categoría"""
        name_field = ft.TextField(
            label="Nombre", autofocus=True, bgcolor=ft.Colors.WHITE
        )
        desc_field = ft.TextField(
            label="Descripción", multiline=True, bgcolor=ft.Colors.WHITE
        )
        icon_field = ft.TextField(
            label="Icono (emoji)", value="💰", bgcolor=ft.Colors.WHITE
        )
        color_field = ft.TextField(
            label="Color (hex)", value="#3b82f6", bgcolor=ft.Colors.WHITE
        )
        type_dropdown = ft.Dropdown(
            label="Tipo",
            options=[
                ft.dropdown.Option(key="expense", text="Gasto"),
                ft.dropdown.Option(key="income", text="Ingreso"),
            ],
            value="expense",
            bgcolor=ft.Colors.WHITE,
        )

        def save_category(e):
            if not name_field.value:
                self.show_snackbar("El nombre es obligatorio", error=True)
                return

            try:
                self.db.add_category(
                    name=name_field.value.strip(),
                    icon=icon_field.value or "💰",
                    color=color_field.value or "#3b82f6",
                    category_type=type_dropdown.value or "expense",
                    description=desc_field.value.strip() if desc_field.value else "",
                )
                self.close_dialog()
                self.show_snackbar("✅ Categoría creada exitosamente")
                self.load_categories_view()
            except Exception as ex:
                self.show_snackbar(f"Error: {str(ex)}", error=True)

        dialog = ft.AlertDialog(
            title=ft.Text("Nueva Categoría"),
            content=ft.Column(
                [name_field, desc_field, icon_field, color_field, type_dropdown],
                tight=True,
                scroll=ft.ScrollMode.AUTO,
                height=400,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.ElevatedButton("Guardar", on_click=save_category),
            ],
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def show_edit_category_dialog(self, category):
        """Muestra diálogo para editar categoría"""
        name_field = ft.TextField(
            label="Nombre", value=category.name, bgcolor=ft.Colors.WHITE
        )
        desc_field = ft.TextField(
            label="Descripción",
            value=category.description or "",
            multiline=True,
            bgcolor=ft.Colors.WHITE,
        )
        icon_field = ft.TextField(
            label="Icono (emoji)", value=category.icon, bgcolor=ft.Colors.WHITE
        )
        color_field = ft.TextField(
            label="Color (hex)", value=category.color, bgcolor=ft.Colors.WHITE
        )

        def update_category(e):
            if not name_field.value:
                self.show_snackbar("El nombre es obligatorio", error=True)
                return

            try:
                self.db.update_category(
                    category.id,
                    name=name_field.value.strip(),
                    icon=icon_field.value,
                    color=color_field.value,
                    description=desc_field.value.strip() if desc_field.value else None,
                )
                self.close_dialog()
                self.show_snackbar("✅ Categoría actualizada")
                self.load_categories_view()
            except Exception as ex:
                self.show_snackbar(f"Error: {str(ex)}", error=True)

        dialog = ft.AlertDialog(
            title=ft.Text("Editar Categoría"),
            content=ft.Column(
                [name_field, desc_field, icon_field, color_field],
                tight=True,
                scroll=ft.ScrollMode.AUTO,
                height=350,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.ElevatedButton("Guardar", on_click=update_category),
            ],
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def delete_category(self, category):
        """Elimina una categoría"""

        def confirm_delete(e):
            if self.db.delete_category(category.id):
                self.close_dialog()
                self.show_snackbar("Categoría eliminada")
                self.load_categories_view()
            else:
                self.show_snackbar("No se puede eliminar esta categoría", error=True)

        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Estás seguro de eliminar '{category.name}'?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.TextButton("Eliminar", on_click=confirm_delete),
            ],
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    # ========== VISTA: CONFIGURACIÓN ==========
    def load_settings_view(self):
        """Vista de configuración y gestión de datos"""
        self.current_view = "settings"
        self.page.floating_action_button = None  # Remover FAB si existe

        # Obtener estadísticas actuales
        stats = self.db.get_database_stats()

        # Tarjeta de estadísticas
        stats_card = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "📊 Estadísticas de la Base de Datos",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Divider(),
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(
                                        "Transacciones",
                                        size=12,
                                        color=ft.Colors.GREY_600,
                                    ),
                                    ft.Text(
                                        str(stats.get("total_transactions", 0)),
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.VerticalDivider(),
                            ft.Column(
                                [
                                    ft.Text(
                                        "Categorías", size=12, color=ft.Colors.GREY_600
                                    ),
                                    ft.Text(
                                        str(stats.get("total_categories", 0)),
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        expand=True,
                    ),
                    ft.Divider(),
                    ft.Text(
                        f"💰 Ingresos totales: {Config.CURRENCY_SYMBOL} {stats.get('total_income', 0):.2f}",
                        size=14,
                    ),
                    ft.Text(
                        f"💸 Gastos totales: {Config.CURRENCY_SYMBOL} {stats.get('total_expenses', 0):.2f}",
                        size=14,
                    ),
                    ft.Text(
                        f"🏷️ Categorías personalizadas: {stats.get('custom_categories', 0)}",
                        size=14,
                    ),
                ],
                spacing=10,
            ),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
        )

        # Opciones de limpieza
        clean_transactions_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.DELETE_SWEEP, size=40, color="#f97316"
                        ),
                        width=60,
                        height=60,
                        border_radius=30,
                        bgcolor="#f9731620",
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                "Limpiar Transacciones",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "Elimina todas las transacciones",
                                size=12,
                                color=ft.Colors.GREY_600,
                            ),
                        ],
                        expand=True,
                        spacing=2,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ARROW_FORWARD_IOS,
                        icon_size=20,
                        on_click=self.confirm_clear_transactions,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            ink=True,
            on_click=self.confirm_clear_transactions,
        )

        clean_categories_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.LABEL_OFF, size=40, color="#eab308"),
                        width=60,
                        height=60,
                        border_radius=30,
                        bgcolor="#eab30820",
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                "Limpiar Categorías Personalizadas",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "Elimina solo categorías creadas por ti",
                                size=12,
                                color=ft.Colors.GREY_600,
                            ),
                        ],
                        expand=True,
                        spacing=2,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ARROW_FORWARD_IOS,
                        icon_size=20,
                        on_click=self.confirm_clear_custom_categories,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            ink=True,
            on_click=self.confirm_clear_custom_categories,
        )

        reset_database_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.RESTART_ALT, size=40, color="#ef4444"),
                        width=60,
                        height=60,
                        border_radius=30,
                        bgcolor="#ef444420",
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                "Resetear Base de Datos",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "Elimina todo excepto categorías predeterminadas",
                                size=12,
                                color=ft.Colors.GREY_600,
                            ),
                        ],
                        expand=True,
                        spacing=2,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ARROW_FORWARD_IOS,
                        icon_size=20,
                        on_click=self.confirm_reset_database,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            ink=True,
            on_click=self.confirm_reset_database,
        )

        # Advertencia
        warning_card = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.WARNING_AMBER, size=24, color="#f97316"),
                    ft.Text(
                        "⚠️ Estas acciones son irreversibles. Asegúrate de tener respaldos si es necesario.",
                        size=12,
                        color=ft.Colors.GREY_700,
                        expand=True,
                    ),
                ],
                spacing=10,
            ),
            padding=15,
            bgcolor="#fef3c7",
            border_radius=10,
            border=ft.border.all(1, "#f59e0b"),
        )

        # Layout
        self.main_container.content = ft.Column(
            [
                ft.Text("⚙️ Configuración", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                stats_card,
                ft.Container(height=10),
                ft.Text("🗑️ Gestión de Datos", size=18, weight=ft.FontWeight.BOLD),
                warning_card,
                ft.Container(height=10),
                clean_transactions_btn,
                ft.Container(height=5),
                clean_categories_btn,
                ft.Container(height=5),
                reset_database_btn,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=10,
        )

        self.page.update()

    def confirm_clear_transactions(self, e):
        """Confirma la limpieza de transacciones"""
        stats = self.db.get_database_stats()
        total_trans = stats.get("total_transactions", 0)

        dialog = ft.AlertDialog(
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.WARNING_AMBER, color="#f97316", size=28),
                    ft.Text("Confirmar Limpieza", weight=ft.FontWeight.BOLD),
                ],
                spacing=10,
            ),
            content=ft.Column(
                [
                    ft.Text(
                        f"Estás a punto de eliminar {total_trans} transacciones.",
                        size=16,
                    ),
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Text(
                            "⚠️ Esta acción NO se puede deshacer",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color="#ef4444",
                        ),
                        padding=10,
                        bgcolor="#fee2e2",
                        border_radius=8,
                    ),
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.ElevatedButton(
                    "Eliminar Todo",
                    on_click=self.clear_transactions,
                    style=ft.ButtonStyle(bgcolor="#ef4444", color=ft.Colors.WHITE),
                ),
            ],
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def clear_transactions(self, e):
        """Ejecuta la limpieza de transacciones"""
        if self.db.clear_all_transactions():
            self.close_dialog()
            self.show_snackbar("✅ Todas las transacciones han sido eliminadas")
            self.load_settings_view()  # Recargar vista para actualizar stats
        else:
            self.show_snackbar("❌ Error al limpiar transacciones", error=True)

    def confirm_clear_custom_categories(self, e):
        """Confirma la limpieza de categorías personalizadas"""
        stats = self.db.get_database_stats()
        custom_cats = stats.get("custom_categories", 0)

        if custom_cats == 0:
            self.show_snackbar("No hay categorías personalizadas para eliminar")
            return

        dialog = ft.AlertDialog(
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.WARNING_AMBER, color="#f97316", size=28),
                    ft.Text("Confirmar Limpieza", weight=ft.FontWeight.BOLD),
                ],
                spacing=10,
            ),
            content=ft.Column(
                [
                    ft.Text(
                        f"Estás a punto de eliminar {custom_cats} categorías personalizadas.",
                        size=16,
                    ),
                    ft.Container(height=10),
                    ft.Text(
                        "Las categorías predeterminadas se mantendrán intactas.",
                        size=14,
                        color=ft.Colors.GREY_600,
                    ),
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.ElevatedButton(
                    "Eliminar Categorías",
                    on_click=self.clear_custom_categories,
                    style=ft.ButtonStyle(bgcolor="#eab308", color=ft.Colors.WHITE),
                ),
            ],
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def clear_custom_categories(self, e):
        """Ejecuta la limpieza de categorías personalizadas"""
        if self.db.clear_custom_categories():
            self.close_dialog()
            self.show_snackbar("✅ Categorías personalizadas eliminadas")
            self.load_settings_view()
        else:
            self.show_snackbar("❌ Error al limpiar categorías", error=True)

    def confirm_reset_database(self, e):
        """Confirma el reseteo completo de la base de datos"""
        stats = self.db.get_database_stats()

        dialog = ft.AlertDialog(
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.DANGEROUS, color="#ef4444", size=32),
                    ft.Text("⚠️ ADVERTENCIA CRÍTICA", weight=ft.FontWeight.BOLD),
                ],
                spacing=10,
            ),
            content=ft.Column(
                [
                    ft.Text(
                        "Esta acción eliminará:",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(height=5),
                    ft.Text(
                        f"• {stats.get('total_transactions', 0)} transacciones", size=14
                    ),
                    ft.Text(
                        f"• {stats.get('custom_categories', 0)} categorías personalizadas",
                        size=14,
                    ),
                    ft.Text("• Todos los presupuestos configurados", size=14),
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "⚠️ ESTA ACCIÓN ES IRREVERSIBLE",
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color="#ef4444",
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Text(
                                    "Solo se mantendrán las categorías predeterminadas",
                                    size=12,
                                    color=ft.Colors.GREY_700,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=15,
                        bgcolor="#fee2e2",
                        border_radius=8,
                        border=ft.border.all(2, "#ef4444"),
                    ),
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.ElevatedButton(
                    "RESETEAR TODO",
                    on_click=self.reset_database,
                    style=ft.ButtonStyle(
                        bgcolor="#ef4444",
                        color=ft.Colors.WHITE,
                    ),
                ),
            ],
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def reset_database(self, e):
        """Ejecuta el reseteo completo de la base de datos"""
        if self.db.reset_database():
            self.close_dialog()
            self.show_snackbar("✅ Base de datos reseteada exitosamente")
            # Volver al mes actual
            self.current_month = datetime.now().month
            self.current_year = datetime.now().year
            self.load_settings_view()
        else:
            self.show_snackbar("❌ Error al resetear la base de datos", error=True)

    # ========== UTILIDADES ==========
    def refresh_current_view(self):
        """Refresca la vista actual"""
        print(f"🔄 Refrescando vista: {self.current_view}")
        if self.current_view == "home":
            self.load_home_view()
        elif self.current_view == "add":
            self.load_add_transaction_view()
        elif self.current_view == "history":
            self.load_history_view()
        elif self.current_view == "charts":
            self.load_charts_view()
        elif self.current_view == "categories":
            self.load_categories_view()
        elif self.current_view == "settings":
            self.load_settings_view()

    def show_snackbar(self, message: str, error: bool = False):
        """Muestra un mensaje temporal"""
        snackbar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor="#ef4444" if error else "#22c55e",
        )
        self.page.open(snackbar)

    def close_dialog(self):
        """Cierra el diálogo actual"""
        if self.page.overlay and len(self.page.overlay) > 0:
            dialog = next(
                (c for c in self.page.overlay if isinstance(c, ft.AlertDialog)),
                None,
            )
            if dialog:
                dialog.open = False
                self.page.overlay.remove(dialog)
                self.page.update()


def main(page: ft.Page):
    """Función principal"""
    print("\n" + "=" * 60)
    print("💰 TERMOWALLET - Iniciando aplicación")
    print("=" * 60 + "\n")
    # Configuración inicial
    page.window.width = 600
    page.window.height = 900
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#f5f5f5"

    # Inicializar app
    try:
        app = ExpenseTrackerApp(page)
        print("\n✅ Aplicación inicializada correctamente\n")
    except Exception as e:
        print(f"\n❌ ERROR FATAL al inicializar:")
        print(f"   {str(e)}\n")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    ft.app(target=main)
