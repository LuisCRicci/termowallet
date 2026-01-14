"""
Aplicación Principal - Dashboard de Gastos Personales (REFACTORIZADA)
Archivo: src/main.py

Ejecutar con: flet run src/main.py
VERSIÓN MODULARIZADA CON VISTAS SEPARADAS
CARACTERÍSTICAS:
✅ Login con contraseña al inicio
✅ Encriptación AES-256
✅ Protección contra fuerza bruta (7 intentos)
✅ Reseteo automático al 7º intento fallido

"""

import sys
import os

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import flet as ft
from datetime import datetime
from src.data.database import DatabaseManager
from src.utils.config import Config
from src.business.auth_manager import AuthManager
from src.ui.login_view import LoginView

# Importar vistas modularizadas
from src.ui import (
    HomeView,
    BudgetView,  # ⭐ AGREGAR
    AddTransactionView,
    HistoryView,
    ChartsView,
    CategoriesView,
    SettingsView
)


class ExpenseTrackerApp:
    """Clase principal de la aplicación TermoWallet"""

    def __init__(self, page: ft.Page):
        self.page = page

        print("🚀 Inicializando TermoWallet...")

        # Inicializar base de datos
        try:
            self.db = DatabaseManager(Config.get_db_path())
            print("✅ Base de datos inicializada")
        except Exception as e:
            print(f"❌ Error inicializando BD: {e}")
            import traceback
            traceback.print_exc()

        # ✅ NUEVO: Inicializar sistema de autenticación
        try:
            self.auth = AuthManager(self.db)
            print("✅ Sistema de autenticación inicializado")
        except Exception as e:
            print(f"❌ Error inicializando autenticación: {e}")
            import traceback
            traceback.print_exc()

        # Configuración de la página
        self.page.title = Config.APP_NAME
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.bgcolor = "#f5f5f5"

        # Estado actual
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        self.current_view = "home"

        # Inicializar vistas (lazy loading)
        self.views = {}
        
        # Flag de autenticación
        self.is_authenticated = False

    def start(self):
        """Inicia la aplicación (primero muestra login)"""
        # ✅ Mostrar pantalla de login
        self.show_login()

    def show_login(self):
        """Muestra la pantalla de login"""
        print("\n🔐 Mostrando pantalla de login...")
        
        # Limpiar página
        self.page.clean()
        self.page.appbar = None
        self.page.floating_action_button = None
        
        # Crear vista de login
        login_view = LoginView(
            self.page,
            self.auth,
            on_success=self.on_login_success
        )
        
        # Mostrar login
        self.page.add(login_view.build())
        self.page.update()

    def on_login_success(self):
        """Callback cuando el login es exitoso"""
        print("✅ Login exitoso - Cargando aplicación principal...")
        
        self.is_authenticated = True
        
        # Limpiar página
        self.page.clean()
        
        # Configurar UI principal
        self.setup_ui()
        self.load_view("home")

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
                ),
                ft.IconButton(
                    icon=ft.Icons.LOGOUT,
                    icon_color=ft.Colors.WHITE,
                    on_click=lambda _: self.logout(),
                    tooltip="Cerrar Sesión",
                ),
            ],
        )

        # Contenedor principal
        self.main_container = ft.Container(
            content=ft.Column([]),
            expand=True,
            padding=10,
            bgcolor="#f5f5f5",
        )

        # Navigation Bar
        self.nav_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Inicio"),
                ft.NavigationBarDestination(icon=ft.Icons.ADD_CIRCLE, label="Añadir"),
                ft.NavigationBarDestination(icon=ft.Icons.LIST, label="Historial"),
                ft.NavigationBarDestination(icon=ft.Icons.PIE_CHART, label="Gráficos"),
                ft.NavigationBarDestination(icon=ft.Icons.CATEGORY, label="Categorías"),
                ft.NavigationBarDestination(icon=ft.Icons.ACCOUNT_BALANCE_WALLET, label="Presupuesto"),
                ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Ajustes"),
            ],
            on_change=self.on_nav_change,
            selected_index=0,
        )

        # Layout principal
        self.page.add(
            ft.Column([self.main_container, self.nav_bar], expand=True, spacing=0)
        )

    def logout(self):
        """Cierra sesión y vuelve al login"""
        print("🔓 Cerrando sesión...")
        
        # Confirmar logout
        def confirm_logout(e):
            self.page.close(dialog)
            self.is_authenticated = False
            self.views.clear()  # Limpiar vistas en caché
            self.show_login()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Cerrar Sesión"),
            content=ft.Text("¿Está seguro que desea cerrar sesión?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dialog)),
                ft.ElevatedButton(
                    "Cerrar Sesión",
                    on_click=confirm_logout,
                    style=ft.ButtonStyle(
                        bgcolor="#ef4444",
                        color=ft.Colors.WHITE,
                    ),
                ),
            ],
        )
        
        self.page.open(dialog)

    def on_nav_change(self, e):
        """Maneja el cambio de navegación"""
        selected = e.control.selected_index

        view_map = {
            0: "home",
            1: "add",
            2: "history",
            3: "charts",
            4: "categories",
            5: "budget",
            6: "settings"
        }

        view_name = view_map.get(selected, "home")
        self.load_view(view_name)

    def handle_nav_change_from_view(self, index: int):
        """Maneja cambios de navegación desde las vistas"""
        self.nav_bar.selected_index = index
        self.on_nav_change(type('obj', (object,), {'control': type('obj', (object,), {'selected_index': index})()})())

    def handle_month_change(self, month: int, year: int):
        """Maneja cambios de mes desde las vistas"""
        self.current_month = month
        self.current_year = year
        self.refresh_current_view()

    def get_or_create_view(self, view_name: str):
        """Obtiene una vista existente o crea una nueva (lazy loading)"""
        if view_name in self.views:
            return self.views[view_name]

        # Crear la vista según el nombre
        if view_name == "home":
            view = HomeView(
                self.page,
                self.db,
                self.show_snackbar,
                self.current_month,
                self.current_year,
                self.handle_month_change,
                self.handle_nav_change_from_view
            )
        elif view_name == "add":
            view = AddTransactionView(
                self.page,
                self.db,
                self.show_snackbar
            )
        elif view_name == "history":
            view = HistoryView(
                self.page,
                self.db,
                self.show_snackbar,
                self.current_month,
                self.current_year,
                self.handle_month_change
            )
        elif view_name == "charts":
            view = ChartsView(
                self.page,
                self.db,
                self.show_snackbar,
                self.current_month,
                self.current_year,
                self.handle_month_change
            )
        elif view_name == "categories":
            view = CategoriesView(
                self.page,
                self.db,
                self.show_snackbar
            )
        elif view_name == "budget":
            view = BudgetView(
                self.page,
                self.db,
                self.show_snackbar,
                self.current_month,
                self.current_year,
                self.handle_month_change
            )
        elif view_name == "settings":
            view = SettingsView(
                self.page,
                self.db,
                self.show_snackbar
            )
        else:
            view = HomeView(
                self.page,
                self.db,
                self.show_snackbar,
                self.current_month,
                self.current_year,
                self.handle_month_change,
                self.handle_nav_change_from_view
            )

        self.views[view_name] = view
        return view

    def load_view(self, view_name: str):
        """Carga una vista específica"""
        # Verificar autenticación
        if not self.is_authenticated:
            print("⚠️ Intento de acceso sin autenticación")
            self.show_login()
            return

        print(f"\n{'='*60}")
        print(f"📱 CARGANDO VISTA: {view_name.upper()}")
        print(f"{'='*60}")

        self.current_view = view_name

        # Configurar FAB según la vista
        if view_name == "home":
            self.page.floating_action_button = ft.FloatingActionButton(
                icon=ft.Icons.ADD,
                bgcolor=Config.PRIMARY_COLOR,
                tooltip="Añadir transacción",
                on_click=lambda _: self.load_view("add"),
            )
        elif view_name == "categories":
            view = self.get_or_create_view(view_name)
            self.page.floating_action_button = ft.FloatingActionButton(
                icon=ft.Icons.ADD,
                on_click=view.show_add_category_dialog,
                tooltip="Añadir categoría",
                bgcolor=Config.PRIMARY_COLOR,
            )
        elif view_name == "charts":
            view = self.get_or_create_view(view_name)
            self.page.floating_action_button = ft.FloatingActionButton(
                icon=ft.Icons.DOWNLOAD,
                tooltip="Generar Reporte",
                on_click=view.show_report_dialog,
                bgcolor="#667eea",
            )
        else:
            self.page.floating_action_button = None

        # Obtener o crear la vista
        view = self.get_or_create_view(view_name)

        # Actualizar mes/año en vistas que lo necesiten
        if hasattr(view, 'current_month'):
            view.current_month = self.current_month
            view.current_year = self.current_year

        # Construir contenido
        try:
            content = view.build()
            self.main_container.content = content
            print(f"✅ Vista {view_name.upper()} cargada exitosamente")
        except Exception as e:
            print(f"❌ Error al cargar vista {view_name}: {e}")
            import traceback
            traceback.print_exc()
            self.show_snackbar(f"Error al cargar vista: {str(e)}", error=True)

        self.page.update()

    def refresh_current_view(self):
        """Refresca la vista actual"""
        print(f"🔄 Refrescando vista: {self.current_view}")
        
        # Eliminar vista del cache para forzar reconstrucción
        if self.current_view in self.views:
            del self.views[self.current_view]
        
        # Recargar vista
        self.load_view(self.current_view)

    def show_snackbar(self, message: str, error: bool = False):
        """Muestra un mensaje temporal"""
        snackbar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor="#ef4444" if error else "#22c55e",
        )
        self.page.open(snackbar)


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
        # ✅ Iniciar con login
        app.start()
        print("\n✅ Aplicación inicializada correctamente\n")
    except Exception as e:
        print(f"\n❌ ERROR FATAL al inicializar:")
        print(f"   {str(e)}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    ft.app(target=main)