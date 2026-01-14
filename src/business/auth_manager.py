"""
Gestor de Autenticación con Encriptación AES-256
Archivo: src/business/auth_manager.py

Sistema de login seguro con:
- Encriptación AES-256 para contraseñas
- Contador de intentos fallidos
- Reseteo automático de BD al 7º intento fallido
"""

import os
import hashlib
from typing import Optional, Tuple
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64
from sqlalchemy import text  # ✅ NUEVO: Importar text para SQLAlchemy 2.0


class AuthManager:
    """Maneja la autenticación y encriptación de contraseñas"""
    
    # Clave maestra derivada del dispositivo (32 bytes para AES-256)
    # En producción, esto debería derivarse de un secret único del dispositivo
    MASTER_KEY = hashlib.sha256(b"TermoWallet_Master_Secret_Key_2024").digest()
    
    def __init__(self, db_manager):
        self.db = db_manager
        self._ensure_auth_table()
    
    def _ensure_auth_table(self):
        """Crea la tabla de autenticación si no existe"""
        try:
            cursor = self.db.session.execute(
                text("""
                CREATE TABLE IF NOT EXISTS auth_config (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    password_hash TEXT NOT NULL,
                    iv TEXT NOT NULL,
                    failed_attempts INTEGER DEFAULT 0,
                    is_locked BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
            )
            self.db.session.commit()
            print("✅ Tabla de autenticación inicializada")
        except Exception as e:
            print(f"⚠️ Tabla auth_config ya existe o error: {e}")
    
    def _encrypt_password(self, password: str) -> Tuple[str, str]:
        """
        Encripta una contraseña usando AES-256-CBC
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            Tupla (encrypted_base64, iv_base64)
        """
        # Generar IV aleatorio (16 bytes para AES)
        iv = os.urandom(16)
        
        # Crear cipher con AES-256-CBC
        cipher = Cipher(
            algorithms.AES(self.MASTER_KEY),
            modes.CBC(iv),
            backend=default_backend()
        )
        
        # Padding PKCS7
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(password.encode('utf-8')) + padder.finalize()
        
        # Encriptar
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        
        # Convertir a base64 para almacenamiento
        encrypted_b64 = base64.b64encode(encrypted).decode('utf-8')
        iv_b64 = base64.b64encode(iv).decode('utf-8')
        
        return encrypted_b64, iv_b64
    
    def _decrypt_password(self, encrypted_b64: str, iv_b64: str) -> str:
        """
        Desencripta una contraseña
        
        Args:
            encrypted_b64: Contraseña encriptada en base64
            iv_b64: IV en base64
            
        Returns:
            Contraseña en texto plano
        """
        # Decodificar base64
        encrypted = base64.b64decode(encrypted_b64)
        iv = base64.b64decode(iv_b64)
        
        # Crear cipher
        cipher = Cipher(
            algorithms.AES(self.MASTER_KEY),
            modes.CBC(iv),
            backend=default_backend()
        )
        
        # Desencriptar
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted) + decryptor.finalize()
        
        # Remover padding
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        return data.decode('utf-8')
    
    def is_password_set(self) -> bool:
        """Verifica si ya existe una contraseña configurada"""
        try:
            result = self.db.session.execute(
                text("SELECT COUNT(*) FROM auth_config WHERE id = 1")
            ).fetchone()
            return result[0] > 0 if result else False
        except Exception as e:
            print(f"❌ Error verificando contraseña: {e}")
            return False
    
    def set_password(self, password: str) -> bool:
        """
        Configura la contraseña inicial
        
        Args:
            password: Contraseña a establecer
            
        Returns:
            bool: True si se configuró correctamente
        """
        if len(password) < 4:
            print("❌ Contraseña muy corta (mínimo 4 caracteres)")
            return False
        
        try:
            # Encriptar contraseña
            encrypted, iv = self._encrypt_password(password)
            
            # Guardar en BD
            if self.is_password_set():
                # Actualizar
                self.db.session.execute(
                    text("""
                    UPDATE auth_config 
                    SET password_hash = :hash, iv = :iv, 
                        failed_attempts = 0, is_locked = 0,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = 1
                    """),
                    {"hash": encrypted, "iv": iv}
                )
            else:
                # Insertar
                self.db.session.execute(
                    text("""
                    INSERT INTO auth_config (id, password_hash, iv, failed_attempts, is_locked)
                    VALUES (1, :hash, :iv, 0, 0)
                    """),
                    {"hash": encrypted, "iv": iv}
                )
            
            self.db.session.commit()
            print("✅ Contraseña configurada correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error configurando contraseña: {e}")
            self.db.session.rollback()
            return False
    
    def verify_password(self, password: str) -> Tuple[bool, str, int]:
        """
        Verifica la contraseña ingresada
        
        Args:
            password: Contraseña a verificar
            
        Returns:
            Tupla (success, message, failed_attempts)
        """
        try:
            # Obtener configuración
            result = self.db.session.execute(
                text("SELECT password_hash, iv, failed_attempts, is_locked FROM auth_config WHERE id = 1")
            ).fetchone()
            
            if not result:
                return False, "No hay contraseña configurada", 0
            
            encrypted, iv, failed_attempts, is_locked = result
            
            # Verificar si está bloqueado
            if is_locked:
                return False, "⛔ Sistema bloqueado. Contacte al administrador.", failed_attempts
            
            # Desencriptar y comparar
            try:
                stored_password = self._decrypt_password(encrypted, iv)
                
                if password == stored_password:
                    # ✅ Contraseña correcta - resetear intentos
                    self.db.session.execute(
                        text("UPDATE auth_config SET failed_attempts = 0, updated_at = CURRENT_TIMESTAMP WHERE id = 1")
                    )
                    self.db.session.commit()
                    return True, "✅ Acceso concedido", 0
                else:
                    # ❌ Contraseña incorrecta
                    return self._handle_failed_attempt(failed_attempts)
                    
            except Exception as decrypt_error:
                print(f"❌ Error desencriptando: {decrypt_error}")
                return False, "Error de autenticación", failed_attempts
                
        except Exception as e:
            print(f"❌ Error verificando contraseña: {e}")
            return False, f"Error: {str(e)}", 0
    
    def _handle_failed_attempt(self, current_attempts: int) -> Tuple[bool, str, int]:
        """
        Maneja un intento fallido de login
        
        Args:
            current_attempts: Intentos fallidos actuales
            
        Returns:
            Tupla (success=False, message, new_attempts)
        """
        new_attempts = current_attempts + 1
        
        try:
            if new_attempts >= 7:
                # 🔥 7º intento fallido - RESETEAR BASE DE DATOS
                self._reset_database()
                return False, (
                    "🔥 LÍMITE DE INTENTOS EXCEDIDO\n\n"
                    "La base de datos ha sido reseteada.\n"
                    "Todos los datos han sido eliminados.\n\n"
                    "Configure una nueva contraseña para continuar."
                ), 0
            
            elif new_attempts == 6:
                # ⚠️ 6º intento - ADVERTENCIA CRÍTICA
                self.db.session.execute(
                    text("UPDATE auth_config SET failed_attempts = :attempts, updated_at = CURRENT_TIMESTAMP WHERE id = 1"),
                    {"attempts": new_attempts}
                )
                self.db.session.commit()
                
                return False, (
                    "⚠️ ADVERTENCIA CRÍTICA\n\n"
                    "Este es su 6º intento fallido.\n\n"
                    "❗ AL PRÓXIMO INTENTO FALLIDO:\n"
                    "• La base de datos será RESETEADA\n"
                    "• TODOS los datos serán ELIMINADOS\n"
                    "• NO habrá forma de recuperarlos\n\n"
                    "Por favor, recuerde su contraseña correctamente."
                ), new_attempts
            
            else:
                # Intentos 1-5
                self.db.session.execute(
                    text("UPDATE auth_config SET failed_attempts = :attempts, updated_at = CURRENT_TIMESTAMP WHERE id = 1"),
                    {"attempts": new_attempts}
                )
                self.db.session.commit()
                
                remaining = 7 - new_attempts
                return False, (
                    f"❌ Contraseña incorrecta\n\n"
                    f"Intentos fallidos: {new_attempts}/7\n"
                    f"Intentos restantes: {remaining}\n\n"
                    f"⚠️ Al 7º intento fallido se reseteará la base de datos."
                ), new_attempts
                
        except Exception as e:
            print(f"❌ Error manejando intento fallido: {e}")
            return False, "Error del sistema", new_attempts
    
    def _reset_database(self):
        """
        🔥 RESETEA COMPLETAMENTE LA BASE DE DATOS
        Elimina todos los datos y resetea la configuración
        """
        print("\n" + "="*60)
        print("🔥 RESETEANDO BASE DE DATOS - LÍMITE DE INTENTOS EXCEDIDO")
        print("="*60)
        
        try:
            # Eliminar todas las transacciones
            self.db.session.execute(text("DELETE FROM transactions"))
            
            # Eliminar presupuestos
            self.db.session.execute(text("DELETE FROM monthly_budgets"))
            
            # Eliminar presupuestos por categoría
            try:
                self.db.session.execute(text("DELETE FROM category_budgets"))
            except:
                pass
            
            # Eliminar categorías personalizadas (mantener predeterminadas)
            self.db.session.execute(text("DELETE FROM categories WHERE is_default = 0"))
            
            # Resetear auth_config
            self.db.session.execute(text("DELETE FROM auth_config WHERE id = 1"))
            
            self.db.session.commit()
            
            print("✅ Base de datos reseteada completamente")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"❌ Error reseteando base de datos: {e}")
            self.db.session.rollback()
    
    def get_failed_attempts(self) -> int:
        """Obtiene el número actual de intentos fallidos"""
        try:
            result = self.db.session.execute(
                text("SELECT failed_attempts FROM auth_config WHERE id = 1")
            ).fetchone()
            return result[0] if result else 0
        except:
            return 0
    
    def change_password(self, old_password: str, new_password: str) -> Tuple[bool, str]:
        """
        Cambia la contraseña (requiere verificar la contraseña actual)
        
        Args:
            old_password: Contraseña actual
            new_password: Nueva contraseña
            
        Returns:
            Tupla (success, message)
        """
        # Verificar contraseña actual
        success, message, _ = self.verify_password(old_password)
        
        if not success:
            return False, "Contraseña actual incorrecta"
        
        if len(new_password) < 4:
            return False, "Nueva contraseña muy corta (mínimo 4 caracteres)"
        
        # Establecer nueva contraseña
        if self.set_password(new_password):
            return True, "✅ Contraseña cambiada correctamente"
        else:
            return False, "Error al cambiar contraseña"
    
    def reset_failed_attempts(self):
        """Resetea el contador de intentos fallidos (uso administrativo)"""
        try:
            self.db.session.execute(
                text("UPDATE auth_config SET failed_attempts = 0, is_locked = 0, updated_at = CURRENT_TIMESTAMP WHERE id = 1")
            )
            self.db.session.commit()
            print("✅ Intentos fallidos reseteados")
        except Exception as e:
            print(f"❌ Error reseteando intentos: {e}")