"""
Procesador de Transacciones Bancarias
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
        Columnas esperadas: fecha, descripcion, monto (nombres flexibles)
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

            self.df = self.df.rename(
                columns={
                    original_date_col: "fecha",
                    original_desc_col: "descripcion",
                    original_amount_col: "monto",
                }
            )

            return (
                True,
                f"Columnas validadas: fecha='{original_date_col}', descripcion='{original_desc_col}', monto='{original_amount_col}'",
            )
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

            # 7. Eliminar duplicados exactos
            duplicates = self.df.duplicated().sum()
            if duplicates > 0:
                self.errors.append(f"⚠️ {duplicates} registros duplicados eliminados")
                self.df = self.df.drop_duplicates()

            # 8. Ordenar por fecha (más reciente primero)
            self.df = self.df.sort_values("fecha", ascending=False)

            # 9. Reset index
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

    def categorize_transactions(self, categories_map: Dict[int, str]) -> bool:
        """
        Asigna categorías a las transacciones basándose en la descripción
        categories_map: {category_id: category_name} - ya con tipos simples
        """
        if self.df is None or len(self.df) == 0:
            return False

        try:
            # Invertir el mapa con tipos seguros
            name_to_id = {}
            for cat_id, cat_name in categories_map.items():
                safe_name = str(cat_name).strip().lower()
                name_to_id[safe_name] = int(cat_id)

            # Aplicar categorización (asegurar strings)
            self.df["categoria"] = self.df["descripcion"].apply(
                lambda desc: self.categorizer.categorize(
                    str(desc).lower() if desc else ""
                )
            )

            # Convertir a minúsculas para matching consistente
            self.df["categoria_lower"] = self.df["categoria"].str.lower().str.strip()

            # Asignar IDs usando el mapa seguro
            self.df["categoria_id"] = self.df["categoria_lower"].map(name_to_id)

            # Establecer categoría por defecto
            default_id = 1  # ID por defecto
            if "otros gastos" in name_to_id:
                default_id = name_to_id["otros gastos"]
            elif "otros" in name_to_id:
                default_id = name_to_id["otros"]
            elif name_to_id:
                default_id = next(iter(name_to_id.values()))

            # Rellenar valores nulos y convertir a entero
            self.df["categoria_id"] = (
                self.df["categoria_id"].fillna(default_id).astype(int)
            )

            # Limpiar columna temporal
            self.df.drop(columns=["categoria_lower"], inplace=True, errors="ignore")

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
                        "transaction_type": "expense",  # Por defecto son gastos
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
            summary = {
                "status": "success",
                "original_count": self.original_count,
                "processed_count": len(self.df),
                "removed_count": self.original_count - len(self.df),
                "total_amount": float(self.df["monto"].sum()),
                "average_amount": float(self.df["monto"].mean()),
                "min_amount": float(self.df["monto"].min()),
                "max_amount": float(self.df["monto"].max()),
                "date_range": {
                    "start": self.df["fecha"].min().strftime("%Y-%m-%d"),
                    "end": self.df["fecha"].max().strftime("%Y-%m-%d"),
                },
                "errors": self.errors,
            }

            # Resumen por categoría si existe
            if "categoria" in self.df.columns:
                summary["by_category"] = (
                    self.df.groupby("categoria")["monto"].sum().to_dict()
                )

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
