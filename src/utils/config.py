"""
Configuración de la Aplicación
Archivo: src/utils/config.py
"""

import os
from datetime import datetime


class Config:
    """Configuración global de la aplicación"""

    # Información de la aplicación
    APP_NAME = "TermoWallet"
    APP_VERSION = "1.0.0"
    APP_ORG = "com.termowallet.app"

    # ✅ RUTAS ADAPTATIVAS PARA ANDROID
    @classmethod
    def get_data_dir(cls):
        """Obtiene el directorio de datos según la plataforma"""
        import sys
        if hasattr(sys, 'getandroidapilevel'):
            # Android: usar directorio de datos de la app
            import os
            return os.path.join(
                os.path.expanduser("~"), 
                ".termowallet"
            )
        else:
            # Desktop: usar directorio del proyecto
            import os
            BASE_DIR = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(__file__)
                )
            )
            return os.path.join(BASE_DIR, "data")
    
    @classmethod
    def get_db_path(cls):
        """Retorna la ruta completa de la base de datos"""
        import os
        data_dir = cls.get_data_dir()
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, "termowallet.db")

    # Base de datos
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    DB_NAME = "termowallet.db"
    DB_PATH = os.path.join(BASE_DIR, DB_NAME)
    DATABASE_URL = f"sqlite:///{DB_PATH}"

    # Crear directorio de datos si no existe
    os.makedirs(DATA_DIR, exist_ok=True)

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

    # Colores (Material Design)
    PRIMARY_COLOR = "#2196F3"  # Blue
    SUCCESS_COLOR = "#4CAF50"  # Green
    ERROR_COLOR = "#F44336"  # Red
    WARNING_COLOR = "#FF9800"  # Orange
    INFO_COLOR = "#00BCD4"  # Cyan

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
    def get_db_path(cls):
        """Retorna la ruta completa de la base de datos"""
        return cls.DB_PATH

    @classmethod
    def ensure_data_directory(cls):
        """Asegura que el directorio de datos existe"""
        os.makedirs(cls.DATA_DIR, exist_ok=True)

    @classmethod
    def get_current_month_year(cls):
        """Retorna el mes y año actual"""
        now = datetime.now()
        return now.month, now.year


# Colores para categorías
CATEGORY_COLORS = {
    "Alimentos": "#FF5722",  # Deep Orange
    "Transporte": "#3F51B5",  # Indigo
    "Entretenimiento": "#9C27B0",  # Purple
    "Salud": "#E91E63",  # Pink
    "Educación": "#4CAF50",  # Green
    "Hogar": "#FFC107",  # Amber
    "Otros": "#607D8B",  # Blue Grey
}

# iconos para categorías
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
    return CATEGORY_COLORS.get(category_name, "#9E9E9E")  # Grey por defecto


def get_category_icon(category_name):
    """Retorna el icono asociado a una categoría"""
    return CATEGORY_ICONS.get(category_name, "category")  # Icono por defecto


def format_currency(amount):
    """Formatea un monto con el símbolo de la moneda"""
    return f"{Config.CURRENCY_SYMBOL}{amount:,.2f}"


def parse_currency(formatted_amount):
    """Parsea un monto formateado y retorna su valor numérico"""
    try:
        # Eliminar el símbolo de la moneda y comas
        cleaned_amount = formatted_amount.replace(Config.CURRENCY_SYMBOL, "").replace(
            ",", ""
        )
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


def validate_description(description):
    """Valida la longitud de la descripción"""
    if len(description) > Config.MAX_DESCRIPTION_LENGTH:
        raise ValueError(
            f"La descripción no puede exceder {Config.MAX_DESCRIPTION_LENGTH} caracteres"
        )
    return True


def validate_notes(notes):
    """Valida la longitud de las notas"""
    if len(notes) > Config.MAX_NOTES_LENGTH:
        raise ValueError(
            f"Las notas no pueden exceder {Config.MAX_NOTES_LENGTH} caracteres"
        )
    return True


def validate_file_size(file_path):
    """Valida que el tamaño del archivo no exceda el límite permitido"""
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > Config.MAX_FILE_SIZE_MB:
        raise ValueError(
            f"El tamaño del archivo no puede exceder {Config.MAX_FILE_SIZE_MB} MB"
        )
    return True


def validate_import_limit(num_transactions):
    """Valida que el número de transacciones a importar no exceda el límite permitido"""
    if num_transactions > Config.MAX_TRANSACTIONS_IMPORT:
        raise ValueError(
            f"No se pueden importar más de {Config.MAX_TRANSACTIONS_IMPORT} transacciones a la vez"
        )
    return True


def get_month_year_format(date):
    """Retorna el mes y año de una fecha en formato 'Mes Año'"""
    return date.strftime(Config.MONTH_YEAR_FORMAT)


def get_date_format(date):
    """Retorna la fecha en formato 'dd/mm/yyyy'"""
    return date.strftime(Config.DATE_FORMAT)


def get_datetime_format(date):
    """Retorna la fecha y hora en formato 'dd/mm/yyyy HH:MM'"""
    return date.strftime(Config.DATETIME_FORMAT)


def get_default_history_months():
    """Retorna el número de meses por defecto para el historial"""
    return Config.DEFAULT_HISTORY_MONTHS


def get_currency_symbol():
    """Retorna el símbolo de la moneda"""
    return Config.CURRENCY_SYMBOL


def get_currency_name():
    """Retorna el nombre de la moneda"""
    return Config.CURRENCY_NAME


def get_category_colors():
    """Retorna el diccionario de colores de categorías"""
    return CATEGORY_COLORS


def get_category_icons():
    """Retorna el diccionario de iconos de categorías"""
    return CATEGORY_ICONS


def get_config():
    """Retorna la configuración completa de la aplicación"""
    return Config
