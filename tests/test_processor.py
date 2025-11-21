"""
Tests para TransactionProcessor - ACTUALIZADO CON KEYWORDS DE BD
Archivo: tests/test_processor.py
"""

import unittest
import os
import sys
import pandas as pd
from datetime import datetime

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.business.processor import TransactionProcessor
from src.data.database import DatabaseManager


class TestTransactionProcessor(unittest.TestCase):
    """Tests para el procesador de transacciones con keywords de BD"""

    def setUp(self):
        """Configuración antes de cada test"""
        self.processor = TransactionProcessor()
        self.db = DatabaseManager("test_processor.db")
        
        # Crear archivos CSV de prueba
        self.test_file = "test_transactions.csv"
        self.test_file_with_type = "test_transactions_with_type.csv"
        
        # CSV básico sin columna tipo
        test_data = pd.DataFrame({
            "fecha": ["2025-11-01", "2025-11-02", "2025-11-03"],
            "descripcion": ["Supermercado Wong", "Gasolina Primax", "Pizza Hut"],
            "monto": [100.50, 15.50, 25.00]
        })
        test_data.to_csv(self.test_file, index=False)
        
        # CSV con columna tipo
        test_data_with_type = pd.DataFrame({
            "fecha": ["2025-11-01", "2025-11-02", "2025-11-03", "2025-11-04"],
            "descripcion": ["Supermercado", "Taxi Uber", "Salario mensual", "Freelance proyecto"],
            "monto": [100.50, 15.50, 3000.00, 500.00],
            "tipo": ["gasto", "expense", "income", "ingreso"]
        })
        test_data_with_type.to_csv(self.test_file_with_type, index=False)

    def tearDown(self):
        """Limpieza después de cada test"""
        # Limpiar archivos
        for file in [self.test_file, self.test_file_with_type]:
            if os.path.exists(file):
                os.remove(file)
        
        # Cerrar BD
        self.db.close()
        if os.path.exists("test_processor.db"):
            os.remove("test_processor.db")
        
        # Resetear processor
        self.processor.reset()

    def test_load_file(self):
        """Test: Carga un archivo CSV"""
        success, message = self.processor.load_file(self.test_file)
        
        self.assertTrue(success, "Carga debe ser exitosa")
        self.assertIn("3", message, "Debe mencionar 3 registros")
        self.assertIsNotNone(self.processor.df)
        
        print(f"✅ Archivo cargado: {message}")

    def test_validate_columns(self):
        """Test: Valida columnas del archivo"""
        self.processor.load_file(self.test_file)
        success, message = self.processor.validate_columns()
        
        self.assertTrue(success, "Validación debe ser exitosa")
        self.assertIn("fecha", message.lower())
        
        print(f"✅ Columnas validadas: {message}")

    def test_validate_columns_with_type(self):
        """✅ NUEVO: Valida columnas incluyendo tipo"""
        self.processor.load_file(self.test_file_with_type)
        success, message = self.processor.validate_columns()
        
        self.assertTrue(success, "Validación debe ser exitosa")
        self.assertIn("tipo", message.lower(), "Debe detectar columna tipo")
        
        print(f"✅ Columnas con tipo validadas: {message}")

    def test_clean_data(self):
        """Test: Limpia los datos"""
        self.processor.load_file(self.test_file)
        self.processor.validate_columns()
        success, message = self.processor.clean_data()
        
        self.assertTrue(success, "Limpieza debe ser exitosa")
        self.assertIsNotNone(self.processor.df)
        
        # Verificar que agregó columna tipo por defecto
        self.assertIn("tipo", self.processor.df.columns)
        self.assertEqual(self.processor.df["tipo"].iloc[0], "expense")
        
        print(f"✅ Datos limpiados: {message}")

    def test_clean_data_with_type_column(self):
        """✅ NUEVO: Limpia datos con columna tipo"""
        self.processor.load_file(self.test_file_with_type)
        self.processor.validate_columns()
        success, message = self.processor.clean_data()
        
        self.assertTrue(success)
        
        # Verificar normalización de tipos
        tipos = self.processor.df["tipo"].unique()
        self.assertTrue(all(t in ["expense", "income"] for t in tipos),
                       "Todos los tipos deben estar normalizados")
        
        print(f"✅ Tipos normalizados: {list(tipos)}")

    def test_categorize_transactions_with_db_keywords(self):
        """✅ CORREGIDO: Categoriza usando keywords de la BD"""
        self.processor.load_file(self.test_file)
        self.processor.validate_columns()
        self.processor.clean_data()
        
        # ✅ CORRECCIÓN: Crear mapas de categorías correctamente
        categories_expense = self.db.get_all_categories("expense")
        categories_income = self.db.get_all_categories("income")
        
        # Crear mapas {id: name}
        categories_map_expense = {cat.id: cat.name for cat in categories_expense}
        categories_map_income = {cat.id: cat.name for cat in categories_income}
        
        # Cargar keywords desde BD al categorizador
        for cat in categories_expense:
            keywords = cat.get_keywords_list()
            if keywords:
                self.processor.categorizer.set_keywords(cat.name, keywords, "expense")
        
        for cat in categories_income:
            keywords = cat.get_keywords_list()
            if keywords:
                self.processor.categorizer.set_keywords(cat.name, keywords, "income")
        
        # Categorizar con los mapas correctos
        success = self.processor.categorize_transactions(
            categories_map_expense, 
            categories_map_income
        )
        
        self.assertTrue(success, "Categorización debe ser exitosa")
        self.assertIn("categoria_id", self.processor.df.columns)
        
        # Verificar que se asignaron categorías
        for idx, row in self.processor.df.iterrows():
            self.assertIsNotNone(row["categoria_id"])
            self.assertGreater(row["categoria_id"], 0)
        
        # Verificar categorización inteligente
        alimentacion = self.db.get_category_by_name("Alimentación", "expense")
        transporte = self.db.get_category_by_name("Transporte", "expense")
        
        # "Supermercado Wong" debe ir a Alimentación
        wong_row = self.processor.df[self.processor.df["descripcion"].str.contains("Wong", case=False)]
        if not wong_row.empty:
            self.assertEqual(wong_row.iloc[0]["categoria_id"], alimentacion.id,
                        "Wong debe categorizarse como Alimentación")
        
        # "Gasolina" debe ir a Transporte
        gasolina_row = self.processor.df[self.processor.df["descripcion"].str.contains("Gasolina", case=False)]
        if not gasolina_row.empty:
            self.assertEqual(gasolina_row.iloc[0]["categoria_id"], transporte.id,
                        "Gasolina debe categorizarse como Transporte")
        
        print(f"✅ Categorización con keywords de BD exitosa")

    def test_categorize_with_income_and_expense(self):
        """✅ CORREGIDO: Categoriza gastos e ingresos correctamente"""
        self.processor.load_file(self.test_file_with_type)
        self.processor.validate_columns()
        self.processor.clean_data()
        
        # ✅ CORRECCIÓN: Crear mapas y cargar keywords
        categories_expense = self.db.get_all_categories("expense")
        categories_income = self.db.get_all_categories("income")
        
        categories_map_expense = {cat.id: cat.name for cat in categories_expense}
        categories_map_income = {cat.id: cat.name for cat in categories_income}
        
        # Cargar keywords
        for cat in categories_expense:
            keywords = cat.get_keywords_list()
            if keywords:
                self.processor.categorizer.set_keywords(cat.name, keywords, "expense")
        
        for cat in categories_income:
            keywords = cat.get_keywords_list()
            if keywords:
                self.processor.categorizer.set_keywords(cat.name, keywords, "income")
        
        # Categorizar
        success = self.processor.categorize_transactions(
            categories_map_expense,
            categories_map_income
        )
        self.assertTrue(success)
        
        # Verificar que ingresos usan categorías de ingreso
        income_rows = self.processor.df[self.processor.df["tipo"] == "income"]
        
        for idx, row in income_rows.iterrows():
            category = self.db.get_category_by_id(row["categoria_id"])
            self.assertEqual(category.category_type, "income",
                        "Ingresos deben usar categorías de ingreso")
        
        print(f"✅ Ingresos y gastos categorizados correctamente")


    def test_get_summary(self):
        """Test: Obtiene resumen de datos"""
        self.processor.load_file(self.test_file_with_type)
        self.processor.validate_columns()
        self.processor.clean_data()
        
        summary = self.processor.get_summary()
        
        # Verificar campos del summary
        self.assertEqual(summary["status"], "success")
        self.assertIn("total_transactions", summary)
        self.assertIn("processed_count", summary)
        self.assertIn("total_amount", summary)
        self.assertIn("total_expenses", summary)
        self.assertIn("total_income", summary)
        self.assertIn("count_expenses", summary)
        self.assertIn("count_income", summary)
        
        # Verificar valores
        self.assertEqual(summary["total_transactions"], 4)
        self.assertGreater(summary["total_amount"], 0)
        self.assertGreater(summary["total_income"], 0)
        
        print(f"✅ Resumen: {summary['count_expenses']} gastos, "
              f"{summary['count_income']} ingresos, "
              f"Total: S/ {summary['total_amount']:.2f}")

    def test_get_processed_data(self):
        """✅ CORREGIDO: Obtiene datos procesados listos para BD"""
        self.processor.load_file(self.test_file)
        self.processor.validate_columns()
        self.processor.clean_data()
        
        # ✅ CORRECCIÓN
        categories_expense = self.db.get_all_categories("expense")
        categories_income = self.db.get_all_categories("income")
        
        categories_map_expense = {cat.id: cat.name for cat in categories_expense}
        categories_map_income = {cat.id: cat.name for cat in categories_income}
        
        for cat in categories_expense:
            keywords = cat.get_keywords_list()
            if keywords:
                self.processor.categorizer.set_keywords(cat.name, keywords, "expense")
        
        for cat in categories_income:
            keywords = cat.get_keywords_list()
            if keywords:
                self.processor.categorizer.set_keywords(cat.name, keywords, "income")
        
        self.processor.categorize_transactions(
            categories_map_expense,
            categories_map_income
        )
        
        data = self.processor.get_processed_data()
        
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # Verificar estructura de cada transacción
        for transaction in data:
            self.assertIn("date", transaction)
            self.assertIn("description", transaction)
            self.assertIn("amount", transaction)
            self.assertIn("category_id", transaction)
            self.assertIn("transaction_type", transaction)
            self.assertIn("source", transaction)
            
            self.assertIsInstance(transaction["date"], datetime)
            self.assertIsInstance(transaction["amount"], float)
            self.assertIn(transaction["transaction_type"], ["expense", "income"])
        
        print(f"✅ {len(data)} transacciones listas para insertar")

    def test_full_import_workflow(self):
        """✅ CORREGIDO: Prueba flujo completo de importación"""
        # 1. Cargar
        success, message = self.processor.load_file(self.test_file_with_type)
        self.assertTrue(success)
        
        # 2. Validar
        success, message = self.processor.validate_columns()
        self.assertTrue(success)
        
        # 3. Limpiar
        success, message = self.processor.clean_data()
        self.assertTrue(success)
        
        # 4. ✅ CORRECCIÓN: Categorizar con keywords de BD
        categories_expense = self.db.get_all_categories("expense")
        categories_income = self.db.get_all_categories("income")
        
        categories_map_expense = {cat.id: cat.name for cat in categories_expense}
        categories_map_income = {cat.id: cat.name for cat in categories_income}
        
        for cat in categories_expense:
            keywords = cat.get_keywords_list()
            if keywords:
                self.processor.categorizer.set_keywords(cat.name, keywords, "expense")
        
        for cat in categories_income:
            keywords = cat.get_keywords_list()
            if keywords:
                self.processor.categorizer.set_keywords(cat.name, keywords, "income")
        
        success = self.processor.categorize_transactions(
            categories_map_expense,
            categories_map_income
        )
        self.assertTrue(success)
        
        # 5. Obtener datos procesados
        data = self.processor.get_processed_data()
        self.assertEqual(len(data), 4)
        
        # 6. Insertar en BD
        count = self.db.add_transactions_bulk(data)
        self.assertEqual(count, 4, "Deben insertarse 4 transacciones")
        
        # 7. Verificar en BD
        all_transactions = self.db.get_all_transactions()
        self.assertEqual(len(all_transactions), 4)
        
        # Verificar que hay ingresos y gastos
        expenses = [t for t in all_transactions if t.transaction_type == "expense"]
        incomes = [t for t in all_transactions if t.transaction_type == "income"]
        
        self.assertGreater(len(expenses), 0, "Debe haber gastos")
        self.assertGreater(len(incomes), 0, "Debe haber ingresos")
        
        print(f"✅ Flujo completo: {len(expenses)} gastos + {len(incomes)} ingresos importados")

    def test_keyword_based_categorization(self):
        """✅ CORREGIDO: Verifica categorización basada en keywords específicas"""
        # Crear CSV con palabras clave específicas
        test_data = pd.DataFrame({
            "fecha": ["2025-11-01", "2025-11-02", "2025-11-03", "2025-11-04"],
            "descripcion": ["Netflix suscripción", "Uber viaje", "Farmacia Inkafarma", "Universidad cuota"],
            "monto": [29.90, 12.50, 45.00, 800.00]
        })
        
        test_file = "test_keywords.csv"
        test_data.to_csv(test_file, index=False)
        
        try:
            # Procesar
            self.processor.load_file(test_file)
            self.processor.validate_columns()
            self.processor.clean_data()
            
            # ✅ CORRECCIÓN
            categories_expense = self.db.get_all_categories("expense")
            categories_income = self.db.get_all_categories("income")
            
            categories_map_expense = {cat.id: cat.name for cat in categories_expense}
            categories_map_income = {cat.id: cat.name for cat in categories_income}
            
            for cat in categories_expense:
                keywords = cat.get_keywords_list()
                if keywords:
                    self.processor.categorizer.set_keywords(cat.name, keywords, "expense")
            
            self.processor.categorize_transactions(
                categories_map_expense,
                categories_map_income
            )
            
            # Verificar categorizaciones específicas
            entretenimiento = self.db.get_category_by_name("Entretenimiento", "expense")
            transporte = self.db.get_category_by_name("Transporte", "expense")
            salud = self.db.get_category_by_name("Salud", "expense")
            educacion = self.db.get_category_by_name("Educación", "expense")
            
            df = self.processor.df
            
            # Netflix -> Entretenimiento
            netflix = df[df["descripcion"].str.contains("Netflix", case=False)].iloc[0]
            self.assertEqual(netflix["categoria_id"], entretenimiento.id)
            
            # Uber -> Transporte
            uber = df[df["descripcion"].str.contains("Uber", case=False)].iloc[0]
            self.assertEqual(uber["categoria_id"], transporte.id)
            
            # Farmacia -> Salud
            farmacia = df[df["descripcion"].str.contains("Farmacia", case=False)].iloc[0]
            self.assertEqual(farmacia["categoria_id"], salud.id)
            
            # Universidad -> Educación
            universidad = df[df["descripcion"].str.contains("Universidad", case=False)].iloc[0]
            self.assertEqual(universidad["categoria_id"], educacion.id)
            
            print("✅ Todas las keywords específicas categorizaron correctamente")
            
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
            
    def test_preview_data(self):
        """Test: Vista previa de datos"""
        self.processor.load_file(self.test_file)
        self.processor.validate_columns()
        self.processor.clean_data()
        
        preview = self.processor.preview_data(rows=2)
        
        self.assertIsNotNone(preview)
        self.assertEqual(len(preview), 2)
        
        print(f"✅ Vista previa de {len(preview)} filas generada")

    def test_reset(self):
        """Test: Resetea el procesador"""
        self.processor.load_file(self.test_file)
        self.processor.validate_columns()
        
        self.assertIsNotNone(self.processor.df)
        
        self.processor.reset()
        
        self.assertIsNone(self.processor.df)
        self.assertEqual(len(self.processor.errors), 0)
        self.assertEqual(self.processor.original_count, 0)
        
        print("✅ Procesador reseteado correctamente")


if __name__ == '__main__':
    unittest.main(verbosity=2)