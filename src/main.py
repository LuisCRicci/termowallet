"""
Aplicación Principal - ✅ VERSIÓN CON DIAGNÓSTICO DETALLADO
Archivo: src/main.py
"""

import sys
import os

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import flet as ft
from datetime import datetime

print("\n" + "="*70)
print("🚀 TERMOWALLET - INICIANDO")
print("="*70)

# ✅ DIAGNÓSTICO INICIAL
print("\n📋 DIAGNÓSTICO DEL SISTEMA:")
print(f"   Python: {sys.version}")
print(f"   Platform: {sys.platform}")
print(f"   Executable: {sys.executable}")

# Verificar si es Android
def check_android():
    """Verifica múltiples formas si es Android"""
    checks = {
        "ANDROID_ROOT": 'ANDROID_ROOT' in os.environ,
        "getandroidapilevel": hasattr(sys, 'getandroidapilevel'),
        "/system/build.prop": os.path.exists('/system/build.prop'),
    }
    
    try:
        import android
        checks["android module"] = True
    except ImportError:
        checks["android module"] = False
    
    is_android = any(checks.values())
    
    print(f"\n🔍 Detección de Android:")
    for key, value in checks.items():
        status = "✅" if value else "❌"
        print(f"   {status} {key}: {value}")
    
    print(f"\n   🎯 Resultado: {'ANDROID' if is_android else 'DESKTOP'}")
    
    # Check modules
    print("\n🔍 Verificando módulos críticos:")
    modules = ['flet', 'sqlalchemy', 'openpyxl', 'certifi', 'dateutil']
    for mod in modules:
        try:
            __import__(mod)
            print(f"   ✅ {mod}: OK")
        except ImportError as e:
            print(f"   ❌ {mod}: NO ENCONTRADO ({e})")
            
    return is_android

IS_ANDROID = check_android()

# ✅ SOLICITAR PERMISOS EN ANDROID (OPCIONAL, NO BLOQUEANTE)
if IS_ANDROID:
    print("\n📱 Detectado Android - Verificando permisos...")
    try:
        from src.utils.android_permissions import request_permissions
        print("   Solicitando permisos...")
        request_permissions()
        print("   ✅ Permisos procesados")
    except Exception as e:
        print(f"   ⚠️ No se pudieron solicitar permisos: {e}")
        print("   ℹ️ Continuando sin solicitud automática")

# ✅ IMPORTAR MÓDULOS CON DIAGNÓSTICO DETALLADO
print("\n📦 CARGANDO MÓDULOS:")

def safe_import(module_path, class_name):
    """Importa un módulo de forma segura con diagnóstico"""
    try:
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)
        print(f"   ✅ {class_name} importado correctamente")
        return cls
    except Exception as e:
        print(f"   ❌ Error importando {class_name}:")
        print(f"      {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# Importar componentes críticos
Config = safe_import('src.utils.config', 'Config')
DatabaseManager = safe_import('src.data.database', 'DatabaseManager')
AuthManager = safe_import('src.business.auth_manager', 'AuthManager')
LoginView = safe_import('src.ui.login_view', 'LoginView')

# Importar vistas
print("\n   📱 Cargando vistas...")
try:
    from src.ui import (
        HomeView,
        BudgetView,
        AddTransactionView,
        HistoryView,
        ChartsView,
        CategoriesView,
        SettingsView
    )
    print("   ✅ Todas las vistas importadas")
except Exception as e:
    print(f"   ❌ Error importando vistas: {e}")
    HomeView = BudgetView = AddTransactionView = None
    HistoryView = ChartsView = CategoriesView = SettingsView = None

print("\n" + "="*70)


class ExpenseTrackerApp:
    """Clase principal de la aplicación TermoWallet"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "TermoWallet"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.bgcolor = "#f5f5f5"

        print("\n🏗️  INICIALIZANDO APLICACIÓN...")

        # Verificar componentes críticos
        if not Config:
            print("❌ Config no disponible")
            self.show_critical_error("Config no pudo cargarse")
            return

        # Verificar configuración
        print(f"\n📊 VERIFICANDO CONFIGURACIÓN:")
        try:
            print(f"   BASE_DIR: {Config.BASE_DIR}")
            print(f"   DATA_DIR: {Config.DATA_DIR}")
            print(f"   DB_PATH: {Config.DB_PATH}")
            
            # Verificar que DATA_DIR existe
            if Config.DATA_DIR and os.path.exists(Config.DATA_DIR):
                print(f"   ✅ DATA_DIR existe")
            else:
                print(f"   ⚠️ DATA_DIR no existe, creando...")
                Config.ensure_data_directory()
            
            # Verificar permisos de escritura
            test_file = os.path.join(Config.DATA_DIR, ".app_init_test")
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                print(f"   ✅ Permisos de escritura OK")
            except Exception as e:
                print(f"   ❌ Sin permisos de escritura: {e}")
                self.show_permission_error()
                return
                
        except Exception as e:
            print(f"   ❌ Error verificando configuración: {e}")
            import traceback
            traceback.print_exc()

        # Inicializar base de datos
        self.db = None
        if DatabaseManager and Config:
            try:
                print(f"\n💾 INICIALIZANDO BASE DE DATOS...")
                db_path = Config.DB_PATH
                print(f"   Ruta: {db_path}")
                
                # Verificar directorio padre
                db_dir = os.path.dirname(db_path)
                if not os.path.exists(db_dir):
                    print(f"   Creando directorio: {db_dir}")
                    os.makedirs(db_dir, mode=0o755, exist_ok=True)
                
                self.db = DatabaseManager(db_path)
                print(f"   ✅ Base de datos inicializada")
                
            except Exception as e:
                print(f"   ❌ Error inicializando BD: {e}")
                import traceback
                traceback.print_exc()
                self.show_database_error(str(e))
                return

        # Sistema de autenticación
        self.auth = None
        if AuthManager and self.db:
            try:
                print(f"\n🔐 INICIALIZANDO AUTENTICACIÓN...")
                self.auth = AuthManager(self.db)
                print(f"   ✅ Sistema de autenticación OK")
            except Exception as e:
                print(f"   ❌ Error en autenticación: {e}")
                import traceback
                traceback.print_exc()

        # Estado actual
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        self.current_view = "home"
        self.views = {}
        self.is_authenticated = False
        
        print("\n✅ APLICACIÓN INICIALIZADA\n")

    def show_critical_error(self, message: str):
        """Muestra error crítico que impide continuar"""
        error_view = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=80, color="#ef4444"),
                    ft.Text(
                        "Error Crítico",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color="#ef4444",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Divider(height=20, color="transparent"),
                    ft.Text(
                        message,
                        size=16,
                        text_align=ft.TextAlign.CENTER,
                        color="#666666",
                    ),
                    ft.Divider(height=30, color="transparent"),
                    ft.Text(
                        "La aplicación no puede continuar.",
                        size=14,
                        text_align=ft.TextAlign.CENTER,
                        color="#999999",
                        italic=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=40,
            expand=True,
            alignment=ft.alignment.center,
        )
        
        self.page.clean()
        self.page.add(error_view)
        self.page.update()

    def show_permission_error(self):
        """Muestra error de permisos con instrucciones"""
        error_view = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.LOCK, size=80, color="#f59e0b"),
                    ft.Text(
                        "Permisos Necesarios",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color="#f59e0b",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Divider(height=15, color="transparent"),
                    ft.Text(
                        "La aplicación necesita permisos de almacenamiento para funcionar.",
                        size=14,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Divider(height=20, color="transparent"),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                "📱 Pasos para conceder permisos:",
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color="#3b82f6",
                            ),
                            ft.Text("1. Ve a Ajustes de tu dispositivo", size=13),
                            ft.Text("2. Busca 'TermoWallet' en Apps", size=13),
                            ft.Text("3. Toca en 'Permisos'", size=13),
                            ft.Text("4. Activa 'Almacenamiento' y 'Archivos y multimedia'", size=13),
                            ft.Text("5. Reinicia la aplicación", size=13),
                        ], spacing=8),
                        padding=20,
                        bgcolor="#f0f9ff",
                        border_radius=10,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            padding=30,
            expand=True,
            alignment=ft.alignment.center,
        )
        
        self.page.clean()
        self.page.add(error_view)
        self.page.update()

    def show_database_error(self, error_msg: str):
        """Muestra error específico de base de datos"""
        
        # Analizar el error
        suggestions = []
        
        if "Permission denied" in error_msg or "Errno 13" in error_msg:
            suggestions = [
                "• Verifica los permisos de la app en Ajustes",
                "• Asegúrate de tener espacio disponible",
                "• Intenta reinstalar la aplicación",
            ]
        elif "disk I/O error" in error_msg:
            suggestions = [
                "• Tu dispositivo puede estar sin espacio",
                "• Libera espacio de almacenamiento",
                "• Verifica que la SD (si usas) no esté dañada",
            ]
        else:
            suggestions = [
                "• Reinstala la aplicación",
                "• Verifica permisos en Ajustes",
                "• Contacta soporte si persiste",
            ]
        
        error_view = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.ERROR, size=80, color="#ef4444"),
                    ft.Text(
                        "Error inicializando base de datos",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color="#ef4444",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Divider(height=10, color="transparent"),
                    ft.Container(
                        content=ft.Text(
                            error_msg,
                            size=12,
                            color="#666666",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        padding=15,
                        bgcolor="#fee",
                        border_radius=8,
                    ),
                    ft.Divider(height=15, color="transparent"),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                "💡 Sugerencias:",
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color="#3b82f6",
                            ),
                            *[ft.Text(s, size=13) for s in suggestions],
                        ], spacing=5),
                        padding=20,
                        bgcolor="#f0f9ff",
                        border_radius=10,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=30,
            expand=True,
            alignment=ft.alignment.center,
        )
        
        self.page.clean()
        self.page.add(error_view)
        self.page.update()

    def start(self):
        """Inicia la aplicación"""
        print("🎬 INICIANDO INTERFAZ...")
        
        # Verificar dependencias críticas
        if not self.db or not self.auth or not LoginView:
            missing = []
            if not self.db: missing.append("Base de datos")
            if not self.auth: missing.append("Autenticación")
            if not LoginView: missing.append("Vista de login")
            
            print(f"❌ Componentes faltantes: {', '.join(missing)}")
            
            self.show_startup_error(missing)
            return
        
        # Mostrar login
        self.show_login()

    def show_startup_error(self, missing_components):
        """Muestra error de inicio con componentes faltantes"""
        error_list = "\n".join([f"• {c}" for c in missing_components])
        
        error_view = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.WARNING, size=80, color="#f59e0b"),
                    ft.Text(
                        "Error al iniciar la aplicación",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color="#f59e0b",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Divider(height=15, color="transparent"),
                    ft.Text(
                        "No se pudieron cargar los siguientes componentes:",
                        size=14,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(
                        content=ft.Text(
                            error_list,
                            size=13,
                            color="#666666",
                        ),
                        padding=15,
                        bgcolor="#fffbeb",
                        border_radius=8,
                    ),
                    ft.Divider(height=20, color="transparent"),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                "🔧 Soluciones:",
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color="#3b82f6",
                            ),
                            ft.Text("1. Concede permisos de almacenamiento en Ajustes", size=13),
                            ft.Text("2. Verifica que tengas espacio disponible (mín. 50 MB)", size=13),
                            ft.Text("3. Reinstala la aplicación si el problema persiste", size=13),
                        ], spacing=8),
                        padding=20,
                        bgcolor="#f0f9ff",
                        border_radius=10,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=30,
            expand=True,
            alignment=ft.alignment.center,
        )
        
        self.page.add(error_view)
        self.page.update()

    def show_login(self):
        """Muestra la pantalla de login"""
        print("🔐 Mostrando pantalla de login...")
        
        try:
            self.page.clean()
            self.page.appbar = None
            self.page.floating_action_button = None
            
            login_view = LoginView(
                self.page,
                self.auth,
                on_success=self.on_login_success
            )
            
            self.page.add(login_view.build())
            self.page.update()
            print("✅ Login mostrado correctamente")
            
        except Exception as e:
            print(f"❌ Error mostrando login: {e}")
            import traceback
            traceback.print_exc()
            self.show_startup_error(["Vista de login"])

    def on_login_success(self):
        """Callback cuando el login es exitoso"""
        print("✅ Login exitoso - Cargando aplicación principal...")
        
        try:
            self.is_authenticated = True
            self.page.clean()
            self.setup_ui()
            self.load_view("home")
            
        except Exception as e:
            print(f"❌ Error después del login: {e}")
            import traceback
            traceback.print_exc()

    def setup_ui(self):
        """Configura la estructura principal de la UI"""
        try:
            self.page.appbar = ft.AppBar(
                title=ft.Text("💰 TermoWallet", size=20, weight=ft.FontWeight.BOLD),
                center_title=True,
                bgcolor="#2196F3",
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

            self.main_container = ft.Container(
                content=ft.Column([]),
                expand=True,
                padding=10,
                bgcolor="#f5f5f5",
            )

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

            self.page.add(
                ft.Column([self.main_container, self.nav_bar], expand=True, spacing=0)
            )
            
            print("✅ UI principal configurada")
            
        except Exception as e:
            print(f"❌ Error configurando UI: {e}")
            import traceback
            traceback.print_exc()

    def logout(self):
        """Cierra sesión"""
        def confirm_logout(e):
            try:
                self.page.close(dialog)
            except:
                pass
            self.is_authenticated = False
            self.views.clear()
            self.show_login()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Cerrar Sesión"),
            content=ft.Text("¿Está seguro que desea cerrar sesión?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dialog)),
                ft.ElevatedButton(
                    "Cerrar Sesión",
                    on_click=confirm_logout,
                    style=ft.ButtonStyle(bgcolor="#ef4444", color=ft.Colors.WHITE),
                ),
            ],
        )
        
        self.page.open(dialog)

    def on_nav_change(self, e):
        """Maneja el cambio de navegación"""
        try:
            selected = e.control.selected_index
            view_map = {
                0: "home", 1: "add", 2: "history", 3: "charts",
                4: "categories", 5: "budget", 6: "settings"
            }
            self.load_view(view_map.get(selected, "home"))
        except Exception as e:
            print(f"❌ Error en navegación: {e}")

    def handle_nav_change_from_view(self, index: int):
        """Maneja cambios de navegación desde las vistas"""
        self.nav_bar.selected_index = index
        self.on_nav_change(type('obj', (object,), {'control': type('obj', (object,), {'selected_index': index})()})())

    def handle_month_change(self, month: int, year: int):
        """Maneja cambios de mes"""
        self.current_month = month
        self.current_year = year
        self.refresh_current_view()

    def get_or_create_view(self, view_name: str):
        """Obtiene o crea una vista"""
        if view_name in self.views:
            return self.views[view_name]

        try:
            view_classes = {
                "home": HomeView,
                "add": AddTransactionView,
                "history": HistoryView,
                "charts": ChartsView,
                "categories": CategoriesView,
                "budget": BudgetView,
                "settings": SettingsView,
            }
            
            ViewClass = view_classes.get(view_name)
            if not ViewClass:
                return None
            
            # Crear vista con parámetros apropiados
            if view_name == "home":
                view = ViewClass(
                    self.page, self.db, self.show_snackbar,
                    self.current_month, self.current_year,
                    self.handle_month_change, self.handle_nav_change_from_view
                )
            elif view_name in ["history", "charts", "budget"]:
                view = ViewClass(
                    self.page, self.db, self.show_snackbar,
                    self.current_month, self.current_year, self.handle_month_change
                )
            else:
                view = ViewClass(self.page, self.db, self.show_snackbar)
            
            self.views[view_name] = view
            return view
                
        except Exception as e:
            print(f"❌ Error creando vista {view_name}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def load_view(self, view_name: str):
        """Carga una vista"""
        if not self.is_authenticated:
            self.show_login()
            return

        print(f"📱 Cargando vista: {view_name}")

        try:
            self.current_view = view_name
            self.page.floating_action_button = None
            
            view = self.get_or_create_view(view_name)
            
            if view:
                if hasattr(view, 'current_month'):
                    view.current_month = self.current_month
                    view.current_year = self.current_year
                
                content = view.build()
                self.main_container.content = content
                print(f"✅ Vista {view_name} cargada")
            else:
                self.show_snackbar(f"Vista {view_name} no disponible", error=True)
            
            self.page.update()
            
        except Exception as e:
            print(f"❌ Error cargando vista: {e}")
            import traceback
            traceback.print_exc()
            self.show_snackbar(f"Error: {str(e)}", error=True)

    def refresh_current_view(self):
        """Refresca la vista actual"""
        if self.current_view in self.views:
            del self.views[self.current_view]
        self.load_view(self.current_view)

    def show_snackbar(self, message: str, error: bool = False):
        """Muestra un mensaje temporal"""
        try:
            snackbar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor="#ef4444" if error else "#22c55e",
            )
            self.page.open(snackbar)
        except:
            pass


def main(page: ft.Page):
    """Función principal"""
    print("\n" + "="*70)
    print("💰 TERMOWALLET - MAIN")
    print("="*70)

    # Configuración de ventana
    page.window.width = 600
    page.window.height = 900
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#f5f5f5"

    # Loading screen
    loading = ft.Container(
        content=ft.Column(
            [
                ft.ProgressRing(width=60, height=60, color="#2196F3"),
                ft.Text("💰 TermoWallet", size=28, weight=ft.FontWeight.BOLD, color="#2196F3"),
                ft.Text("Iniciando...", size=16, color="#666666"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        ),
        expand=True,
        alignment=ft.alignment.center,
    )
    
    page.add(loading)
    page.update()

    # Inicializar app
    try:
        app = ExpenseTrackerApp(page)
        page.clean()
        app.start()
        print("\n✅ APLICACIÓN LISTA\n")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR FATAL:")
        print(f"   {str(e)}\n")
        import traceback
        traceback.print_exc()
        print("="*70 + "\n")
        
        # Error screen
        page.clean()
        error_view = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.ERROR, size=100, color="#ef4444"),
                    ft.Text("Error Fatal", size=24, weight=ft.FontWeight.BOLD, color="#ef4444"),
                    ft.Text(str(e), size=14, text_align=ft.TextAlign.CENTER),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            padding=40,
            expand=True,
            alignment=ft.alignment.center,
        )
        page.add(error_view)
        page.update()


if __name__ == "__main__":
    ft.app(target=main)