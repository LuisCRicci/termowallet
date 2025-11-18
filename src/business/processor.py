"""
Procesador de Transacciones Bancarias - CON SOPORTE PARA COLUMNA TIPO
Archivo: src/business/processor.py
"""

import pandas as pd
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from src.business.categorizer import TransactionCategorizer


class TransactionProcessor:
    """Clase para procesar y limpiar archivos de transacciones bancarias"""

    def __init__(self):
        self.categorizer = TransactionCategorizer()
        self.df = None
        self.errors = []
        self.original_count = 0

    def load_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Carga un archivo CSV o Excel
        Returns: (success, message)
        """
        try:
            self.errors = []

            if file_path.endswith(".csv"):
                # Intentar diferentes encodings
                encodings = ["utf-8", "latin-1", "iso-8859-1", "cp1252"]
                for encoding in encodings:
                    try:
                        self.df = pd.read_csv(file_path, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    return False, "No se pudo decodificar el archivo CSV"

            elif file_path.endswith((".xlsx", ".xls")):
                self.df = pd.read_excel(file_path)
            else:
                return False, "Formato no soportado. Use CSV o Excel (.xlsx, .xls)"

            if self.df is None or len(self.df) == 0:
                return False, "El archivo está vacío"

            self.original_count = len(self.df)
            return True, f"Archivo cargado: {self.original_count} registros"

        except FileNotFoundError:
            return False, "Archivo no encontrado"
        except Exception as e:
            return False, f"Error al cargar archivo: {str(e)}"

    def validate_columns(self) -> Tuple[bool, str]:
        """
        Valida que el archivo tenga las columnas necesarias
        Columnas esperadas: fecha, descripcion, monto, tipo (opcional)
        """
        if self.df is None:
            return False, "No hay datos cargados"

        # Convertir nombres de columnas a minúsculas para comparación
        columns_lower = [col.lower().strip() for col in self.df.columns]

        # Buscar columnas de fecha
        date_keywords = ["fecha", "date", "dia", "day", "when", "datetime"]
        date_cols = [
            col
            for col in columns_lower
            if any(keyword in col for keyword in date_keywords)
        ]

        # Buscar columnas de descripción
        desc_keywords = [
            "descripcion",
            "description",
            "concepto",
            "detalle",
            "detail",
            "desc",
            "memo",
            "nota",
            "note",
        ]
        desc_cols = [
            col
            for col in columns_lower
            if any(keyword in col for keyword in desc_keywords)
        ]

        # Buscar columnas de monto
        amount_keywords = [
            "monto",
            "amount",
            "importe",
            "valor",
            "value",
            "precio",
            "price",
            "total",
            "cantidad",
            "quantity",
        ]
        amount_cols = [
            col
            for col in columns_lower
            if any(keyword in col for keyword in amount_keywords)
        ]

        # ✅ NUEVO: Buscar columna de tipo
        type_keywords = ["tipo", "type", "categoria", "category"]
        type_cols = [
            col
            for col in columns_lower
            if any(keyword in col for keyword in type_keywords)
        ]

        # Validaciones
        if not date_cols:
            return (
                False,
                f"No se encontró columna de fecha. Columnas disponibles: {', '.join(self.df.columns)}",
            )
        if not desc_cols:
            return (
                False,
                f"No se encontró columna de descripción. Columnas disponibles: {', '.join(self.df.columns)}",
            )
        if not amount_cols:
            return (
                False,
                f"No se encontró columna de monto. Columnas disponibles: {', '.join(self.df.columns)}",
            )

        # Normalizar nombres de columnas usando el índice original
        try:
            original_date_col = self.df.columns[columns_lower.index(date_cols[0])]
            original_desc_col = self.df.columns[columns_lower.index(desc_cols[0])]
            original_amount_col = self.df.columns[columns_lower.index(amount_cols[0])]

            rename_dict = {
                original_date_col: "fecha",
                original_desc_col: "descripcion",
                original_amount_col: "monto",
            }

            # ✅ NUEVO: Renombrar columna de tipo si existe
            if type_cols:
                original_type_col = self.df.columns[columns_lower.index(type_cols[0])]
                rename_dict[original_type_col] = "tipo"

            self.df = self.df.rename(columns=rename_dict)

            message = f"Columnas validadas: fecha='{original_date_col}', descripcion='{original_desc_col}', monto='{original_amount_col}'"
            if type_cols:
                message += f", tipo='{original_type_col}'"

            return (True, message)
        except Exception as e:
            return False, f"Error al normalizar columnas: {str(e)}"

    def clean_data(self) -> Tuple[bool, str]:
        """
        Limpia y estandariza los datos
        """
        if self.df is None:
            return False, "No hay datos para limpiar"

        initial_count = len(self.df)
        self.errors = []

        try:
            # 1. Eliminar filas completamente vacías
            self.df = self.df.dropna(how="all")

            # 2. Convertir y limpiar fechas
            self.df["fecha"] = pd.to_datetime(self.df["fecha"], errors="coerce")
            invalid_dates = self.df["fecha"].isna().sum()
            if invalid_dates > 0:
                self.errors.append(f"⚠️ {invalid_dates} fechas inválidas eliminadas")
                self.df = self.df.dropna(subset=["fecha"])

            # 3. Limpiar descripción
            self.df["descripcion"] = self.df["descripcion"].astype(str)
            self.df["descripcion"] = self.df["descripcion"].str.strip()

            # Reemplazar valores comunes de "vacío"
            empty_values = ["", "nan", "none", "null", "n/a", "na"]
            self.df["descripcion"] = self.df["descripcion"].apply(
                lambda x: None if x.lower() in empty_values else x
            )

            desc_count = self.df["descripcion"].isna().sum()
            if desc_count > 0:
                self.errors.append(f"⚠️ {desc_count} descripciones vacías eliminadas")
                self.df = self.df.dropna(subset=["descripcion"])

            # 4. Limpiar y convertir monto
            self.df["monto"] = self.df["monto"].astype(str)

            # Eliminar símbolos de moneda comunes
            currency_symbols = ["S/", "S/.", "$", "€", "£", "USD", "PEN", "EUR"]
            for symbol in currency_symbols:
                self.df["monto"] = self.df["monto"].str.replace(symbol, "", regex=False)

            # Eliminar espacios y comas
            self.df["monto"] = self.df["monto"].str.replace(" ", "")
            self.df["monto"] = self.df["monto"].str.replace(",", "")

            # Convertir a numérico
            self.df["monto"] = pd.to_numeric(self.df["monto"], errors="coerce")

            invalid_amounts = self.df["monto"].isna().sum()
            if invalid_amounts > 0:
                self.errors.append(f"⚠️ {invalid_amounts} montos inválidos eliminados")
                self.df = self.df.dropna(subset=["monto"])

            # 5. Convertir montos negativos a positivos
            self.df["monto"] = self.df["monto"].abs()

            # 6. Eliminar montos cero o muy pequeños
            zero_count = len(self.df[self.df["monto"] <= 0.001])
            if zero_count > 0:
                self.errors.append(f"⚠️ {zero_count} montos en cero eliminados")
                self.df = self.df[self.df["monto"] > 0.001]

            # ✅ NUEVO: 7. Procesar columna tipo si existe
            if "tipo" in self.df.columns:
                self.df["tipo"] = self.df["tipo"].astype(str).str.lower().str.strip()
                
                # Normalizar valores de tipo
                type_mapping = {
                    "gasto": "expense",
                    "gastos": "expense",
                    "expense": "expense",
                    "egreso": "expense",
                    "egresos": "expense",
                    "salida": "expense",
                    "ingreso": "income",
                    "ingresos": "income",
                    "income": "income",
                    "entrada": "income",
                }
                
                self.df["tipo"] = self.df["tipo"].map(type_mapping)
                
                # Contar valores inválidos
                invalid_types = self.df["tipo"].isna().sum()
                if invalid_types > 0:
                    self.errors.append(f"⚠️ {invalid_types} tipos inválidos (se asumirán como gastos)")
                    # Rellenar tipos inválidos con "expense"
                    self.df["tipo"] = self.df["tipo"].fillna("expense")
            else:
                # Si no existe columna tipo, asumir todos son gastos
                self.df["tipo"] = "expense"

            # 8. Eliminar duplicados exactos
            duplicates = self.df.duplicated().sum()
            if duplicates > 0:
                self.errors.append(f"⚠️ {duplicates} registros duplicados eliminados")
                self.df = self.df.drop_duplicates()

            # 9. Ordenar por fecha (más reciente primero)
            self.df = self.df.sort_values("fecha", ascending=False)

            # 10. Reset index
            self.df = self.df.reset_index(drop=True)

            final_count = len(self.df)
            removed = initial_count - final_count

            # Construir mensaje
            message = f"✅ Limpieza completada: {final_count} registros válidos"
            if removed > 0:
                message += f" ({removed} registros eliminados)"
            if self.errors:
                message += "\n" + "\n".join(self.errors)

            return True, message

        except Exception as e:
            return False, f"❌ Error en limpieza: {str(e)}"

    def categorize_transactions(self, categories_map_expense: Dict[int, str], 
                                categories_map_income: Dict[int, str]) -> bool:
        """
        Asigna categorías a las transacciones basándose en la descripción y el tipo
        categories_map_expense: {category_id: category_name} para gastos
        categories_map_income: {category_id: category_name} para ingresos
        """
        if self.df is None or len(self.df) == 0:
            return False

        try:
            # Invertir los mapas con tipos seguros
            name_to_id_expense = {}
            for cat_id, cat_name in categories_map_expense.items():
                safe_name = str(cat_name).strip().lower()
                name_to_id_expense[safe_name] = int(cat_id)

            name_to_id_income = {}
            for cat_id, cat_name in categories_map_income.items():
                safe_name = str(cat_name).strip().lower()
                name_to_id_income[safe_name] = int(cat_id)

            # Aplicar categorización según el tipo
            def assign_category(row):
                desc = str(row["descripcion"]).lower() if row["descripcion"] else ""
                transaction_type = row["tipo"]
                
                # ✅ CORREGIDO: Pasar el tipo de transacción al categorizador
                category_name = self.categorizer.categorize(desc, transaction_type)
                category_name_lower = category_name.lower().strip()
                
                # Elegir el mapa correcto según el tipo
                if transaction_type == "income":
                    name_to_id = name_to_id_income
                    default_id = next(iter(name_to_id_income.values())) if name_to_id_income else 1
                else:
                    name_to_id = name_to_id_expense
                    default_id = name_to_id_expense.get("otros gastos", 
                                 name_to_id_expense.get("otros", 
                                 next(iter(name_to_id_expense.values())) if name_to_id_expense else 1))
                
                # Buscar ID de categoría
                category_id = name_to_id.get(category_name_lower, default_id)
                
                return category_id

            self.df["categoria_id"] = self.df.apply(assign_category, axis=1)

            return True

        except Exception as e:
            print(f"❌ Error en categorización: {e}")
            return False

    def get_processed_data(self) -> List[Dict]:
        """
        Retorna los datos procesados listos para insertar en la BD
        """
        if self.df is None or len(self.df) == 0:
            return []

        try:
            transactions = []
            for _, row in self.df.iterrows():
                transactions.append(
                    {
                        "date": row["fecha"].to_pydatetime(),
                        "description": str(row["descripcion"]),
                        "amount": float(row["monto"]),
                        "category_id": int(row["categoria_id"]),
                        "transaction_type": str(row["tipo"]),  # ✅ Ahora usa el tipo del CSV
                        "source": "imported",
                        "original_description": str(row["descripcion"]),
                    }
                )

            return transactions

        except Exception as e:
            print(f"❌ Error al preparar datos: {e}")
            return []

    def get_summary(self) -> Dict:
        """Obtiene un resumen de los datos procesados"""
        if self.df is None or len(self.df) == 0:
            return {"status": "empty", "message": "No hay datos procesados"}

        try:
            # ✅ NUEVO: Separar estadísticas por tipo
            expenses = self.df[self.df["tipo"] == "expense"]
            incomes = self.df[self.df["tipo"] == "income"]

            summary = {
                "status": "success",
                "original_count": self.original_count,
                "processed_count": len(self.df),
                "total_transactions": len(self.df),
                "removed_count": self.original_count - len(self.df),
                "total_amount": float(self.df["monto"].sum()),
                "total_expenses": float(expenses["monto"].sum()) if len(expenses) > 0 else 0.0,
                "total_income": float(incomes["monto"].sum()) if len(incomes) > 0 else 0.0,
                "count_expenses": len(expenses),
                "count_income": len(incomes),
                "average_amount": float(self.df["monto"].mean()),
                "min_amount": float(self.df["monto"].min()),
                "max_amount": float(self.df["monto"].max()),
                "date_range": {
                    "start": self.df["fecha"].min().strftime("%Y-%m-%d"),
                    "end": self.df["fecha"].max().strftime("%Y-%m-%d"),
                },
                "errors": self.errors,
            }

            return summary

        except Exception as e:
            return {"status": "error", "message": f"Error al generar resumen: {str(e)}"}

    def preview_data(self, rows: int = 10) -> Optional[pd.DataFrame]:
        """Retorna una vista previa de los datos procesados"""
        if self.df is None or len(self.df) == 0:
            return None

        return self.df.head(rows)

    def export_to_dict(self) -> List[Dict]:
        """Exporta los datos procesados a una lista de diccionarios"""
        if self.df is None or len(self.df) == 0:
            return []

        return self.df.to_dict("records")

    def reset(self):
        """Resetea el procesador"""
        self.df = None
        self.errors = []
        self.original_count = 0