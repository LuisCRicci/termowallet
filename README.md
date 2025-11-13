# 💰 TermoWallet

**Aplicación móvil Android para control financiero personal**

## 📋 Descripción

Sistema completo de gestión de finanzas personales que permite:
- ✅ Registrar gastos e ingresos manualmente
- ✅ Importar transacciones desde CSV/Excel
- ✅ Categorizar automáticamente los movimientos
- ✅ Visualizar estadísticas y gráficos interactivos
- ✅ Calcular ahorros mensuales
- ✅ Gestionar categorías personalizadas

---

## 🛠️ Tecnologías Utilizadas

| Componente | Tecnología | Versión |
|------------|------------|---------|
| **Framework UI** | Flet | 0.28.3 |
| **Base de Datos** | SQLAlchemy | 2.0.44 |
| **Base de Datos** | SQLite3 | 3.50.4 |
| **Procesamiento** | Pandas | 2.3.3 |
| **Visualización** | Plotly | 6.3.1 |
| **Lenguaje** | Python | 3.10+ |
| **Base de Datos** | openpyxl| 3.1.5 |

---

## 🚀 Instalación

### Requisitos Previos
- Python 3.10 o superior
- pip (gestor de paquetes)
- Git (opcional)

### Pasos de Instalación

```bash
# 1. Clonar repositorio
git clone https://github.com/LuisCRicci/termowallet.git

# 2. Ejemplos para crear entorno virtual
python3.10 -m venv env310
python3.11 -m venv mi_entorno


# 3. Activar entorno virtual
# Windows:
.\mi_entorno\Scripts\activate
# Mac/Linux:
source mi_entorno/bin/activate

Una vez activado, verás el nombre del entorno en tu terminal.

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar aplicación
flet run src/main.py
```

---

## 📱 Ejecución en Android

### Opción 1: Emulador (Desarrollo)

```bash
# Abrir emulador de Android Studio primero
flet run --android src/main.py
```

### Opción 2: Dispositivo Real

```bash
# 1. Generar APK
flet build apk src/main.py

# 2. Ubicación del APK
# build/apk/termowallet.apk

# 3. Transferir al dispositivo e instalar
# Habilitar "Instalar apps desconocidas" en Ajustes
```

---

## 📂 Estructura del Proyecto

```
── README.md                    # Documentación del proyecto
├── requirements.txt             # Dependencias Python
├── .gitignore                   # Archivos a ignorar en Git
├── .env.example                 # Variables de entorno ejemplo
├── data/                        # Base de datos SQLite
│   └── expenses.db              # (se crea automáticamente)
├── docs/                        # Documentación adicional
├── tests/                       # Tests unitarios
│   └── __init__.py
└── src/                         # Código fuente
    ├── __init__.py
    ├── main.py                  # Punto de entrada principal
    ├── models/                  # Modelos de datos (ORM)
    │   ├── __init__.py
    │   ├── database.py          # Configuración SQLAlchemy
    │   ├── transaction.py       # Modelo Transaction
    │   └── category.py          # Modelo Category
    ├── views/                   # Vistas de la UI (Flet)
    │   ├── __init__.py
    │   ├── home_view.py         # Vista principal
    │   ├── transactions_view.py # Gestión de transacciones
    │   ├── dashboard_view.py    # Gráficos y análisis
    │   ├── import_view.py       # Importar CSV/Excel
    │   └── categories_view.py   # Gestión de categorías
    ├── services/                # Lógica de negocio
    │   ├── __init__.py
    │   ├── transaction_service.py
    │   └── category_service.py
    └── utils/                   # Utilidades
        ├── __init__.py
        ├── csv_processor.py     # Procesamiento CSV/Excel
        └── categorizer.py       # Auto-categorización

```

---

## 🎯 Funcionalidades Principales

### 1. Gestión de Transacciones

**Ingreso Manual:**
- Formulario intuitivo para gastos e ingresos
- Campos: monto, descripción, categoría, fecha, notas
- Validación de datos en tiempo real

**Importación de Archivos:**
- Soporta CSV y Excel (.xlsx, .xls)
- Detección automática de columnas (fecha, descripción, monto)
- Limpieza y validación de datos
- Categorización automática basada en palabras clave

### 2. Categorización Inteligente

**Categorías Predeterminadas:**

**Gastos:**
- 🍔 Alimentación
- 🚗 Transporte
- 🎮 Entretenimiento
- 💡 Servicios
- ⚕️ Salud
- 📚 Educación
- 🏠 Vivienda
- 🛍️ Compras
- 📦 Otros Gastos

**Ingresos:**
- 💵 Salario
- 💼 Freelance
- 📈 Inversiones
- 🏪 Ventas
- 🎁 Bonos
- 💰 Otros Ingresos

**Categorías Personalizadas:**
- Crear nuevas categorías
- Asignar colores e iconos personalizados
- Diferenciar entre gastos e ingresos

### 3. Visualizaciones y Reportes

**Dashboard Mensual:**
- Tarjetas de resumen (Ingresos, Gastos, Ahorros)
- Tasa de ahorro con indicador visual
- Transacciones recientes

**Gráficos:**
- Distribución de gastos por categoría (barras)
- Distribución de ingresos por categoría (barras)
- Tendencia mensual de los últimos 6 meses

**Historial Completo:**
- Lista cronológica (más reciente primero)
- Agrupación por día
- Filtros por mes
- Opciones de edición y eliminación

### 4. Cálculo de Ahorros

```
Ahorro = Total Ingresos - Total Gastos
Tasa de Ahorro = (Ahorro / Ingresos) × 100%
```

- Resumen mensual automático
- Indicador visual de cumplimiento de metas
- Historial de 6 meses para análisis de tendencias

---

## 📊 Uso de la Aplicación

### Pantalla Principal (Home)

1. **Visualizar resumen del mes actual:**
   - Ingresos totales
   - Gastos totales
   - Ahorro generado
   - Tasa de ahorro

2. **Navegar entre meses:**
   - Usar flechas ← → para ver meses anteriores/siguientes

3. **Ver transacciones recientes:**
   - Últimas 5 transacciones del mes

### Añadir Transacción

1. **Seleccionar tipo:** Gasto o Ingreso
2. **Completar formulario:**
   - Monto (obligatorio)
   - Descripción (obligatorio)
   - Categoría (seleccionar de lista)
   - Fecha (selector de calendario)
   - Notas (opcional)
3. **Guardar:** Toca el botón "Guardar Transacción"

### Importar desde Archivo

1. **Preparar archivo CSV o Excel:**
   ```csv
   fecha,descripcion,monto
   30-10-2025,sueldo-neto,2500.00
   28-10-2025,Supermercado,150.50
   27-10-2025,Taxi,12.00
   ```

2. **En la app:**
   - Ir a "Añadir"
   - Tocar "Importar desde archivo"
   - Seleccionar archivo
   - Confirmar importación

3. **Revisión automática:**
   - Validación de formato
   - Limpieza de datos
   - Categorización inteligente
   - Confirmación de cantidad importada

### Ver Historial

1. **Navegar a "Historial"**
2. **Revisar transacciones por día**
3. **Cambiar de mes** con flechas
4. **Eliminar transacción:**
   - Tocar icono de papelera
   - Confirmar eliminación

### Analizar Gráficos

1. **Navegar a "Gráficos"**
2. **Interpretar visualizaciones:**
   - Barras por categoría: identifica dónde gastas más
   - Tendencia mensual: observa patrones de gasto
   - Comparación ingresos vs gastos

### Gestionar Categorías

1. **Navegar a "Categorías"**
2. **Crear nueva categoría:**
   - Tocar botón "+"
   - Ingresar nombre y descripción
   - Seleccionar tipo (Gasto/Ingreso)
   - Elegir emoji y color
   - Guardar

3. **Eliminar categoría:**
   - Solo categorías sin transacciones
   - Categorías predeterminadas no se pueden eliminar
   - Datos involucrados se recategorizan

---

## 🎨 Personalización

### Colores de Categorías

Las categorías usan códigos hexadecimales:
```python
'#e9f413ff'  # Amarillo
'#f59e0b'  # Mostaza
'#f5360bff'  # Naranja
'#ef4444'  # Rojo
'#8ceb7eff'  # Verde
'#3b82f6'  # Azul
'#d36fe8ff'  # rosado
'#8b5cf6'  # Morado
```

### Iconos Emoji

Usa cualquier emoji Unicode:
```
💰 🍔 🚗 🎮 💡 ⚕️ 📚 🏠 🛍️ 📦 
💵 💼 📈 🏪 🎁 ⚙️ 🚨 👤 🧪 💬
👨‍🍳 🤷‍♀️ 🛒 📋 🧽 🤖 ❄️ 👷‍♂️ ☕️ 💅 
🌲 🍪 🗺 🎞 🧑‍💻 🛬 🐞 ❤️ 💳 🎓

```

---

## 🧪 Testing

### Tests Unitarios

```bash
# Ejecutar todos los tests
python -m unittest discover tests/

# Test específico
python -m tests.test_database

# Ejemplo test de labase de datos
python -m tests.debug_db

```

### Generar Datos de Prueba

```bash
python scripts/generate_test_data.py
```

---

## 📈 Roadmap

### Versión 1.0 (Actual)
- [ ] CRUD de transacciones
- [ ] Importación CSV/Excel
- [ ] Categorización automática
- [ ] Visualizaciones básicas
- [ ] Gestión de categorías
- [ ] APK Android

### Versión 1.1 (Próxima)
- [ ] Autenticación de usuarios
- [ ] Backup en la nube
- [ ] Exportar reportes PDF
- [ ] Modo oscuro/claro
- [ ] Múltiples monedas

### Versión 2.0 (Futuro)
- [ ] Presupuestos mensuales
- [ ] Alertas y notificaciones
- [ ] Gastos recurrentes
- [ ] Predicciones con ML
- [ ] Sincronización multi-dispositivo

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Añade nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto es parte de un trabajo académico de Ciencia de Datos e Inteligencia Artificial con licencia MIT.

---

## 👥 Equipo de Desarrollo

- **Desarrollo:** LuisCRicci 
- **Gestión de Proyecto:** Karen
- **Testing:**  jancoyk

---

## 📞 Soporte

¿Problemas o preguntas?
- 📧 Email: soporte@termowallet.com
- 📱 Issues: [GitHub Issues](https://github.com/LuisCRicci/termowallet/issues)

---

## 🙏 Agradecimientos

- **Flet Framework** por la facilidad de desarrollo móvil
- **SQLAlchemy** por el ORM robusto
- **Pandas** por el procesamiento de datos
- Comunidad de Python por las excelentes librerías

---

**Desarrollado con ❤️  con la contribucion de:**

1. Luis Alberto Cusy Ricci 
2. Jancarlos Froilan Linares Sagastizabal
3. Luz Marina Vega Calderón
4. Karen Paola Barrientos Quintanilla
5. 
6. 