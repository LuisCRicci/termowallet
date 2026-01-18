"""
Configuración de la Aplicación - ✅ SIN JNIUS (evita crashes en Android)
Archivo: src/utils/config.py
"""

import os
import sys
import tempfile
from datetime import datetime


class Config:
    """Configuración global de la aplicación"""

    # Información de la aplicación
    APP_NAME = "TermoWallet"
    APP_VERSION = "1.0.1"
    APP_ORG = "com.termowallet.app"

    # ✅ DETECCIÓN DE PLATAFORMA SIMPLE Y SEGURA (SIN JNIUS)
    @classmethod
    def is_android(cls):
        """
        Detecta si está ejecutándose en Android
        ⚠️ SIN usar jnius para evitar crashes
        """
        # Método 1: API Level (EL MÁS CONFIABLE)
        if hasattr(sys, 'getandroidapilevel'):
            try:
                level = sys.getandroidapilevel()
                print(f"✅ Android API Level detectado: {level}")
                return True
            except:
                pass
        
        # Método 2: Variables de entorno específicas de Android
        android_env_vars = [
            'ANDROID_ARGUMENT',
            'ANDROID_PRIVATE',
            'ANDROID_APP_PATH',
        ]
        
        for var in android_env_vars:
            if var in os.environ:
                value = os.environ[var]
                if '/data/data/' in value or '/data/user/' in value:
                    print(f"✅ Android detectado via {var}: {value}")
                    return True
        
        # Método 3: Verificar archivo específico de Android
        if os.path.exists('/system/build.prop'):
            print("✅ Android detectado via /system/build.prop")
            return True
        
        return False
    
    # ✅ RUTAS SEGURAS SIN JNIUS
    @classmethod
    def get_base_dir(cls):
        """Obtiene el directorio base - SIN JNIUS"""
        
        if cls.is_android():
            print("📱 Plataforma: Android")
            
            # ❌ NO USAR JNIUS - Solo variables de entorno
            for env_var in ['ANDROID_PRIVATE', 'ANDROID_APP_PATH']:
                if env_var in os.environ:
                    base = os.environ[env_var]
                    print(f"✅ Base dir (env {env_var}): {base}")
                    if base and os.path.isabs(base):
                        return base
            
            # Ruta por defecto
            default_path = f"/data/data/{cls.APP_ORG}/files"
            if os.path.exists(default_path):
                print(f"✅ Base dir (default): {default_path}")
                return default_path
            
            # Fallback: temp
            print("⚠️ Usando fallback: tempdir")
            return tempfile.gettempdir()
        
        else:
            print("💻 Plataforma: Desktop")
            
            # Opción 1: Directorio del proyecto
            try:
                current_file = os.path.abspath(__file__)
                base = os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(current_file)
                    )
                )
                
                if os.path.exists(base) and os.access(base, os.W_OK):
                    print(f"✅ Base dir (proyecto): {base}")
                    return base
            except Exception as e:
                print(f"⚠️ Error obteniendo ruta del proyecto: {e}")
            
            # Opción 2: Home del usuario
            home = os.path.expanduser("~")
            app_dir = os.path.join(home, ".termowallet")
            print(f"✅ Base dir (home): {app_dir}")
            return app_dir
    
    @classmethod
    def get_data_dir(cls):
        """✅ Directorio de datos con creación segura"""
        base = cls.get_base_dir()
        
        if base == tempfile.gettempdir():
            data_dir = os.path.join(base, "termowallet_data")
        else:
            data_dir = os.path.join(base, "data")
        
        try:
            if not os.path.exists(data_dir):
                os.makedirs(data_dir, mode=0o755, exist_ok=True)
                print(f"✅ Data dir creado: {data_dir}")
            else:
                print(f"✅ Data dir existe: {data_dir}")
            
            # Verificar permisos
            test_file = os.path.join(data_dir, ".test_write")
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                print(f"✅ Permisos de escritura OK en: {data_dir}")
            except Exception as e:
                print(f"❌ Sin permisos de escritura en {data_dir}: {e}")
                data_dir = os.path.join(tempfile.gettempdir(), "termowallet_data")
                os.makedirs(data_dir, mode=0o755, exist_ok=True)
                print(f"⚠️ Usando temp alternativo: {data_dir}")
            
            return data_dir
            
        except Exception as e:
            print(f"❌ Error creando data_dir: {e}")
            data_dir = os.path.join(tempfile.gettempdir(), "termowallet_data")
            try:
                os.makedirs(data_dir, mode=0o755, exist_ok=True)
            except:
                pass
            print(f"⚠️ Usando fallback: {data_dir}")
            return data_dir
    
    @classmethod
    def get_temp_dir(cls):
        """✅ Directorio temporal - SIN JNIUS"""
        temp_dir = tempfile.gettempdir()
        app_temp = os.path.join(temp_dir, "termowallet_temp")
        
        try:
            os.makedirs(app_temp, mode=0o755, exist_ok=True)
            print(f"✅ Temp dir: {app_temp}")
            return app_temp
        except:
            return temp_dir
    
    @classmethod
    def get_reports_dir(cls):
        """
        ✅ Directorio para reportes
        ⚠️ En Android, se usa temp + FilePicker para guardar donde el usuario elija
        """
        if cls.is_android():
            # En Android, usar temp y FilePicker
            return cls.get_temp_dir()
        
        # Desktop: usar carpeta del proyecto
        reports_dir = os.path.join(cls.get_base_dir(), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        return reports_dir
    
    @classmethod
    def get_db_path(cls):
        """Retorna la ruta completa de la base de datos"""
        data_dir = cls.get_data_dir()
        db_path = os.path.join(data_dir, "termowallet.db")
        print(f"📊 DB Path: {db_path}")
        return db_path

    @classmethod
    def initialize_paths(cls):
        """✅ Inicializa las rutas con máxima seguridad - SIN JNIUS"""
        print("\n" + "="*60)
        print("🔧 INICIALIZANDO CONFIGURACIÓN DE RUTAS (SIN JNIUS)")
        print("="*60)
        
        try:
            is_android = cls.is_android()
            platform_name = "Android" if is_android else "Desktop"
            print(f"🖥️ Plataforma detectada: {platform_name}")
            
            cls.BASE_DIR = cls.get_base_dir()
            print(f"📂 BASE_DIR: {cls.BASE_DIR}")
            
            cls.DATA_DIR = cls.get_data_dir()
            print(f"📂 DATA_DIR: {cls.DATA_DIR}")
            
            cls.DB_PATH = cls.get_db_path()
            print(f"📊 DB_PATH: {cls.DB_PATH}")
            
            cls.DATABASE_URL = f"sqlite:///{cls.DB_PATH}"
            
            print("\n🔍 VERIFICACIONES:")
            
            if os.path.exists(cls.DATA_DIR):
                print(f"✅ DATA_DIR existe y es accesible")
            else:
                print(f"⚠️ DATA_DIR no existe, intentando crear...")
                os.makedirs(cls.DATA_DIR, mode=0o755, exist_ok=True)
            
            test_file = os.path.join(cls.DATA_DIR, ".init_test")
            try:
                with open(test_file, 'w') as f:
                    f.write("initialized")
                os.remove(test_file)
                print(f"✅ Permisos de escritura verificados")
            except Exception as e:
                print(f"❌ ERROR: Sin permisos de escritura: {e}")
                raise PermissionError(f"No se puede escribir en {cls.DATA_DIR}")
            
            try:
                stat = os.statvfs(cls.DATA_DIR)
                free_mb = (stat.f_bavail * stat.f_frsize) / (1024 * 1024)
                print(f"💾 Espacio disponible: {free_mb:.1f} MB")
                
                if free_mb < 10:
                    print(f"⚠️ ADVERTENCIA: Poco espacio disponible")
            except:
                pass
            
            print("="*60)
            print("✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE (SIN JNIUS)")
            print("="*60 + "\n")
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR CRÍTICO EN INICIALIZACIÓN:")
            print(f"   {str(e)}")
            import traceback
            traceback.print_exc()
            print("="*60 + "\n")
            
            print("🚨 Intentando configuración de emergencia...")
            
            temp_base = tempfile.gettempdir()
            cls.BASE_DIR = temp_base
            cls.DATA_DIR = os.path.join(temp_base, "termowallet_emergency")
            os.makedirs(cls.DATA_DIR, mode=0o755, exist_ok=True)
            cls.DB_PATH = os.path.join(cls.DATA_DIR, "termowallet.db")
            cls.DATABASE_URL = f"sqlite:///{cls.DB_PATH}"
            
            print(f"⚠️ Usando directorio de emergencia: {cls.DATA_DIR}")
            
            return False

    # Configuración básica
    BASE_DIR = None
    DATA_DIR = None
    DB_NAME = "termowallet.db"
    DB_PATH = None
    DATABASE_URL = None

    # Moneda
    CURRENCY_SYMBOL = "S/"
    CURRENCY_NAME = "Soles"

    # Formatos
    DATE_FORMAT = "%d/%m/%Y"
    DATETIME_FORMAT = "%d/%m/%Y %H:%M"
    MONTH_YEAR_FORMAT = "%B %Y"

    # Límites
    MAX_FILE_SIZE_MB = 10
    MAX_TRANSACTIONS_IMPORT = 10000
    MAX_DESCRIPTION_LENGTH = 255
    MAX_NOTES_LENGTH = 500

    # Colores
    PRIMARY_COLOR = "#2196F3"
    SUCCESS_COLOR = "#4CAF50"
    ERROR_COLOR = "#F44336"
    WARNING_COLOR = "#FF9800"
    INFO_COLOR = "#00BCD4"

    # Categorías predeterminadas
    USE_DEFAULT_CATEGORIES = True

    # Análisis
    DEFAULT_HISTORY_MONTHS = 6

    # UI
    CARD_HEIGHT = 120
    ICON_SIZE_SMALL = 20
    ICON_SIZE_MEDIUM = 28
    ICON_SIZE_LARGE = 40

    # Validaciones
    MIN_AMOUNT = 0.01
    MAX_AMOUNT = 999999.99

    @classmethod
    def ensure_data_directory(cls):
        """Asegura que el directorio de datos existe"""
        try:
            data_dir = cls.get_data_dir()
            if not os.path.exists(data_dir):
                os.makedirs(data_dir, mode=0o755, exist_ok=True)
            print(f"✅ Directorio de datos asegurado: {data_dir}")
        except Exception as e:
            print(f"⚠️ Error asegurando directorio: {e}")

    @classmethod
    def get_current_month_year(cls):
        """Retorna el mes y año actual"""
        now = datetime.now()
        return now.month, now.year


# ✅ INICIALIZAR RUTAS AL IMPORTAR
print("\n🚀 Inicializando Config (SIN JNIUS)...")
try:
    success = Config.initialize_paths()
    if success:
        print("✅ Config inicializado correctamente\n")
    else:
        print("⚠️ Config inicializado con advertencias\n")
except Exception as e:
    print(f"❌ Error fatal inicializando Config: {e}\n")
    import traceback
    traceback.print_exc()


# Colores para categorías
CATEGORY_COLORS = {
    "Alimentos": "#FF5722",
    "Transporte": "#3F51B5",
    "Entretenimiento": "#9C27B0",
    "Salud": "#E91E63",
    "Educación": "#4CAF50",
    "Hogar": "#FFC107",
    "Otros": "#607D8B",
}

CATEGORY_ICONS = {
    "Alimentos": "restaurant",
    "Transporte": "directions_bus",
    "Entretenimiento": "movie",
    "Salud": "local_hospital",
    "Educación": "school",
    "Hogar": "home",
    "Otros": "category",
}


def get_category_color(category_name):
    """Retorna el color asociado a una categoría"""
    return CATEGORY_COLORS.get(category_name, "#9E9E9E")


def get_category_icon(category_name):
    """Retorna el icono asociado a una categoría"""
    return CATEGORY_ICONS.get(category_name, "category")


def format_currency(amount):
    """Formatea un monto con el símbolo de la moneda"""
    return f"{Config.CURRENCY_SYMBOL}{amount:,.2f}"


def parse_currency(formatted_amount):
    """Parsea un monto formateado y retorna su valor numérico"""
    try:
        cleaned_amount = formatted_amount.replace(Config.CURRENCY_SYMBOL, "").replace(",", "")
        return float(cleaned_amount)
    except ValueError:
        raise ValueError("Monto inválido")


def validate_amount(amount):
    """Valida que el monto esté dentro de los límites permitidos"""
    if amount < Config.MIN_AMOUNT or amount > Config.MAX_AMOUNT:
        raise ValueError(
            f"El monto debe estar entre {Config.CURRENCY_SYMBOL}{Config.MIN_AMOUNT} y {Config.CURRENCY_SYMBOL}{Config.MAX_AMOUNT}"
        )
    return True