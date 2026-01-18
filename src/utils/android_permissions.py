"""
Helper para permisos en Android - VERSIÓN SIN JNIUS
Archivo: src/utils/android_permissions.py

✅ Sin jnius - Evita crashes en Android
✅ Los permisos se manejan automáticamente por Flet
"""

import sys
import os


def request_permissions():
    """
    Placeholder para solicitar permisos
    
    NOTA: En Flet para Android, los permisos declarados en
    AndroidManifest.xml se solicitan automáticamente cuando
    la app intenta acceder a recursos protegidos.
    
    Returns:
        bool: True siempre (no hay nada que hacer)
    """
    if sys.platform != "android" and not hasattr(sys, 'getandroidapilevel'):
        print("ℹ️ No es Android, permisos no necesarios")
        return True
    
    print("📱 Android detectado")
    print("✅ Los permisos se solicitan automáticamente por Flet")
    print("ℹ️ Si necesitas permisos adicionales, actualiza AndroidManifest.xml")
    return True


def request_storage_permissions():
    """Alias de request_permissions()"""
    return request_permissions()


def get_app_storage_path():
    """
    Obtiene la ruta de almacenamiento interno de la app
    
    Returns:
        str: Ruta del directorio de almacenamiento
    """
    if sys.platform != "android" and not hasattr(sys, 'getandroidapilevel'):
        import tempfile
        return tempfile.gettempdir()
    
    # En Android, usar variables de entorno
    try:
        if 'ANDROID_PRIVATE' in os.environ:
            path = os.environ['ANDROID_PRIVATE']
            print(f"📁 Almacenamiento de app: {path}")
            return path
        elif 'ANDROID_APP_PATH' in os.environ:
            path = os.environ['ANDROID_APP_PATH']
            print(f"📁 Almacenamiento de app: {path}")
            return path
    except:
        pass
    
    # Fallback
    fallback = "/data/data/com.termowallet.app/files"
    print(f"📁 Almacenamiento de app (fallback): {fallback}")
    return fallback


print("✅ android_permissions cargado correctamente")