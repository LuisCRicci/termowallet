"""
Vista de gestión de categorías - CON PALABRAS CLAVE
Archivo: src/ui/categories_view.py
"""

import flet as ft
from .base_view import BaseView
from src.utils.config import Config

from .widgets import EmojiPickerDialog, ColorPickerDialog

class CategoriesView(BaseView):
    """Vista de gestión de categorías con palabras clave"""
    
    def __init__(self, page: ft.Page, db_manager, show_snackbar_callback):
        super().__init__(page, db_manager, show_snackbar_callback)
        self.is_saving = False

    def _create_category_tile(self, category):
        """Crea un tile para una categoría CON indicador de palabras clave"""
        keywords_list = category.get_keywords_list()
        keywords_count = len(keywords_list)
        
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
                                category.description if category.description else "Sin descripción",
                                size=12,
                                color=ft.Colors.GREY_600,
                            ),
                            # ✅ NUEVO: Mostrar cantidad de palabras clave
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.KEY, size=14, color="#3b82f6"),
                                        ft.Text(
                                            f"{keywords_count} palabras clave",
                                            size=11,
                                            color="#3b82f6",
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                    ],
                                    spacing=5,
                                ),
                                padding=ft.padding.only(top=5),
                            ) if keywords_count > 0 else ft.Container(),
                        ],
                        expand=True,
                        spacing=2,
                    ),
                    ft.Row(
                        [
                            # ✅ NUEVO: Botón para editar palabras clave
                            ft.IconButton(
                                icon=ft.Icons.LABEL,
                                icon_size=20,
                                tooltip="Palabras clave",
                                icon_color="#667eea",
                                on_click=lambda e, cat=category: self.show_keywords_dialog(cat),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_size=20,
                                tooltip="Editar",
                                on_click=lambda e, cat=category: self.show_edit_category_dialog(cat),
                                disabled=category.is_default,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_size=20,
                                tooltip="Eliminar",
                                on_click=lambda e, cat=category: self.delete_category(cat),
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

    def show_keywords_dialog(self, category):
        """✅ ACTUALIZADO: Muestra diálogo para gestionar palabras clave CON restauración"""
        keywords_list = category.get_keywords_list()
        
        # Campo para agregar nueva palabra clave
        new_keyword_field = ft.TextField(
            label="Nueva palabra clave",
            hint_text="Escribe una palabra y presiona Enter",
            bgcolor=ft.Colors.WHITE,
            on_submit=lambda e: add_keyword(e),
        )
        
        # Lista de palabras clave actuales
        keywords_chips = ft.Row(
            wrap=True,
            spacing=5,
            run_spacing=5,
        )
        
        def update_chips():
            """Actualiza los chips de palabras clave"""
            keywords_chips.controls.clear()
            current_keywords = category.get_keywords_list()
            
            if not current_keywords:
                keywords_chips.controls.append(
                    ft.Text(
                        "No hay palabras clave. Agrega algunas para mejorar la categorización automática.",
                        size=12,
                        color=ft.Colors.GREY_600,
                        italic=True,
                    )
                )
            else:
                for keyword in sorted(current_keywords):
                    keywords_chips.controls.append(
                        ft.Chip(
                            label=ft.Text(keyword, size=12),
                            on_delete=lambda e, k=keyword: remove_keyword(k),
                            bgcolor=ft.Colors.LIGHT_BLUE_100,
                            delete_icon_color=ft.Colors.RED_400,
                        )
                    )
            self.page.update()
        
        def add_keyword(e):
            """Agrega una nueva palabra clave"""
            if not new_keyword_field.value or not new_keyword_field.value.strip():
                return
            
            keyword = new_keyword_field.value.strip().lower()
            current_keywords = category.get_keywords_list()
            
            if keyword in current_keywords:
                self.show_snackbar("Esta palabra clave ya existe", error=True)
                return
            
            current_keywords.append(keyword)
            category.set_keywords_list(current_keywords)
            self.db.session.commit()
            
            new_keyword_field.value = ""
            update_chips()
        
        def remove_keyword(keyword):
            """Elimina una palabra clave"""
            current_keywords = category.get_keywords_list()
            if keyword in current_keywords:
                current_keywords.remove(keyword)
                category.set_keywords_list(current_keywords)
                self.db.session.commit()
                update_chips()
        
        def restore_defaults(e):
            """✅ NUEVO: Restaura palabras clave predeterminadas de esta categoría"""
            # Confirmar antes de restaurar
            def confirm_restore(e):
                result = self.db.restore_default_keywords(category.id)

                # Cerrar diálogo de confirmación
                self.close_dialog()

                if result["success"] and result["updated_count"] > 0:
                    
                    # Actualizar chips dentro del diálogo
                    update_chips()

                    # 🔥 Recargar vista principal para actualizar el contador
                    self._reload_view()

                    self.show_snackbar(f"✅ Keywords restauradas: {category.name}")

                else:
                    self.show_snackbar(result["message"], error=True)

            
            # Diálogo de confirmación
            confirm_dialog = ft.AlertDialog(
                title=ft.Text("Confirmar Restauración"),
                content=ft.Column(
                    [
                        ft.Text(
                            f"¿Restaurar las palabras clave predeterminadas de '{category.name}'?",
                            size=14,
                        ),
                        ft.Container(height=10),
                        ft.Container(
                            content=ft.Text(
                                "⚠️ Se perderán las palabras clave personalizadas actuales",
                                size=12,
                                color="#f59e0b",
                                weight=ft.FontWeight.BOLD,
                            ),
                            padding=10,
                            bgcolor="#fef3c7",
                            border_radius=8,
                        ),
                    ],
                    tight=True,
                ),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                    ft.ElevatedButton(
                        "Restaurar",
                        on_click=confirm_restore,
                        style=ft.ButtonStyle(bgcolor="#3b82f6", color=ft.Colors.WHITE),
                    ),
                ],
            )
            
            self.show_dialog(confirm_dialog)
        
        def save_and_close(e):
            """Guarda y cierra el diálogo"""
            self.close_dialog()
            self.show_snackbar("✅ Palabras clave actualizadas")
            self._reload_view()
        
        # Inicializar chips
        update_chips()
        
        # ✅ NUEVO: Botón de restaurar solo para categorías predeterminadas
        restore_button = None
        if category.is_default:
            restore_button = ft.OutlinedButton(
                "Restaurar defaults",
                icon=ft.Icons.RESTORE,
                on_click=restore_defaults,
                style=ft.ButtonStyle(
                    color="#3b82f6",
                ),
            )
        
        dialog = ft.AlertDialog(
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.LABEL, color=category.color, size=28),
                    ft.Text(
                        f"Palabras clave: {category.name}",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                spacing=10,
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        # Información
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "💡 Las palabras clave ayudan a categorizar automáticamente las transacciones",
                                        size=12,
                                        color=ft.Colors.BLUE_700,
                                    ),
                                    ft.Text(
                                        "Ejemplo: Para 'Alimentación' agrega: pizza, restaurant, supermercado, etc.",
                                        size=11,
                                        color=ft.Colors.GREY_600,
                                        italic=True,
                                    ),
                                ],
                                spacing=5,
                            ),
                            padding=10,
                            bgcolor=ft.Colors.BLUE_50,
                            border_radius=8,
                        ),
                        ft.Divider(height=20),
                        # Campo para agregar
                        new_keyword_field,
                        ft.ElevatedButton(
                            "Agregar",
                            icon=ft.Icons.ADD,
                            on_click=add_keyword,
                            style=ft.ButtonStyle(
                                bgcolor=category.color,
                                color=ft.Colors.WHITE,
                            ),
                        ),
                        ft.Divider(height=20),
                        # Lista de palabras clave
                        ft.Row(
                            [
                                ft.Text(
                                    f"🔑 Palabras clave actuales ({len(category.get_keywords_list())})",
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                # ✅ NUEVO: Badge indicando si es categoría default
                                (
                                    ft.Container(
                                        content=ft.Text(
                                            "Default",
                                            size=10,
                                            color=ft.Colors.WHITE,
                                        ),
                                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                        bgcolor="#3b82f6",
                                        border_radius=10,
                                    )
                                    if category.is_default
                                    else ft.Container()
                                ),
                            ],
                            spacing=10,
                        ),
                        ft.Container(
                            height=200,
                            padding=10,
                            bgcolor=ft.Colors.GREY_50,
                            border_radius=8,
                            content=ft.ListView(
                                controls=[keywords_chips],
                                spacing=5,
                                auto_scroll=False,
                                expand=True,
                            ),
                        ),
                    ],
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=550,
                height=500,
            ),
            actions=[
                ft.TextButton(
                    "Cerrar",
                    on_click=save_and_close,
                ),
                # ✅ NUEVO: Botón de restaurar (solo si es categoría default)
                restore_button if restore_button else ft.Container(),
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN if restore_button else ft.MainAxisAlignment.END,
        )
        
        self.show_dialog(dialog)

    def show_add_category_dialog(self, e):
        """Muestra diálogo para añadir categoría CON palabras clave"""
        self.is_saving = False
        
        name_field = ft.TextField(
            label="Nombre", 
            autofocus=True, 
            bgcolor=ft.Colors.WHITE
        )
        desc_field = ft.TextField(
            label="Descripción", 
            multiline=True, 
            bgcolor=ft.Colors.WHITE
        )
        icon_field = ft.TextField(
            label="Icono (emoji)", 
            value="💰", 
            bgcolor=ft.Colors.WHITE
        )
        color_field = ft.TextField(
            label="Color (hex)", 
            value="#3b82f6", 
            bgcolor=ft.Colors.WHITE
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
        
        # ✅ NUEVO: Campo para palabras clave
        keywords_field = ft.TextField(
            label="Palabras clave (opcional)",
            hint_text="Ejemplo: pizza, restaurant, comida (separadas por comas)",
            multiline=True,
            min_lines=2,
            max_lines=3,
            bgcolor=ft.Colors.WHITE,
        )

        def save_category(e):
            if self.is_saving:
                return
            
            if not name_field.value:
                self.show_snackbar("El nombre es obligatorio", error=True)
                return

            self.is_saving = True
            
            try:
                existing = self.db.get_category_by_name(
                    name_field.value.strip(),
                    type_dropdown.value or "expense"
                )
                
                if existing:
                    self.show_snackbar("Ya existe una categoría con ese nombre", error=True)
                    self.is_saving = False
                    return
                
                # Crear categoría
                category = self.db.add_category(
                    name=name_field.value.strip(),
                    icon=icon_field.value or "💰",
                    color=color_field.value or "#3b82f6",
                    category_type=type_dropdown.value or "expense",
                    description=desc_field.value.strip() if desc_field.value else "",
                )
                
                # ✅ NUEVO: Agregar palabras clave si se proporcionaron
                if keywords_field.value and keywords_field.value.strip():
                    keywords = [
                        k.strip() 
                        for k in keywords_field.value.split(',') 
                        if k.strip()
                    ]
                    category.set_keywords_list(keywords)
                    self.db.session.commit()
                
                self.close_dialog()
                self.show_snackbar("✅ Categoría creada exitosamente")
                self._reload_view()
                
            except Exception as ex:
                self.show_snackbar(f"Error: {str(ex)}", error=True)
                self.is_saving = False

        dialog = ft.AlertDialog(
            title=ft.Text("Nueva Categoría"),
            content=ft.Container(
                content=ft.Column(
                    [
                        name_field, 
                        desc_field, 
                        icon_field, 
                        color_field, 
                        type_dropdown,
                        ft.Divider(height=10),
                        keywords_field,  # ✅ NUEVO
                        ft.Text(
                            "💡 Las palabras clave ayudan a categorizar automáticamente",
                            size=11,
                            color=ft.Colors.GREY_600,
                            italic=True,
                        ),
                    ],
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                height=500,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.ElevatedButton("Guardar", on_click=save_category),
            ],
        )

        self.show_dialog(dialog)

    def show_edit_category_dialog(self, category):
        """Muestra diálogo para editar categoría"""
        self.is_saving = False
        
        name_field = ft.TextField(
            label="Nombre", 
            value=category.name, 
            bgcolor=ft.Colors.WHITE
        )
        desc_field = ft.TextField(
            label="Descripción",
            value=category.description or "",
            multiline=True,
            bgcolor=ft.Colors.WHITE,
        )
        icon_field = ft.TextField(
            label="Icono (emoji)", 
            value=category.icon, 
            bgcolor=ft.Colors.WHITE
        )
        color_field = ft.TextField(
            label="Color (hex)", 
            value=category.color, 
            bgcolor=ft.Colors.WHITE
        )

        def update_category(e):
            if self.is_saving:
                return
                
            if not name_field.value:
                self.show_snackbar("El nombre es obligatorio", error=True)
                return

            self.is_saving = True

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
                self._reload_view()
                
            except Exception as ex:
                self.show_snackbar(f"Error: {str(ex)}", error=True)
                self.is_saving = False

        dialog = ft.AlertDialog(
            title=ft.Text("Editar Categoría"),
            content=ft.Container(
                content=ft.Column(
                    [name_field, desc_field, icon_field, color_field],
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                height=350,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.ElevatedButton("Guardar", on_click=update_category),
            ],
        )

        self.show_dialog(dialog)

    def delete_category(self, category):
        """Elimina una categoría"""
        def confirm_delete(e):
            if self.db.delete_category(category.id):
                self.close_dialog()
                self.show_snackbar("Categoría eliminada")
                self._reload_view()
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

        self.show_dialog(dialog)

    def _reload_view(self):
        """Recarga la vista correctamente"""
        try:
            new_content = self.build()
            
            if hasattr(self.page, 'controls') and len(self.page.controls) > 0:
                main_column = self.page.controls[0]
                if hasattr(main_column, 'controls') and len(main_column.controls) > 0:
                    main_container = main_column.controls[0]
                    main_container.content = new_content
            
            self.page.update()
            
        except Exception as e:
            print(f"❌ Error al recargar vista: {e}")
            import traceback
            traceback.print_exc()

    def build(self) -> ft.Control:
        """Construye la vista de categorías"""
        expense_cats = self.db.get_all_categories("expense")
        income_cats = self.db.get_all_categories("income")

        tabs_content = []

        expense_tiles = [self._create_category_tile(cat) for cat in expense_cats]
        tabs_content.append(
            ft.Tab(
                text="Gastos",
                icon=ft.Icons.TRENDING_DOWN,
                content=ft.Column(expense_tiles, scroll=ft.ScrollMode.AUTO),
            )
        )

        income_tiles = [self._create_category_tile(cat) for cat in income_cats]
        tabs_content.append(
            ft.Tab(
                text="Ingresos",
                icon=ft.Icons.TRENDING_UP,
                content=ft.Column(income_tiles, scroll=ft.ScrollMode.AUTO),
            )
        )

        category_tabs = ft.Tabs(tabs=tabs_content, expand=True)

        return ft.Column(
            [
                ft.Text("🏷️ Categorías", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Text(
                        "💡 Tip: Haz clic en el icono 🏷️ para gestionar las palabras clave de cada categoría",
                        size=12,
                        color=ft.Colors.GREY_600,
                        italic=True,
                    ),
                    padding=10,
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=8,
                ),
                ft.Divider(),
                category_tabs,
            ],
            expand=True,
            spacing=10,
        )