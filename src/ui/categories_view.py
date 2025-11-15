"""
Vista de gestión de categorías - SOLUCIÓN FINAL
Archivo: src/ui/categories_view.py
"""

import flet as ft
from .base_view import BaseView
from src.utils.config import Config

class CategoriesView(BaseView):
    """Vista de gestión de categorías"""
    
    def __init__(self, page: ft.Page, db_manager, show_snackbar_callback):
        super().__init__(page, db_manager, show_snackbar_callback)
        self.is_saving = False  # Flag para evitar clics múltiples
        self.on_refresh_callback = None  # ⭐ NUEVO: Callback para refrescar desde main

    def set_refresh_callback(self, callback):
        """⭐ NUEVO: Establece el callback para refrescar la vista"""
        self.on_refresh_callback = callback

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
        self.is_saving = False  # Reset flag
        
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
            # Evitar clics múltiples
            if self.is_saving:
                return
            
            if not name_field.value:
                self.show_snackbar("El nombre es obligatorio", error=True)
                return

            self.is_saving = True  # Bloquear
            
            try:
                # Verificar si ya existe
                existing = self.db.get_category_by_name(
                    name_field.value.strip(),
                    type_dropdown.value or "expense"
                )
                
                if existing:
                    self.show_snackbar("Ya existe una categoría con ese nombre", error=True)
                    self.is_saving = False
                    return
                
                self.db.add_category(
                    name=name_field.value.strip(),
                    icon=icon_field.value or "💰",
                    color=color_field.value or "#3b82f6",
                    category_type=type_dropdown.value or "expense",
                    description=desc_field.value.strip() if desc_field.value else "",
                )
                
                self.close_dialog()
                self.show_snackbar("✅ Categoría creada exitosamente")
                
                # ⭐ USAR CALLBACK PARA REFRESCAR
                if self.on_refresh_callback:
                    self.on_refresh_callback()
                
            except Exception as ex:
                self.show_snackbar(f"Error: {str(ex)}", error=True)
                self.is_saving = False

        dialog = ft.AlertDialog(
            title=ft.Text("Nueva Categoría"),
            content=ft.Container(
                content=ft.Column(
                    [name_field, desc_field, icon_field, color_field, type_dropdown],
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
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
        self.is_saving = False  # Reset flag
        
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
            # Evitar clics múltiples
            if self.is_saving:
                return
                
            if not name_field.value:
                self.show_snackbar("El nombre es obligatorio", error=True)
                return

            self.is_saving = True  # Bloquear

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
                
                # ⭐ USAR CALLBACK PARA REFRESCAR
                if self.on_refresh_callback:
                    self.on_refresh_callback()
                
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

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def delete_category(self, category):
        """Elimina una categoría"""
        def confirm_delete(e):
            if self.db.delete_category(category.id):
                self.close_dialog()
                self.show_snackbar("Categoría eliminada")
                
                # ⭐ USAR CALLBACK PARA REFRESCAR
                if self.on_refresh_callback:
                    self.on_refresh_callback()
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
                ft.Divider(),
                category_tabs,
            ],
            expand=True,
            spacing=10,
        )