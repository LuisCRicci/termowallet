"""
Vista de Importación de Archivos
Archivo: src/ui/upload_view.py
"""

import flet as ft
from src.utils.config import Config
from src.business.processor import TransactionProcessor


class UploadView:
    """Vista para importar transacciones desde archivos"""

    def __init__(self, db_manager, page: ft.Page, on_success_callback=None):
        self.db = db_manager
        self.page = page
        self.processor = TransactionProcessor()
        self.on_success = on_success_callback

        # Estado
        self.file_path = None
        self.preview_data = None

    def build(self) -> ft.Container:
        """Construye la vista"""

        # Título
        title = ft.Text("Importar Transacciones", size=24, weight=ft.FontWeight.BOLD)

        # Instrucciones
        instructions = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "📄 Formato de archivo soportado:", weight=ft.FontWeight.BOLD
                    ),
                    ft.Text("• CSV (.csv)"),
                    ft.Text("• Excel (.xlsx, .xls)"),
                    ft.Divider(height=10),
                    ft.Text("📋 Columnas requeridas:", weight=ft.FontWeight.BOLD),
                    ft.Text("• Fecha: fecha, date, día"),
                    ft.Text("• Descripción: descripción, concepto, detalle"),
                    ft.Text("• Monto: monto, amount, importe, valor"),
                    ft.Divider(height=10),
                    ft.Text(
                        "💡 Ejemplo de archivo CSV:", weight=ft.FontWeight.BOLD, size=12
                    ),
                    ft.Container(
                        content=ft.Text(
                            "fecha,descripcion,monto\n"
                            "2024-11-01,Supermercado,150.50\n"
                            "2024-11-02,Taxi,15.00\n"
                            "2024-11-03,Restaurant,45.80",
                            size=11,
                            font_family="Courier",
                        ),
                        bgcolor=ft.Colors.GREY_900,
                        padding=10,
                        border_radius=5,
                    ),
                ],
                spacing=5,
            ),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.SURFACE,
        )

        # Botón de selección de archivo
        def pick_file(e):
            file_picker.pick_files(
                allowed_extensions=["csv", "xlsx", "xls"], allow_multiple=False
            )

        def on_file_selected(e: ft.FilePickerResultEvent):
            if e.files and len(e.files) > 0:
                self.file_path = e.files[0].path
                file_name_text.value = f"📁 {e.files[0].name}"
                process_button.disabled = False
                self.page.update()

        file_picker = ft.FilePicker(on_result=on_file_selected)
        self.page.overlay.append(file_picker)

        file_name_text = ft.Text(
            "Ningún archivo seleccionado",
            size=14,
            color=ft.Colors.GREY_600,
            italic=True,
        )

        select_button = ft.ElevatedButton(
            "Seleccionar Archivo",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=pick_file,
            style=ft.ButtonStyle(bgcolor=Config.PRIMARY_COLOR, color=ft.Colors.WHITE),
        )

        # Botón de procesamiento
        process_button = ft.ElevatedButton(
            "Procesar e Importar",
            icon=ft.Icons.SYNC,
            on_click=self._process_file,
            disabled=True,
            style=ft.ButtonStyle(bgcolor=Config.SUCCESS_COLOR, color=ft.Colors.WHITE),
        )

        # Contenedor de resultados
        self.results_container = ft.Container(visible=False)

        return ft.Container(
            content=ft.Column(
                [
                    title,
                    ft.Divider(height=20),
                    instructions,
                    ft.Divider(height=20),
                    ft.Row(
                        [select_button, file_name_text],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=10,
                    ),
                    process_button,
                    self.results_container,
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=15,
            ),
            expand=True,
            padding=10,
        )

    def _process_file(self, e):
        """Procesa el archivo seleccionado"""
        if not self.file_path:
            self._show_snackbar("No hay archivo seleccionado", error=True)
            return

        # Mostrar loading
        self.results_container.content = ft.Column(
            [ft.ProgressRing(), ft.Text("Procesando archivo...", size=14)],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.results_container.visible = True
        self.page.update()

        try:
            # 1. Cargar archivo
            success, message = self.processor.load_file(self.file_path)
            if not success:
                self._show_error(message)
                return

            # 2. Validar columnas
            success, message = self.processor.validate_columns()
            if not success:
                self._show_error(message)
                return

            # 3. Limpiar datos
            success, message = self.processor.clean_data()
            if not success:
                self._show_error(message)
                return

            # 4. Categorizar
            categories = self.db.get_all_categories("expense")
            categories_map = {cat.id: cat.name for cat in categories}
            if not self.processor.categorize_transactions(categories_map):
                self._show_error("Error al categorizar transacciones")
                return

            # 5. Mostrar resumen y confirmación
            summary = self.processor.get_summary()
            self._show_summary(summary)

        except Exception as ex:
            self._show_error(f"Error inesperado: {str(ex)}")

    def _show_summary(self, summary: dict):
        """Muestra resumen de procesamiento y botón de confirmación"""

        # Contenedor de resumen
        summary_items = [
            ft.Text(
                "✅ Archivo procesado exitosamente",
                size=18,
                weight=ft.FontWeight.BOLD,
                color=Config.SUCCESS_COLOR,
            ),
            ft.Divider(height=10),
        ]

        if summary["status"] == "success":
            summary_items.extend(
                [
                    ft.Row(
                        [
                            ft.Text("Registros originales:", weight=ft.FontWeight.BOLD),
                            ft.Text(str(summary["original_count"])),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(
                        [
                            ft.Text("Registros válidos:", weight=ft.FontWeight.BOLD),
                            ft.Text(str(summary["processed_count"])),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(
                        [
                            ft.Text("Registros eliminados:", weight=ft.FontWeight.BOLD),
                            ft.Text(str(summary["removed_count"])),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(height=10),
                    ft.Row(
                        [
                            ft.Text("Monto total:", weight=ft.FontWeight.BOLD),
                            ft.Text(
                                f"{Config.CURRENCY_SYMBOL} {summary['total_amount']:.2f}"
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(
                        [
                            ft.Text("Rango de fechas:", weight=ft.FontWeight.BOLD),
                            ft.Text(
                                f"{summary['date_range']['start']} → {summary['date_range']['end']}"
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ]
            )

            # Errores/advertencias si existen
            if summary.get("errors"):
                summary_items.append(ft.Divider(height=10))
                summary_items.append(
                    ft.Text("⚠️ Advertencias:", weight=ft.FontWeight.BOLD)
                )
                for error in summary["errors"]:
                    summary_items.append(
                        ft.Text(error, size=12, color=Config.WARNING_COLOR)
                    )

        summary_container = ft.Container(
            content=ft.Column(summary_items, spacing=5),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.SURFACE,
        )

        # Botones de acción
        def confirm_import(e):
            processed_data = self.processor.get_processed_data()
            count = self.db.add_transactions_bulk(processed_data)

            self._show_snackbar(f"✅ {count} transacciones importadas exitosamente")

            # Reset
            self.processor.reset()
            self.file_path = None

            # Callback de éxito
            if self.on_success:
                self.on_success()

            # Actualizar vista
            self.results_container.visible = False
            self.page.update()

        def cancel_import(e):
            self.processor.reset()
            self.file_path = None
            self.results_container.visible = False
            self.page.update()

        buttons_row = ft.Row(
            [
                ft.OutlinedButton(
                    "Cancelar", icon=ft.Icons.CANCEL, on_click=cancel_import
                ),
                ft.ElevatedButton(
                    "Confirmar e Importar",
                    icon=ft.Icons.CHECK_CIRCLE,
                    on_click=confirm_import,
                    style=ft.ButtonStyle(
                        bgcolor=Config.SUCCESS_COLOR, color=ft.Colors.WHITE
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.END,
            spacing=10,
        )

        # Actualizar contenedor de resultados
        self.results_container.content = ft.Column(
            [summary_container, buttons_row], spacing=15
        )
        self.page.update()

    def _show_error(self, message: str):
        """Muestra un mensaje de error"""
        self.results_container.content = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.ERROR, size=48, color=Config.ERROR_COLOR),
                    ft.Text(
                        "Error",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=Config.ERROR_COLOR,
                    ),
                    ft.Text(message, size=14, text_align=ft.TextAlign.CENTER),
                    ft.TextButton(
                        "Intentar de nuevo", on_click=lambda _: self._hide_results()
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=20,
        )
        self.page.update()
        self._show_snackbar(message, error=True)

    def _hide_results(self):
        """Oculta el contenedor de resultados"""
        self.results_container.visible = False
        self.processor.reset()
        self.page.update()

    def _show_snackbar(self, message: str, error: bool = False):
        """Muestra un snackbar usando el método page.open()"""
        # 1. Crea el objeto SnackBar
        snackbar_control = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=Config.ERROR_COLOR if error else Config.SUCCESS_COLOR,
        )
        # 2. Usa el método page.open() para mostrar el control temporal
        #    Esto reemplaza: self.page.snackbar = snackbar_control
        #    y también: self.page.snackbar.open = True, y page.update()
        self.page.open(snackbar_control)
        self.page.update()
