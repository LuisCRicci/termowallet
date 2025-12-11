"""
Helper MEJORADO para permisos en Android - VERSIÓN SIMPLIFICADA
Archivo: src/utils/android_permissions.py
"""

import sys
import os

def get_app_storage_path():
    """
    Obtiene la ruta de almacenamiento de la app en Android
    Versión simplificada y robusta
    """
    if sys.platform != "android":
        import tempfile
        return tempfile.gettempdir()
    
    try:
        # Método principal: directorio de archivos de la app
        from android.storage import app_storage_path
        path = app_storage_path()
        print(f"📁 Ruta de app Android: {path}")
        
        # Verificar que podemos escribir
        os.makedirs(path, exist_ok=True)
        return path
        
    except Exception as e:
        print(f"❌ Error obteniendo ruta Android: {e}")
        
        # Fallbacks en orden de preferencia
        fallbacks = [
            "/data/data/com.termowallet.app/files",
            "/storage/emulated/0/Android/data/com.termowallet.app/files",
            "/storage/emulated/0/Download"
        ]
        
        for fallback in fallbacks:
            try:
                os.makedirs(fallback, exist_ok=True)
                print(f"📁 Usando fallback: {fallback}")
                return fallback
            except:
                continue
        
        # Último recurso
        final_fallback = "/data/data/com.termowallet.app/files"
        os.makedirs(final_fallback, exist_ok=True)
        return final_fallback

def share_file_android(filepath: str, mime_type: str = "application/octet-stream"):
    """
    Comparte archivo en Android - Versión simplificada
    """
    if sys.platform != "android":
        print("ℹ️ No es Android, compartir no disponible")
        return False
    
    try:
        from jnius import autoclass, cast
        
        print(f"📤 Compartiendo: {filepath}")
        
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        Uri = autoclass('android.net.Uri')
        File = autoclass('java.io.File')
        
        current_activity = cast('android.app.Activity', PythonActivity.mActivity)
        
        # Crear intent de compartir
        intent = Intent(Intent.ACTION_SEND)
        intent.setType(mime_type)
        
        # Obtener URI del archivo
        file = File(filepath)
        uri = Uri.fromFile(file)
        
        intent.putExtra(Intent.EXTRA_STREAM, uri)
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        
        # Lanzar selector de compartir
        chooser = Intent.createChooser(intent, "Compartir reporte")
        current_activity.startActivity(chooser)
        
        print("✅ Archivo compartido")
        return True
        
    except Exception as e:
        print(f"❌ Error al compartir: {e}")
        return False