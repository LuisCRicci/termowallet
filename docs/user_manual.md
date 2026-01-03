# 🔑 Sistema de Palabras Clave Personalizado - TermoWallet

## 📋 Resumen de Funcionalidades Implementadas

### 1. ✅ Inicialización Automática
**Cuándo**: Primera vez que inicia la app o al crear la BD

**Archivos modificados**:
- `src/data/database.py` → método `__init__()`

**Qué hace**:
```python
DatabaseManager.__init__()
  ├─ _initialize_default_categories()  # Crea categorías
  └─ _initialize_default_keywords()    # Asigna keywords automáticamente ✅
```

**Resultado**: Todas las categorías predeterminadas tienen sus keywords cargadas automáticamente.

---

### 2. ✅ Gestión Individual de Keywords por Categoría

**Dónde**: Vista de Categorías → Botón 🏷️ en cada categoría

**Archivos modificados**:
- `src/ui/categories_view.py` → `show_keywords_dialog()`

**Funcionalidades**:
- ➕ **Agregar** palabras clave personalizadas
- ➖ **Eliminar** palabras clave existentes
- 👀 **Visualizar** todas las keywords con chips
- 🔄 **Restaurar defaults** (solo categorías predeterminadas)

**Flujo de uso**:
```
1. Usuario va a "Categorías"
2. Hace clic en 🏷️ de cualquier categoría
3. Ve diálogo con keywords actuales
4. Puede:
   - Escribir nueva keyword + Enter
   - Eliminar cualquier chip (X)
   - Restaurar defaults (si es categoría predeterminada)
```

---

### 3. ✅ Restauración Masiva de Keywords

**Dónde**: Settings → "Restaurar Palabras Clave"

**Archivos modificados**:
- `src/data/database.py` → `restore_default_keywords()`
- `src/ui/settings_view.py` → `confirm_restore_keywords()` + `restore_keywords()`

**Qué hace**:
- Restaura las keywords predeterminadas de **TODAS** las categorías default
- NO afecta transacciones ni categorías personalizadas
- Sobrescribe keywords personalizadas con las originales

**Cuándo usarlo**:
- Has modificado muchas keywords y quieres volver al estado original
- Después de experimentar, quieres resetear solo las keywords
- Para corregir keywords que no funcionan bien

---

### 4. ✅ Reset Completo con Reinicialización

**Dónde**: Settings → "Resetear Base de Datos"

**Archivos modificados**:
- `src/data/database.py` → `reset_database()`

**Qué hace**:
```python
reset_database()
  ├─ Elimina todas las transacciones
  ├─ Elimina categorías personalizadas
  ├─ Elimina presupuestos
  ├─ Limpia keywords de categorías default
  └─ _initialize_default_keywords()  # Re-inicializa keywords ✅
```

---

## 🎯 Casos de Uso

### Caso 1: Usuario Nuevo
```
1. Instala la app
2. Se ejecuta __init__()
3. ✅ Categorías + Keywords cargadas automáticamente
4. Listo para importar transacciones
```

### Caso 2: Personalizar Keywords
```
1. Usuario va a "Categorías"
2. Clic en 🏷️ en "Alimentación"
3. Agrega: "mcdonalds", "burguer king", "kfc"
4. ✅ Ahora esas palabras categorizan automáticamente
```

### Caso 3: Resetear Una Categoría
```
1. Usuario modificó mucho las keywords de "Transporte"
2. Va a "Categorías" → 🏷️ "Transporte"
3. Clic en "Restaurar defaults"
4. ✅ Keywords vuelven al estado original
```

### Caso 4: Resetear Todas las Keywords
```
1. Usuario experimenta con keywords
2. Quiere volver al estado original
3. Settings → "Restaurar Palabras Clave"
4. ✅ TODAS las categorías default restauradas
5. Categorías personalizadas NO se afectan
```

### Caso 5: Reset Total
```
1. Usuario quiere empezar desde cero
2. Settings → "Resetear Base de Datos"
3. Confirma acción
4. ✅ Todo eliminado + Keywords reinicializadas
```

---

## 🛠️ Archivos Modificados

### 1. `src/data/database.py`
```python
# Métodos modificados:
✅ __init__()                           # Llama a _initialize_default_keywords()
✅ reset_database()                     # Limpia y re-inicializa keywords
✅ _initialize_default_keywords()       # Mejorado con mejor logging

# Métodos nuevos:
✨ restore_default_keywords(category_id=None)  # Restaura keywords
```

### 2. `src/ui/categories_view.py`
```python
# Métodos modificados:
✅ show_keywords_dialog(category)      # Ahora incluye botón "Restaurar defaults"

# Funcionalidad agregada:
✨ Botón "Restaurar defaults" en diálogo
✨ Badge "Default" para categorías predeterminadas
```

### 3. `src/ui/settings_view.py`
```python
# Métodos nuevos:
✨ confirm_restore_keywords(e)         # Diálogo de confirmación
✨ restore_keywords(e)                 # Ejecuta restauración

# Métodos modificados:
✅ reset_database(e)                   # Mejor feedback sobre keywords
✅ build()                             # Incluye botón "Restaurar Keywords"
```

---

## 🧪 Testing Checklist

### ✅ Prueba 1: Inicialización
- [ ] Elimina `termowallet.db`
- [ ] Inicia la app
- [ ] Ve a Categorías → 🏷️ cualquier categoría
- [ ] Verifica que tenga keywords cargadas

### ✅ Prueba 2: Personalización
- [ ] Agrega keyword personalizada
- [ ] Verifica que se guarde
- [ ] Importa CSV con esa keyword
- [ ] Verifica que se categorice correctamente

### ✅ Prueba 3: Restaurar Individual
- [ ] Modifica keywords de "Alimentación"
- [ ] Clic en "Restaurar defaults"
- [ ] Verifica que vuelvan las originales

### ✅ Prueba 4: Restaurar Masiva
- [ ] Modifica keywords de varias categorías
- [ ] Settings → "Restaurar Palabras Clave"
- [ ] Verifica que todas vuelvan al original

### ✅ Prueba 5: Reset Total
- [ ] Settings → "Resetear Base de Datos"
- [ ] Verifica que keywords se reinicialicen
- [ ] Verifica que transacciones se eliminen

---

## 📊 Diferencias entre Acciones

| Acción | Transacciones | Categorías Custom | Keywords Predeterminadas | Presupuestos |
|--------|---------------|-------------------|-------------------------|--------------|
| **Limpiar Transacciones** | ❌ Elimina | ✅ Mantiene | ✅ Mantiene | ✅ Mantiene |
| **Limpiar Categorías Custom** | ✅ Mantiene | ❌ Elimina | ✅ Mantiene | ✅ Mantiene |
| **Restaurar Keywords** | ✅ Mantiene | ✅ Mantiene | 🔄 Restaura | ✅ Mantiene |
| **Reset Total** | ❌ Elimina | ❌ Elimina | 🔄 Restaura | ❌ Elimina |

---

## 🎨 UI/UX Highlights

### Diálogo de Keywords
```
┌───────────────────────────────────────────┐
│ 🏷️ Palabras clave: Alimentación           │
├───────────────────────────────────────────┤
│ 💡 Las palabras clave ayudan a...         │
├───────────────────────────────────────────┤
│ Nueva palabra clave                       │
│ [_____________________________]           │
│ [➕ Agregar]                              │
├───────────────────────────────────────────┤
│ 🔑 Palabras clave actuales (127) [Default]│
│ ┌───────────────────────────────────┐     │
│ │ [pizza ❌] [burger ❌] [cafe ❌]  │     │
│ │ [restaurant ❌] [comida ❌] ...   │     │
│ └───────────────────────────────────┘     │
├───────────────────────────────────────────┤
│ [Cerrar]              [🔄 Restaurar]      │
└───────────────────────────────────────────┘
```

### Settings - Gestión de Datos
```
┌─────────────────────────────────────────┐
│ 🗑️ Gestión de Datos                     │
├─────────────────────────────────────────┤
│ ⚠️ Estas acciones son irreversibles...  │
├─────────────────────────────────────────┤
│ [🗑️ Limpiar Transacciones        →]     │
│ [🏷️ Limpiar Categorías Custom    →]     │
│ [🔄 Restaurar Palabras Clave     →]     │  
│ [♻️ Resetear Base de Datos       →]     │
└─────────────────────────────────────────┘
```

---

## 🚀 Ventajas del Sistema

### 1. **Flexibilidad Total**
- Usuario puede personalizar keywords sin perder las predeterminadas
- Puede restaurar en cualquier momento

### 2. **Seguridad**
- Múltiples niveles de confirmación
- Opciones granulares (individual vs masiva)
- No pierde datos importantes accidentalmente

### 3. **Facilidad de Uso**
- Keywords se cargan automáticamente
- UI intuitiva con chips visuales
- Feedback claro en cada acción

### 4. **Mantenibilidad**
- Código modular y bien documentado
- Funciones reutilizables
- Fácil agregar nuevas keywords predeterminadas

---

## 💡 Próximas Mejoras Potenciales

1. **Exportar/Importar Keywords**
   - Guardar configuración personalizada en archivo
   - Compartir keywords entre usuarios

2. **Sugerencias Inteligentes**
   - Analizar transacciones existentes
   - Sugerir keywords basado en patrones

3. **Keywords por Contexto**
   - Keywords diferentes según región/país
   - Perfiles de usuario (estudiante, familiar, etc.)

4. **Machine Learning**
   - Aprender de categorizaciones manuales
   - Mejorar keywords automáticamente

5. **Estadísticas de Keywords**
   - Mostrar qué keywords se usan más
   - Cuáles tienen mejor tasa de acierto

---

## 📝 Notas Importantes

### Comportamiento de `_initialize_default_keywords()`
- ✅ Solo actualiza categorías **sin keywords** (keywords vacías o None)
- ✅ NO sobrescribe keywords existentes (excepto con `restore_default_keywords()`)
- ✅ Ejecuta automáticamente en `__init__()` y `reset_database()`

### Diferencia entre Métodos
```python
# _initialize_default_keywords()
# → Solo llena keywords VACÍAS
# → NO sobrescribe keywords existentes

# restore_default_keywords()
# → SOBRESCRIBE keywords existentes
# → Requiere confirmación explícita
```

### Seguridad
- Todos los diálogos tienen confirmación
- Mensajes claros sobre qué se va a perder
- Operaciones reversibles cuando es posible

---

## 🎓 Para Desarrolladores

### Agregar Nueva Categoría Predeterminada

1. **En `database.py` → `_initialize_default_categories()`**:
```python
Category(
    name="Nueva Categoría",
    icon="🆕",
    color="#hex",
    category_type="expense",  # o "income"
    is_default=True,
    description="Descripción"
)
```

2. **En `database.py` → `_initialize_default_keywords()`**:
```python
default_expense_keywords = {
    # ...
    "Nueva Categoría": [
        "palabra1", "palabra2", "palabra3"
    ]
}
```

3. **Resetea BD para probar**:
```bash
# Elimina termowallet.db
# O usa Settings → Resetear BD
```

### Debugging
```python
# En database.py los métodos tienen prints:
print("✅ Keywords asignadas a: {category.name}")
print(f"✅ {updated_count} categorías actualizadas...")

# Para ver logs:
# 1. Ejecuta: flet run src/main.py
# 2. Observa la terminal
```

---



## ⚕️ Teting 

```bash
export PYTHONPATH="${PYTHONPATH}:/home/gandalf/Projects/mobile/termowallet"
```
**Nota** : cambiar la ruta por la ruta configurada en tu equipo
```bash
python tests/run_test.py
```

si todo a salio bien veras el resumen del testing de la siguiente forma: 

```bash

=========================================================
                       RESUMEN FINAL                        
=========================================================

Dependencias             : ✓ PASS
Estructura               : ✓ PASS
Base de Datos            : ✓ PASS
Sistema Keywords         : ✓ PASS
Tests Unitarios          : ✓ PASS
Diagnóstico              : ✓ PASS
Android Compatibility    : ✓ PASS

🎉 ¡Todos los tests pasaron!
La aplicación está lista para ejecutarse y compilar.
```

## 🏁 Conclusión

El sistema de keywords personalizado está completamente funcional con:

✅ **Inicialización automática**
✅ **Gestión individual por categoría**
✅ **Restauración granular (individual o masiva)**
✅ **Reset total con reinicialización**
✅ **UI intuitiva y segura**
✅ **Código documentado y mantenible**

¡Todo listo para usar! 🎉


