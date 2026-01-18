"""
Gestor de Autenticación con Hashing Seguro PBKDF2
Archivo: src/business/auth_manager.py

✅ COMPLETAMENTE REESCRITO - Sin dependencia de cryptography
Sistema de login seguro con:
- Hashing PBKDF2-HMAC-SHA256 (100,000 iteraciones)
- Contador de intentos fallidos
- Reseteo automático de BD al 7º intento fallido
"""

import os
import hashlib
import binascii
from typing import Optional, Tuple
from sqlalchemy import text


class AuthManager:
    """Maneja la autenticación usando Hashing Seguro (PBKDF2)"""
    
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
    
    def _hash_password(self, password: str, salt: bytes = None) -> str:
        """
        Hashea una contraseña usando PBKDF2-HMAC-SHA256
        
        Args:
            password: Contraseña en texto plano
            salt: Salt opcional (se genera si no se provee)
        
        Returns:
            str: "salt_hex$hash_hex"
        """
        if salt is None:
            salt = os.urandom(16)  # 16 bytes de salt aleatorio
        
        # 100,000 iteraciones de PBKDF2 con SHA256
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )
        
        # Convertir a hexadecimal
        salt_hex = binascii.hexlify(salt).decode('ascii')
        hash_hex = binascii.hexlify(pwd_hash).decode('ascii')
        
        return f"{salt_hex}${hash_hex}"
    
    def _verify_hash(self, password: str, stored_hash: str) -> bool:
        """
        Verifica una contraseña contra un hash almacenado
        
        Args:
            password: Contraseña ingresada
            stored_hash: Hash almacenado ("salt$hash")
        
        Returns:
            bool: True si la contraseña es correcta
        """
        try:
            # Separar salt y hash
            if "$" not in stored_hash:
                print("❌ Formato de hash inválido")
                return False
            
            salt_hex, hash_hex = stored_hash.split("$", 1)
            
            # Convertir salt de hex a bytes
            salt = binascii.unhexlify(salt_hex)
            
            # Calcular hash de la contraseña ingresada
            new_hash = self._hash_password(password, salt)
            
            # Comparar de forma segura
            return new_hash == stored_hash
            
        except Exception as e:
            print(f"❌ Error verificando hash: {e}")
            return False
    
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
        Configura o actualiza la contraseña
        
        Args:
            password: Contraseña en texto plano (mínimo 4 caracteres)
        
        Returns:
            bool: True si se configuró correctamente
        """
        if len(password) < 4:
            print("❌ Contraseña muy corta (mínimo 4 caracteres)")
            return False
        
        try:
            # Hashear contraseña
            hashed_data = self._hash_password(password)
            
            # Guardar en BD
            if self.is_password_set():
                # Actualizar existente
                self.db.session.execute(
                    text("""
                    UPDATE auth_config 
                    SET password_hash = :hash,
                        failed_attempts = 0,
                        is_locked = 0,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = 1
                    """),
                    {"hash": hashed_data}
                )
            else:
                # Insertar nueva
                self.db.session.execute(
                    text("""
                    INSERT INTO auth_config (id, password_hash, failed_attempts, is_locked)
                    VALUES (1, :hash, 0, 0)
                    """),
                    {"hash": hashed_data}
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
            Tuple[bool, str, int]: (éxito, mensaje, intentos_fallidos)
        """
        try:
            # Obtener configuración
            result = self.db.session.execute(
                text("SELECT password_hash, failed_attempts, is_locked FROM auth_config WHERE id = 1")
            ).fetchone()
            
            if not result:
                return False, "❌ No hay contraseña configurada", 0
            
            stored_hash, failed_attempts, is_locked = result
            
            # Verificar si está bloqueado
            if is_locked:
                return False, "🔒 Sistema bloqueado. Contacte al administrador.", failed_attempts
            
            # Verificar contraseña
            if self._verify_hash(password, stored_hash):
                # ✅ Contraseña correcta - resetear intentos
                self.db.session.execute(
                    text("UPDATE auth_config SET failed_attempts = 0, updated_at = CURRENT_TIMESTAMP WHERE id = 1")
                )
                self.db.session.commit()
                return True, "✅ Acceso concedido", 0
            else:
                # ❌ Contraseña incorrecta
                return self._handle_failed_attempt(failed_attempts)
        
        except Exception as e:
            print(f"❌ Error verificando contraseña: {e}")
            import traceback
            traceback.print_exc()
            return False, f"❌ Error: {str(e)}", 0
    
    def _handle_failed_attempt(self, current_attempts: int) -> Tuple[bool, str, int]:
        """
        Maneja un intento fallido de login
        
        Args:
            current_attempts: Intentos fallidos actuales
        
        Returns:
            Tuple[bool, str, int]: (False, mensaje, nuevos_intentos)
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
            return False, "❌ Error del sistema", new_attempts
    
    def _reset_database(self):
        """
        🔥 RESETEA COMPLETAMENTE LA BASE DE DATOS
        Elimina todos los datos y resetea la configuración
        """
        print("\n" + "="*60)
        print("🔥 RESETEANDO BASE DE DATOS - LÍMITE DE INTENTOS EXCEDIDO")
        print("="*60)
        
        try:
            # Eliminar transacciones
            self.db.session.execute(text("DELETE FROM transactions"))
            
            # Eliminar presupuestos
            self.db.session.execute(text("DELETE FROM monthly_budgets"))
            
            # Eliminar presupuestos por categoría
            try:
                self.db.session.execute(text("DELETE FROM category_budgets"))
            except:
                pass
            
            # Eliminar categorías personalizadas
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
            Tuple[bool, str]: (éxito, mensaje)
        """
        # Verificar contraseña actual
        success, message, _ = self.verify_password(old_password)
        
        if not success:
            return False, "❌ Contraseña actual incorrecta"
        
        if len(new_password) < 4:
            return False, "❌ Nueva contraseña muy corta (mínimo 4 caracteres)"
        
        # Establecer nueva contraseña
        if self.set_password(new_password):
            return True, "✅ Contraseña cambiada correctamente"
        else:
            return False, "❌ Error al cambiar contraseña"
    
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