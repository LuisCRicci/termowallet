"""
Vista de Login con Contraseña
Archivo: src/ui/login_view.py

Pantalla de autenticación con:
- Configuración inicial de contraseña
- Login con validación
- Advertencias de intentos fallidos
- Interfaz moderna y segura
"""

import flet as ft
from typing import Callable


class LoginView:
    """Vista de autenticación"""
    
    def __init__(self, page: ft.Page, auth_manager, on_success: Callable):
        self.page = page
        self.auth = auth_manager
        self.on_success = on_success
        
        # Estados
        self.is_setup_mode = not self.auth.is_password_set()
        self.password_visible = False
        
        # Widgets
        self.password_field = None
        self.confirm_field = None
        self.message_text = None
        self.submit_button = None
    
    def build(self) -> ft.Container:
        """Construye la vista de login"""
        
        if self.is_setup_mode:
            return self._build_setup_screen()
        else:
            return self._build_login_screen()
    
    def _build_setup_screen(self) -> ft.Container:
        """Pantalla de configuración inicial de contraseña"""
        
        self.password_field = ft.TextField(
            label="Crear Contraseña",
            hint_text="Mínimo 4 caracteres",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK,
            border_color="#667eea",
            focused_border_color="#667eea",
            on_submit=lambda _: self._handle_setup(),
        )
        
        self.confirm_field = ft.TextField(
            label="Confirmar Contraseña",
            hint_text="Repita su contraseña",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            border_color="#667eea",
            focused_border_color="#667eea",
            on_submit=lambda _: self._handle_setup(),
        )
        
        self.message_text = ft.Text(
            "",
            size=12,
            color="#ef4444",
            text_align=ft.TextAlign.CENTER,
            visible=False,
        )
        
        self.submit_button = ft.ElevatedButton(
            "Configurar Contraseña",
            icon=ft.Icons.CHECK_CIRCLE,
            on_click=lambda _: self._handle_setup(),
            style=ft.ButtonStyle(
                bgcolor="#667eea",
                color=ft.Colors.WHITE,
                padding=15,
            ),
            width=300,
        )
        
        return ft.Container(
            content=ft.Column(
                [
                    # Logo/Título
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(
                                    ft.Icons.ACCOUNT_BALANCE_WALLET,
                                    size=80,
                                    color="#667eea",
                                ),
                                ft.Text(
                                    "TermoWallet",
                                    size=32,
                                    weight=ft.FontWeight.BOLD,
                                    color="#667eea",
                                ),
                                ft.Container(height=10),
                                ft.Text(
                                    "Configuración Inicial",
                                    size=18,
                                    weight=ft.FontWeight.W_500,
                                    color=ft.Colors.GREY_700,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        margin=ft.margin.only(bottom=40),
                    ),
                    
                    # Instrucciones
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.Icons.INFO_OUTLINE, color="#3b82f6", size=24),
                                ft.Text(
                                    "Por seguridad, configure una contraseña",
                                    size=14,
                                    color=ft.Colors.GREY_700,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Text(
                                    "⚠️ Recuerde su contraseña. Después de 7 intentos fallidos, todos los datos serán eliminados.",
                                    size=12,
                                    color="#f59e0b",
                                    text_align=ft.TextAlign.CENTER,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                        ),
                        padding=15,
                        bgcolor="#eff6ff",
                        border_radius=10,
                        margin=ft.margin.only(bottom=30),
                    ),
                    
                    # Campos
                    ft.Container(
                        content=ft.Column(
                            [
                                self.password_field,
                                ft.Container(height=15),
                                self.confirm_field,
                                ft.Container(height=10),
                                self.message_text,
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        margin=ft.margin.only(bottom=20),
                    ),
                    
                    # Botón
                    self.submit_button,
                    
                    # Info de seguridad
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.SECURITY, size=16, color=ft.Colors.GREY_500),
                                ft.Text(
                                    "Encriptación AES-256",
                                    size=11,
                                    color=ft.Colors.GREY_600,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=5,
                        ),
                        margin=ft.margin.only(top=20),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=30,
            expand=True,
            bgcolor=ft.Colors.WHITE,
            alignment=ft.alignment.center,
        )
    
    def _build_login_screen(self) -> ft.Container:
        """Pantalla de login"""
        
        # Obtener intentos fallidos actuales
        failed_attempts = self.auth.get_failed_attempts()
        
        self.password_field = ft.TextField(
            label="Contraseña",
            hint_text="Ingrese su contraseña",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK,
            border_color="#667eea",
            focused_border_color="#667eea",
            on_submit=lambda _: self._handle_login(),
            autofocus=True,
        )
        
        self.message_text = ft.Text(
            "",
            size=12,
            color="#ef4444",
            text_align=ft.TextAlign.CENTER,
            visible=False,
        )
        
        self.submit_button = ft.ElevatedButton(
            "Iniciar Sesión",
            icon=ft.Icons.LOGIN,
            on_click=lambda _: self._handle_login(),
            style=ft.ButtonStyle(
                bgcolor="#667eea",
                color=ft.Colors.WHITE,
                padding=15,
            ),
            width=300,
        )
        
        # Widget de advertencia según intentos
        warning_widget = self._get_warning_widget(failed_attempts)
        
        return ft.Container(
            content=ft.Column(
                [
                    # Logo/Título
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(
                                    ft.Icons.ACCOUNT_BALANCE_WALLET,
                                    size=80,
                                    color="#667eea",
                                ),
                                ft.Text(
                                    "TermoWallet",
                                    size=32,
                                    weight=ft.FontWeight.BOLD,
                                    color="#667eea",
                                ),
                                ft.Container(height=10),
                                ft.Text(
                                    "Bienvenido de nuevo",
                                    size=18,
                                    weight=ft.FontWeight.W_500,
                                    color=ft.Colors.GREY_700,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        margin=ft.margin.only(bottom=40),
                    ),
                    
                    # Advertencia de intentos (si aplica)
                    warning_widget,
                    
                    # Campo de contraseña
                    ft.Container(
                        content=ft.Column(
                            [
                                self.password_field,
                                ft.Container(height=10),
                                self.message_text,
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        margin=ft.margin.only(bottom=20),
                    ),
                    
                    # Botón
                    self.submit_button,
                    
                    # Contador de intentos
                    ft.Container(
                        content=ft.Text(
                            f"Intentos fallidos: {failed_attempts}/7" if failed_attempts > 0 else "",
                            size=11,
                            color="#f59e0b" if failed_attempts >= 3 else ft.Colors.GREY_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        margin=ft.margin.only(top=15),
                    ),
                    
                    # Info de seguridad
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.SECURITY, size=16, color=ft.Colors.GREY_500),
                                ft.Text(
                                    "Protegido con AES-256",
                                    size=11,
                                    color=ft.Colors.GREY_600,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=5,
                        ),
                        margin=ft.margin.only(top=20),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=30,
            expand=True,
            bgcolor=ft.Colors.WHITE,
            alignment=ft.alignment.center,
        )
    
    def _get_warning_widget(self, failed_attempts: int) -> ft.Container:
        """Genera widget de advertencia según intentos fallidos"""
        
        if failed_attempts == 0:
            return ft.Container()
        
        elif failed_attempts >= 6:
            # Advertencia crítica
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.WARNING, color="#ef4444", size=32),
                        ft.Text(
                            "⚠️ ADVERTENCIA CRÍTICA",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color="#ef4444",
                        ),
                        ft.Divider(height=10, color="#ef4444"),
                        ft.Text(
                            "AL PRÓXIMO INTENTO FALLIDO:",
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color="#991b1b",
                        ),
                        ft.Text(
                            "• La base de datos será RESETEADA\n"
                            "• TODOS los datos serán ELIMINADOS\n"
                            "• NO habrá forma de recuperarlos",
                            size=11,
                            color="#991b1b",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=5),
                        ft.Text(
                            f"Este es su intento #{failed_attempts} de 7",
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color="#ef4444",
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                padding=20,
                bgcolor="#fee2e2",
                border_radius=10,
                border=ft.border.all(2, "#ef4444"),
                margin=ft.margin.only(bottom=30),
            )
        
        elif failed_attempts >= 3:
            # Advertencia media
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.ERROR_OUTLINE, color="#f59e0b", size=28),
                        ft.Text(
                            "⚠️ Cuidado con los intentos fallidos",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color="#92400e",
                        ),
                        ft.Text(
                            f"Llevas {failed_attempts} intentos fallidos de 7.\n"
                            "Al 7º intento se eliminará toda la base de datos.",
                            size=11,
                            color="#92400e",
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                padding=15,
                bgcolor="#fef3c7",
                border_radius=10,
                border=ft.border.all(1, "#f59e0b"),
                margin=ft.margin.only(bottom=20),
            )
        
        else:
            return ft.Container()
    
    def _handle_setup(self):
        """Maneja la configuración inicial de contraseña"""
        
        password = self.password_field.value
        confirm = self.confirm_field.value
        
        # Validaciones
        if not password or not confirm:
            self._show_error("Por favor complete ambos campos")
            return
        
        if len(password) < 4:
            self._show_error("La contraseña debe tener al menos 4 caracteres")
            return
        
        if password != confirm:
            self._show_error("Las contraseñas no coinciden")
            return
        
        # Configurar contraseña
        if self.auth.set_password(password):
            self._show_success("✅ Contraseña configurada correctamente")
            # Esperar un momento y proceder
            self.page.update()
            import time
            time.sleep(1)
            self.on_success()
        else:
            self._show_error("Error al configurar contraseña")
    
    def _handle_login(self):
        """Maneja el intento de login"""
        
        password = self.password_field.value
        
        if not password:
            self._show_error("Por favor ingrese su contraseña")
            return
        
        # Verificar contraseña
        success, message, failed_attempts = self.auth.verify_password(password)
        
        if success:
            self._show_success(message)
            # Esperar un momento y proceder
            self.page.update()
            import time
            time.sleep(0.5)
            self.on_success()
        else:
            # Mostrar error
            self._show_error(message)
            
            # Si es el 7º intento, resetear vista
            if "RESETEADA" in message or "reseteada" in message:
                self.page.update()
                import time
                time.sleep(2)
                # Recargar en modo setup
                self.is_setup_mode = True
                self.page.clean()
                self.page.add(self.build())
                self.page.update()
            else:
                # Limpiar campo
                self.password_field.value = ""
                # Reconstruir vista para actualizar contador
                self.page.clean()
                self.page.add(self.build())
                self.page.update()
    
    def _show_error(self, message: str):
        """Muestra un mensaje de error"""
        self.message_text.value = message
        self.message_text.color = "#ef4444"
        self.message_text.visible = True
        self.page.update()
    
    def _show_success(self, message: str):
        """Muestra un mensaje de éxito"""
        self.message_text.value = message
        self.message_text.color = "#22c55e"
        self.message_text.visible = True
        self.page.update()