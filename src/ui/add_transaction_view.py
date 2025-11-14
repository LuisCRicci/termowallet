"""
Vista para añadir transacciones
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