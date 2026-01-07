"""
Vista para añadir transacciones - CON SOPORTE PARA COLUMNA TIPO
Archivo: src/ui/add_transaction_view.py
"""

import flet as ft
from datetime import datetime
from .base_view import BaseView
from src.utils.config import Config
from src.business.processor import TransactionProcessor


class AddTransactionView(BaseView):
    """Vista para añadir transacciones manualmente"""

    def __init__(self, page: ft.Page, db_manager, show_snackbar_callback):
        super().__init__(page, db_manager, show_snackbar_callback)
        self.processor = TransactionProcessor()
        self._init_fields()

    def _init_fields(self):
        """Inicializa los campos del formulario"""
        self.transaction_type_tabs = ft.Tabs(
            selected_index=0,
            on_change=self.on_transaction_type_change,
            tabs=[
                ft.Tab(text="Gasto", icon=ft.Icons.REMOVE_CIRCLE),
                ft.Tab(text="Ingreso", icon=ft.Icons.ADD_CIRCLE),
            ],
        )

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
        """✅ ACTUALIZADO: Guarda la transacción y muestra alertas de presupuesto"""
        if self.is_saving:
            return

        # Validaciones
        if not self.amount_field.value or self.amount_field.value.strip() == "":
            self.show_snackbar("El monto es obligatorio", error=True)
            return

        if not self.description_field.value or self.description_field.value.strip() == "":
            self.show_snackbar("La descripción es obligatoria", error=True)
            return

        try:
            amount = float(self.amount_field.value)
            if amount <= 0:
                self.show_snackbar("El monto debe ser mayor a 0", error=True)
                return
        except ValueError:
            self.show_snackbar("Monto inválido", error=True)
            return

        self.is_saving = True

        try:
            # Obtener valores
            description = self.description_field.value.strip()
            category_id = int(self.category_dropdown.value)
            transaction_type = self.type_dropdown.value
            notes = self.notes_field.value.strip() if self.notes_field.value else None
            date = self.date_picker.value

            # Guardar transacción
            self.db.add_transaction(
                date=date,
                description=description,
                amount=amount,
                category_id=category_id,
                transaction_type=transaction_type,
                notes=notes,
                source="manual",
            )

            # ✅ NUEVO: Verificar alertas de presupuesto SOLO para gastos
            if transaction_type == "expense":
                alert = self.db.check_category_budget_alert(
                    category_id, 
                    date.year, 
                    date.month
                )
                
                if alert["has_alert"]:
                    # Mostrar diálogo de alerta
                    self.show_budget_alert_dialog(alert)
                else:
                    # Si no hay alerta, mostrar mensaje normal
                    self.show_snackbar("✅ Transacción guardada exitosamente")
            else:
                # Para ingresos, mostrar mensaje normal
                self.show_snackbar("✅ Ingreso registrado exitosamente")

            # Limpiar campos
            self.amount_field.value = ""
            self.description_field.value = ""
            self.notes_field.value = ""
            self.amount_field.focus()
            
            self.page.update()

        except Exception as ex:
            self.show_snackbar(f"Error: {str(ex)}", error=True)
        finally:
            self.is_saving = False


    def show_budget_alert_dialog(self, alert: dict):
        """
        ✅ NUEVO: Muestra un diálogo con la alerta de presupuesto
        
        Args:
            alert: Diccionario con información de la alerta
        """
        # Colores según el tipo de alerta
        colors = {
            "warning": {
                "bg": "#fef3c7",
                "border": "#f59e0b",
                "text": "#92400e",
                "button": "#f59e0b"
            },
            "danger": {
                "bg": "#fee2e2",
                "border": "#ef4444",
                "text": "#991b1b",
                "button": "#ef4444"
            },
            "over_budget": {
                "bg": "#fee2e2",
                "border": "#dc2626",
                "text": "#7f1d1d",
                "button": "#dc2626"
            }
        }
        
        theme = colors.get(alert["alert_type"], colors["warning"])
        
        # Crear contenido del diálogo
        content = ft.Column(
            [
                # Icono grande
                ft.Container(
                    content=ft.Text(
                        alert["icon"],
                        size=64,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.alignment.center,
                ),
                
                # Título según severidad
                ft.Text(
                    "¡LÍMITE EXCEDIDO!" if alert["alert_type"] == "over_budget"
                    else "¡CASI AL LÍMITE!" if alert["alert_type"] == "danger"
                    else "ALERTA DE PRESUPUESTO",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=theme["text"],
                    text_align=ft.TextAlign.CENTER,
                ),
                
                ft.Divider(height=20),
                
                # Información de la categoría
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Text(
                                            alert["category_icon"],
                                            size=28
                                        ),
                                        width=50,
                                        height=50,
                                        bgcolor=f"{alert['category_color']}30",
                                        border_radius=25,
                                        alignment=ft.alignment.center,
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text(
                                                alert["category_name"],
                                                size=18,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                            ft.Text(
                                                f"{alert['percentage_used']:.1f}% usado",
                                                size=14,
                                                color=theme["text"],
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                        ],
                                        spacing=2,
                                        expand=True,
                                    ),
                                ],
                                spacing=15,
                            ),
                            
                            ft.Container(height=15),
                            
                            # Barra de progreso
                            ft.Column(
                                [
                                    ft.ProgressBar(
                                        value=min(alert["percentage_used"] / 100, 1.0),
                                        color=theme["button"],
                                        bgcolor=ft.Colors.GREY_200,
                                        height=8,
                                    ),
                                ],
                            ),
                            
                            ft.Container(height=15),
                            
                            # Detalles
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Row(
                                            [
                                                ft.Text("Presupuesto:", size=13, weight=ft.FontWeight.BOLD),
                                                ft.Text(
                                                    f"{Config.CURRENCY_SYMBOL} {alert['assigned_amount']:.2f}",
                                                    size=13
                                                ),
                                            ],
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        ),
                                        ft.Row(
                                            [
                                                ft.Text("Gastado:", size=13, weight=ft.FontWeight.BOLD),
                                                ft.Text(
                                                    f"{Config.CURRENCY_SYMBOL} {alert['spent_amount']:.2f}",
                                                    size=13,
                                                    color=theme["text"],
                                                ),
                                            ],
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        ),
                                        ft.Divider(height=5),
                                        ft.Row(
                                            [
                                                ft.Text(
                                                    "Disponible:" if alert['remaining'] >= 0 else "Excedido:",
                                                    size=14,
                                                    weight=ft.FontWeight.BOLD,
                                                ),
                                                ft.Text(
                                                    f"{Config.CURRENCY_SYMBOL} {abs(alert['remaining']):.2f}",
                                                    size=14,
                                                    weight=ft.FontWeight.BOLD,
                                                    color="#22c55e" if alert['remaining'] >= 0 else "#ef4444",
                                                ),
                                            ],
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        ),
                                    ],
                                    spacing=8,
                                ),
                                padding=15,
                                bgcolor=ft.Colors.GREY_50,
                                border_radius=8,
                            ),
                        ],
                        spacing=5,
                    ),
                    padding=15,
                    bgcolor=theme["bg"],
                    border_radius=10,
                    border=ft.border.all(2, theme["border"]),
                ),
                
                # Mensaje motivacional
                ft.Container(
                    content=ft.Text(
                        "💡 Considera ajustar tus gastos en esta categoría para cumplir tu presupuesto."
                        if alert["alert_type"] != "over_budget"
                        else "💡 Has excedido el límite. Revisa tus gastos o ajusta tu presupuesto.",
                        size=12,
                        color=ft.Colors.GREY_700,
                        text_align=ft.TextAlign.CENTER,
                        italic=True,
                    ),
                    padding=10,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        
        dialog = ft.AlertDialog(
            content=ft.Container(
                content=content,
                width=400,
            ),
            actions=[
                ft.TextButton(
                    "Entendido",
                    on_click=lambda _: self.close_dialog(),
                    style=ft.ButtonStyle(
                        bgcolor=theme["button"],
                        color=ft.Colors.WHITE,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        
        self.show_dialog(dialog)


    # ✅ AGREGAR TAMBIÉN: Método para mostrar resumen de alertas en la vista principal

    def show_all_alerts_summary(self, e):
        """
        ✅ OPCIONAL: Muestra un resumen de todas las alertas del mes
        Útil para agregar un botón en la vista de añadir transacción
        """
        from datetime import datetime
        
        now = datetime.now()
        alerts = self.db.get_all_category_budget_alerts(now.year, now.month)
        
        if not alerts:
            self.show_snackbar("✅ No hay alertas de presupuesto")
            return
        
        # Crear lista de alertas
        alert_tiles = []
        for alert in alerts:
            alert_tiles.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(alert["icon"], size=24),
                            ft.Column(
                                [
                                    ft.Text(
                                        alert["category_name"],
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        f"{alert['percentage_used']:.1f}% usado - "
                                        f"{Config.CURRENCY_SYMBOL} {abs(alert['remaining']):.2f} "
                                        f"{'disponible' if alert['remaining'] >= 0 else 'excedido'}",
                                        size=11,
                                        color=ft.Colors.GREY_600,
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                        ],
                        spacing=10,
                    ),
                    padding=10,
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=8,
                    margin=ft.margin.only(bottom=5),
                )
            )
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"⚡ Alertas de Presupuesto ({len(alerts)})"),
            content=ft.Container(
                content=ft.Column(
                    alert_tiles,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=400,
                height=300,
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda _: self.close_dialog()),
            ],
        )
        
        self.show_dialog(dialog)

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
                        "Formato esperado: fecha, descripcion, monto, tipo (opcional)",
                        size=12,
                        italic=True,
                    ),
                    ft.Container(height=5),
                    ft.Text(
                        "La columna 'tipo' puede contener: gasto, ingreso, expense, income",
                        size=11,
                        italic=True,
                        color=ft.Colors.GREY_600,
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

    """
    Actualización del método process_import_file en add_transaction_view.py
    Para usar las palabras clave almacenadas en la base de datos
    """

    def process_import_file(self, file_path: str):
        """✅ ACTUALIZADO: Usa palabras clave de la BD para categorizar"""
        self.close_dialog()
        self.show_snackbar("Procesando archivo...")

        try:
            # 1. Cargar archivo
            success, message = self.processor.load_file(file_path)
            if not success:
                self.show_snackbar(message, error=True)
                return

            # 2. Validar columnas
            success, message = self.processor.validate_columns()
            if not success:
                self.show_snackbar(message, error=True)
                return

            # 3. Limpiar datos
            success, message = self.processor.clean_data()
            if not success:
                self.show_snackbar(message, error=True)
                return

            # 4. Obtener categorías con sus palabras clave de la BD
            categories_expense = self.db.get_all_categories("expense")
            categories_income = self.db.get_all_categories("income")

            # ✅ NUEVO: Actualizar el categorizador con las palabras clave de la BD
            from src.business.categorizer import TransactionCategorizer
            categorizer = TransactionCategorizer()
            
            # Cargar palabras clave personalizadas de gastos
            for cat in categories_expense:
                keywords_from_db = cat.get_keywords_list()
                if keywords_from_db:
                    # Reemplazar las palabras clave predeterminadas con las de la BD
                    categorizer.set_keywords(cat.name, keywords_from_db, "expense")
            
            # Cargar palabras clave personalizadas de ingresos
            for cat in categories_income:
                keywords_from_db = cat.get_keywords_list()
                if keywords_from_db:
                    categorizer.set_keywords(cat.name, keywords_from_db, "income")
            
            # Actualizar el categorizador del processor
            self.processor.categorizer = categorizer

            # Crear mapas de categorías
            categories_map_expense = {}
            for cat in categories_expense:
                try:
                    safe_id = int(cat.id) if cat.id is not None else 0
                    safe_name = str(cat.name) if cat.name is not None else "Sin categoría"
                    categories_map_expense[safe_id] = safe_name
                except Exception as e:
                    print(f"⚠️ Error al procesar categoría de gasto: {e}")
                    continue

            categories_map_income = {}
            for cat in categories_income:
                try:
                    safe_id = int(cat.id) if cat.id is not None else 0
                    safe_name = str(cat.name) if cat.name is not None else "Sin categoría"
                    categories_map_income[safe_id] = safe_name
                except Exception as e:
                    print(f"⚠️ Error al procesar categoría de ingreso: {e}")
                    continue

            # 5. Categorizar transacciones
            self.processor.categorize_transactions(
                categories_map_expense, 
                categories_map_income
            )

            # 6. Obtener datos procesados
            processed_data = self.processor.get_processed_data()

            # 7. Insertar en base de datos
            count = self.db.add_transactions_bulk(processed_data)

            # 8. Mostrar resumen
            summary = self.processor.get_summary()
            
            message = f"✅ {count} transacciones importadas exitosamente\n"
            message += f"📊 Gastos: {summary.get('count_expenses', 0)} | "
            message += f"Ingresos: {summary.get('count_income', 0)}"

            self.show_snackbar(message)

        except Exception as ex:
            import traceback
            traceback.print_exc()
            self.show_snackbar(f"Error al importar: {str(ex)}", error=True)






    def build(self) -> ft.Control:
        """Construye la vista"""
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

        return ft.Column(
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