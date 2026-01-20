# 💰 TermoWallet

**Aplicación móvil Android para control financiero personal**

## 📋 Descripción

el sistema es un MVP de gestión de finanzas personales que permite:
- ✅ Registrar gastos e ingresos manualmente
- ✅ Importar transacciones desde CSV/Excel
- ✅ Categorizar automáticamente los movimientos
- ✅ Visualizar estadísticas y gráficos interactivos
- ✅ Calcular ahorros mensuales
- ✅ Gestionar categorías personalizadas
- ✅ Gestionar Presupuestos y asignar presupuestos a las categorías

---

## 🛠️ Tecnologías Utilizadas

| Componente | Tecnología | Versión |
|------------|------------|---------|
| **Lenguaje** | Python | 3.11.14 |
| **Framework UI** | Flet | 0.28.3 |
| **ORM** | SQLAlchemy | 2.0.44 |
| **Base de Datos** | SQLite3 | 3.50.4 |
| **Utilidades de fecha** | python-dateutil | 2.8.0|
| **SSL para requests** | certifi | 2023.7.22 |
| **Procesamiento de archivos Excel** | openpyxl| 3.1.5 |

---

## 🚀 Instalación

### Requisitos Previos
- Python 3.11 o superior
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
flet run
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
flet build apk --verbose

# 2. Ubicación del APK
build/apk/app-release.apk

# 3. Transferir al dispositivo e instalar

 ° Habilitar "Instalar apps desconocidas" en Ajustes
 ° Copiar el archivo app-release.apk en el alamcenamiento del dispositivo andorit.
 ° Abrir el archivo e intalar siguiendo las instrucciones
 ° Configurar tu contraseña dentro de la aplicación 
 ° Realiza descarga de reportes periodicamente.
```

---

## 📂 Estructura del Proyecto

```
.
├── android                                # Configuración nativa para despliegue en Android
│   ├── AndroidManifest.xml                # Manifiesto de la app (permisos, nombre, iconos)
│   └── rest
│       └── xml
│           └── file_paths.xml             # Configuración de rutas para compartir archivos
├── assets                                 # Recursos estáticos de la aplicación
│   ├── icon_foreground.png                # Capa superior del icono adaptativo
│   └── icon.png                           # Icono principal de la aplicación
├── data                                   # Persistencia local de datos
│   └── expenses.db                        # Base de datos SQLite (se crea automáticamente)
├── flet.yaml                              # Configuración de empaquetado y build de Flet
├── LICENSE                                # Términos legales y licencia de uso
├── main.py                                # Punto de entrada principal (redirige a src/main.py)
├── README.md                              # Documentación del proyecto y guía de instalación
├── requirements.txt                       # Librerías necesarias (flet, sqlite3, etc.)
├── .gitignore                             # Archivos y carpetas excluidos del control de versiones
├── src                                    # Código fuente principal de la aplicación
│   ├── business                           # Lógica de negocio (Reglas y procesamiento)
│   │   ├── auth_manager.py                # Gestión de sesiones y autenticación de usuarios
│   │   ├── categorizer.py                 # Lógica para clasificar gastos de forma automática
│   │   ├── __init__.py                    # Inicializador del paquete business
│   │   ├── processor.py                   # Procesamiento de datos y cálculos financieros
│   │   └── report_generator.py            # Creación de reportes en PDF o formatos exportables
│   ├── data                               # Capa de acceso a datos
│   │   ├── database.py                    # Conector y métodos CRUD para SQLite
│   │   ├── __init__.py                    # Inicializador del paquete data
│   │   └── models.py                      # Definición de clases de datos (User, Expense, etc.)
│   ├── __init__.py                        # Inicializador del paquete src
│   ├── main.py                            # Inicialización de la App Flet y routing
│   ├── ui                                 # Interfaz de usuario (Vistas y Componentes)
│   │   ├── add_transaction_view.py        # Pantalla para registrar nuevos movimientos
│   │   ├── base_view.py                   # Clase base/plantilla para las vistas del sistema
│   │   ├── budget_view.py                 # Gestión de presupuestos mensuales
│   │   ├── categories_view.py             # Administración de categorías personalizadas
│   │   ├── charts_view.py                 # Visualización de estadísticas y gráficos
│   │   ├── history_view.py                # Listado histórico de transacciones
│   │   ├── home_view.py                   # Dashboard o pantalla de inicio
│   │   ├── __init__.py                    # Inicializador del paquete ui
│   │   ├── login_view.py                  # Interfaz de acceso y registro
│   │   ├── settings_view.py               # Ajustes de la app (idioma, tema, moneda)
│   │   └── widgets.py                     # Componentes reutilizables (botones, inputs, etc.)
│   └── utils                              # Utilidades y funciones auxiliares
│       ├── android_permissions.py         # Manejo de permisos específicos para Android
│       ├── config.py                      # Carga de variables de entorno o constantes
│       ├── helpers.py                     # Funciones de apoyo (formateo de fechas, moneda)
│       └── __init__.py                    # Inicializador del paquete utils
├── storage                                # Almacenamiento local de archivos de la app
│   ├── data                               # Archivos generados por el usuario
│   └── temp                               # Archivos temporales de procesamiento
└── temp                                   # Carpeta temporal (caché o compilación)

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
- Detección automática de columnas (fecha, descripción, monto, tipo)
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
- 🏠 Vivienda y equipos
- 🛍️ Vestimenta
- 📱 Comunicaciones
- 🍽️ Restaurantes y gastronomía
- ✈️ Hospedaje y viajes
- 🎲 Vicios y hobbies
- 🧼 Higiene/Cuidado personal
- 📦 Otros Gastos

**Ingresos:**
- 💵 Salario
- 💼 Freelance
- 📈 Inversiones
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
- Tendencia mensual de los últimos 12 meses

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
- Historial de 12 meses para análisis de tendencias

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

3. **Ver transacciones :**
   - Transacciones top del mes

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
   fecha,descripcion,monto,tipo
   30-10-2025,sueldo-neto,2500.00,ingreso
   28-10-2025,Supermercado,150.50,gasto
   27-10-2025,Taxi,12.00,gasto
   ```

2. **En la app:**
   - Ir a "Añadir"
   - Tocar "Importar desde archivo"
   - Seleccionar archivo
   - Confirmar importación

3. **Revisión automática:**
   - Validación de formato
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
python tests/run_test.py

# Test específico
python tests/test_database.py

# Ejemplo test de labase de datos
python tests/debug_db.py

# Ejemplo test de procesos
python tests/test_processor.py

```

### Generar Datos de Prueba

- Clonar el repositorio o descargar el archivo dataset_gastos_personales_simulado.csv de :
https://github.com/LuisCRicci/gastos_personales_dataset_generator

Guardar el archivo dentro del dispositivo donde se ejecuta la aplicación.

```bash

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
---

## 📞 Soporte

¿Problemas o preguntas?
- 📧 Email: luisricci@outlook.com.pe.
- 📱 Issues: [GitHub Issues](https://github.com/LuisCRicci/termowallet/issues)

---

## 🙏 Agradecimientos

- **Flet Framework** por la facilidad de desarrollo móvil
- **SQLAlchemy** por el ORM robusto
- Comunidad de Python por las excelentes librerías

---

**Desarrollado con ❤️  con la contribucion de:**

1. Luis Alberto Cusy Ricci 
2. Karen Paola Barrientos Quintanilla 