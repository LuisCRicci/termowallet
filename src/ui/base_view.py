"""
Clase base para todas las vistas
Archivo: src/ui/base_view.py

Esta clase abstracta proporciona funcionalidad común para todas las vistas:
- Acceso a la base de datos
- Manejo de snackbars
- Gestión de diálogos
- Métodos abstractos que deben implementar las vistas hijas
"""

import flet as ft
from abc import ABC, abstractmethod
from typing import Optional, Callable


class BaseView(ABC):
    """
    Clase base abstracta para todas las vistas de la aplicación.
    
    Todas las vistas deben heredar de esta clase e implementar el método build().
    
    Attributes:
        page (ft.Page): Referencia a la página principal de Flet
        db: Instancia del DatabaseManager
        show_snackbar (Callable): Función callback para mostrar mensajes
        content (ft.Control): Contenido actual de la vista
    """

    def __init__(self, page: ft.Page, db_manager, show_snackbar_callback: Callable):
        """
        Inicializa la vista base.
        
        Args:
            page: Página principal de Flet
            db_manager: Instancia del gestor de base de datos
            show_snackbar_callback: Función para mostrar notificaciones
        """
        self.page = page
        self.db = db_manager
        self.show_snackbar = show_snackbar_callback
        self.content = None

    @abstractmethod
    def build(self) -> ft.Control:
        """
        Construye y retorna el contenido de la vista.
        
        Este método debe ser implementado por todas las clases hijas.
        
        Returns:
            ft.Control: El control de Flet que representa el contenido de la vista
            
        Raises:
            NotImplementedError: Si la clase hija no implementa este método
        """
        pass

    def get_content(self) -> ft.Control:
        """
        Retorna el contenido de la vista, construyéndolo si es necesario.
        
        Returns:
            ft.Control: El contenido de la vista
        """
        if self.content is None:
            self.content = self.build()
        return self.content

    def refresh(self):
        """
        Refresca la vista reconstruyendo su contenido.
        
        Útil cuando los datos han cambiado y la vista necesita actualizarse.
        """
        self.content = self.build()

    def close_dialog(self):
        """
        ⭐ CORRECCIÓN: Cierra diálogos SIN remover del overlay
        Solo cambia open=False y actualiza la página
        """
        if self.page.overlay and len(self.page.overlay) > 0:
            for control in self.page.overlay:
                if isinstance(control, ft.AlertDialog):
                    control.open = False
        self.page.update()

    def show_dialog(self, dialog: ft.AlertDialog):
        """Muestra un diálogo en la página"""
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def show_loading(self, message: str = "Cargando..."):
        """
        Muestra un indicador de carga.
        
        Args:
            message: Mensaje a mostrar junto al indicador
        """
        loading_dialog = ft.AlertDialog(
            modal=True,
            content=ft.Column(
                [
                    ft.ProgressRing(),
                    ft.Text(message, text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
            ),
        )
        self.show_dialog(loading_dialog)

    def update_page(self):
        """
        Actualiza la página de Flet.
        
        Útil para refrescar la UI después de cambios.
        """
        self.page.update()

    def on_error(self, error: Exception, message: str = "Ha ocurrido un error"):
        """
        Maneja errores mostrando un mensaje al usuario.
        
        Args:
            error: La excepción que ocurrió
            message: Mensaje personalizado para el usuario
        """
        error_message = f"{message}: {str(error)}"
        print(f"❌ ERROR: {error_message}")
        self.show_snackbar(error_message, error=True)

    def confirm_action(
        self,
        title: str,
        message: str,
        on_confirm: Callable,
        confirm_text: str = "Confirmar",
        cancel_text: str = "Cancelar",
        is_dangerous: bool = False
    ):
        """
        Muestra un diálogo de confirmación antes de ejecutar una acción.
        
        Args:
            title: Título del diálogo
            message: Mensaje de confirmación
            on_confirm: Función a ejecutar si el usuario confirma
            confirm_text: Texto del botón de confirmación
            cancel_text: Texto del botón de cancelar
            is_dangerous: Si True, el botón de confirmación será rojo
        """
        def handle_confirm(e):
            self.close_dialog()
            on_confirm(e)

        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton(cancel_text, on_click=lambda _: self.close_dialog()),
                ft.ElevatedButton(
                    confirm_text,
                    on_click=handle_confirm,
                    style=ft.ButtonStyle(
                        bgcolor="#ef4444" if is_dangerous else None,
                        color=ft.Colors.WHITE if is_dangerous else None,
                    ),
                ),
            ],
        )
        self.show_dialog(dialog)