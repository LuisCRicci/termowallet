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
        self.is_saving = False
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
            autofocus=True, # ✅ NUEVO: Focus en monto al abrir
        )

        self.description_field = ft.TextField(
            label="Descripción",
            hint_text="¿En qué gastaste/ganaste?",
            max_length=Config.MAX_DESCRIPTION_LENGTH,
            bgcolor=ft.Colors.WHITE,
        )

        # ✅ CORREGIDO: Usar TextField simple con valor inicial
        self.date_field = ft.TextField(
            label="Fecha",
            value=datetime.now().strftime("%Y-%m-%d"),
            read_only=True,
            on_click=self.pick_date,
            bgcolor=ft.Colors.WHITE,
            suffix_icon=ft.Icons.CALENDAR_TODAY,
        )

         # ✅ NUEVO: Almacenar la fecha real en una variable
        self.selected_date = datetime.now()
        
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
        """✅ COMPLETAMENTE CORREGIDO: Guarda la transacción con campos correctos"""
        
        # ✅ Prevenir doble guardado
        if self.is_saving:
            return
        
        # Validaciones básicas
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
            # ✅ CORREGIDO: Obtener valores de los campos correctos
            description = self.description_field.value.strip()
            category_id = int(self.category_dropdown.value)
            
            # ✅ CORREGIDO: Determinar tipo de transacción desde las tabs
            transaction_type = "expense" if self.transaction_type_tabs.selected_index == 0 else "income"
            
            # ✅ CORREGIDO: Usar la fecha almacenada
            date = self.selected_date
            
            notes = self.notes_field.value.strip() if self.notes_field.value else None

            # ✅ Guardar transacción en BD
            print(f"\n📝 GUARDANDO TRANSACCIÓN:")
            print(f"   Fecha: {date.strftime('%Y-%m-%d')}")
            print(f"   Descripción: {description}")
            print(f"   Monto: {amount}")
            print(f"   Tipo: {transaction_type}")
            print(f"   Categoría ID: {category_id}")
            
            self.db.add_transaction(
                date=date,
                description=description,
                amount=amount,
                category_id=category_id,
                transaction_type=transaction_type,
                notes=notes,
                source="manual",
            )

            # ✅ Verificar alertas de presupuesto SOLO para gastos
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

            # ✅ Limpiar campos después de guardar
            self.amount_field.value = ""
            self.description_field.value = ""
            self.notes_field.value = ""
            self.selected_date = datetime.now()
            self.date_field.value = self.selected_date.strftime("%Y-%m-%d")
            
            # ✅ Volver a poner focus en el campo de monto
            self.amount_field.focus()
            
            self.page.update()
            
            print("✅ Transacción guardada correctamente\n")

        except Exception as ex:
            import traceback
            print(f"\n❌ ERROR AL GUARDAR TRANSACCIÓN:")
            print(traceback.format_exc())
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


    # ✅✅✅✅ SIN USAR AUN: Método para mostrar resumen de alertas en la vista principal 

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
    ✅ REEMPLAZAR COMPLETAMENTE el método process_import_file 
    EN: src/ui/add_transaction_view.py

    Este método ahora:
    1. Procesa en lotes de 100
    2. Hace commit por lote
    3. Refresca la sesión al finalizar
    4. Recarga automáticamente la vista
    """

    def process_import_file(self, file_path: str):
        """✅ MEJORADO: Gestiona correctamente las transacciones masivas con recarga automática"""
        self.close_dialog()
        self.show_snackbar("Procesando archivo...")

        try:
            # ============================================================
            # PASO 1: CARGAR Y VALIDAR ARCHIVO
            # ============================================================
            
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

            # ============================================================
            # PASO 2: CONFIGURAR CATEGORIZADOR
            # ============================================================
            
            categories_expense = self.db.get_all_categories("expense")
            categories_income = self.db.get_all_categories("income")

            from src.business.categorizer import TransactionCategorizer
            categorizer = TransactionCategorizer()
            
            # Cargar palabras clave de gastos
            for cat in categories_expense:
                keywords_from_db = cat.get_keywords_list()
                if keywords_from_db:
                    categorizer.set_keywords(cat.name, keywords_from_db, "expense")
            
            # Cargar palabras clave de ingresos
            for cat in categories_income:
                keywords_from_db = cat.get_keywords_list()
                if keywords_from_db:
                    categorizer.set_keywords(cat.name, keywords_from_db, "income")
            
            self.processor.categorizer = categorizer

            # Crear mapas de categorías
            categories_map_expense = {}
            for cat in categories_expense:
                try:
                    categories_map_expense[int(cat.id)] = str(cat.name)
                except:
                    continue

            categories_map_income = {}
            for cat in categories_income:
                try:
                    categories_map_income[int(cat.id)] = str(cat.name)
                except:
                    continue

            # Categorizar
            self.processor.categorize_transactions(
                categories_map_expense, 
                categories_map_income
            )

            # ============================================================
            # PASO 3: INSERCIÓN MASIVA EN LOTES
            # ============================================================
            
            processed_data = self.processor.get_processed_data()
            
            print(f"\n{'='*60}")
            print(f"📦 IMPORTACIÓN MASIVA")
            print(f"{'='*60}")
            print(f"   Total a insertar: {len(processed_data)}")
            print(f"{'='*60}\n")
            
            BATCH_SIZE = 100
            total_inserted = 0
            total_failed = 0
            
            for i in range(0, len(processed_data), BATCH_SIZE):
                batch = processed_data[i:i + BATCH_SIZE]
                batch_num = (i // BATCH_SIZE) + 1
                
                try:
                    print(f"  📦 Lote {batch_num}: Insertando {len(batch)} transacciones...")
                    
                    # Insertar el lote
                    count = self.db.add_transactions_bulk(batch)
                    
                    # ✅ COMMIT EXPLÍCITO después de cada lote
                    self.db.session.commit()
                    
                    total_inserted += count
                    print(f"  ✅ Lote {batch_num}: {count} transacciones insertadas y confirmadas")
                    
                except Exception as batch_error:
                    print(f"  ❌ Error en lote {batch_num}: {batch_error}")
                    
                    # Rollback del lote fallido
                    try:
                        self.db.session.rollback()
                    except:
                        pass
                    
                    total_failed += len(batch)
                    continue
            
            # ============================================================
            # PASO 4: REFRESCAR SESIÓN DE BD
            # ============================================================
            
            print(f"\n{'='*60}")
            print(f"🔄 REFRESCANDO SESIÓN DE BASE DE DATOS")
            print(f"{'='*60}")
            
            try:
                # Cerrar sesión actual
                self.db.session.close()
                print(f"  ✅ Sesión actual cerrada")
                
                # Crear nueva sesión
                from sqlalchemy.orm import sessionmaker
                Session = sessionmaker(bind=self.db.engine)
                self.db.session = Session()
                
                print(f"  ✅ Nueva sesión creada")
                
            except Exception as refresh_error:
                print(f"  ⚠️ Error al refrescar sesión: {refresh_error}")
                # Continuar de todos modos
            
            # ============================================================
            # PASO 5: MOSTRAR RESUMEN
            # ============================================================
            
            summary = self.processor.get_summary()
            
            print(f"\n{'='*60}")
            print(f"✅ IMPORTACIÓN COMPLETADA")
            print(f"{'='*60}")
            print(f"   Insertadas: {total_inserted}")
            print(f"   Fallidas: {total_failed}")
            print(f"   Gastos: {summary.get('count_expenses', 0)}")
            print(f"   Ingresos: {summary.get('count_income', 0)}")
            print(f"{'='*60}\n")
            
            # Mensaje al usuario
            if total_inserted > 0:
                message = f"✅ {total_inserted} transacciones importadas exitosamente\n"
                message += f"📊 Gastos: {summary.get('count_expenses', 0)} | "
                message += f"Ingresos: {summary.get('count_income', 0)}"
                
                if total_failed > 0:
                    message += f"\n⚠️ {total_failed} transacciones fallaron"
                
                self.show_snackbar(message)
            else:
                self.show_snackbar("❌ No se pudo importar ninguna transacción", error=True)
                return
            
            # ============================================================
            # PASO 6: ✅ RECARGAR VISTA AUTOMÁTICAMENTE
            # ============================================================
            
            print(f"\n{'='*60}")
            print(f"🔄 RECARGANDO INTERFAZ")
            print(f"{'='*60}")
            
            try:
                # Método 1: Usar force_refresh_after_import (más agresivo, recomendado)
                if hasattr(self.page, 'app') and hasattr(self.page.app, 'force_refresh_after_import'):
                    print(f"  🔨 Usando force_refresh_after_import...")
                    success = self.page.app.force_refresh_after_import()
                    
                    if success:
                        print(f"  ✅ Vista recargada con force_refresh")
                    else:
                        print(f"  ⚠️ force_refresh falló, intentando reload...")
                        # Fallback a reload
                        if hasattr(self.page.app, 'reload_current_view'):
                            self.page.app.reload_current_view()
                            print(f"  ✅ Vista recargada con reload")
                
                # Método 2: Usar reload_current_view (moderado)
                elif hasattr(self.page, 'app') and hasattr(self.page.app, 'reload_current_view'):
                    print(f"  🔨 Usando reload_current_view...")
                    self.page.app.reload_current_view()
                    print(f"  ✅ Vista recargada con reload")
                
                # Método 3: Usar refresh simple (básico)
                elif hasattr(self.page, 'app') and hasattr(self.page.app, 'refresh_current_view'):
                    print(f"  🔨 Usando refresh_current_view...")
                    self.page.app.refresh_current_view()
                    print(f"  ✅ Vista refrescada")
                
                # Fallback final: actualizar página
                else:
                    print(f"  ⚠️ Métodos de recarga no disponibles, usando page.update()...")
                    self.page.update()
                    print(f"  ✅ Página actualizada (básico)")
                
                print(f"{'='*60}\n")
                
            except Exception as reload_error:
                print(f"  ⚠️ Error al recargar vista: {reload_error}")
                import traceback
                traceback.print_exc()
                
                # Último intento
                try:
                    self.page.update()
                except:
                    pass

        except Exception as ex:
            print(f"\n{'='*60}")
            print(f"❌ ERROR CRÍTICO EN IMPORTACIÓN")
            print(f"{'='*60}")
            import traceback
            traceback.print_exc()
            print(f"{'='*60}\n")
            
            # Rollback de seguridad
            try:
                self.db.session.rollback()
            except:
                pass
            
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