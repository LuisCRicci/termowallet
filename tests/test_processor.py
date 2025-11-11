# ========================================
# tests/test_processor.py
# ========================================

"""
Tests para el módulo de procesamiento
Archivo: tests/test_processor.py
"""

import unittest
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.business.processor import TransactionProcessor


class TestTransactionProcessor(unittest.TestCase):
    """Tests para TransactionProcessor"""

    def setUp(self):
        """Configuración antes de cada test"""
        self.processor = TransactionProcessor()

        # Crear archivo CSV de prueba
        self.test_csv = "test_data.csv"
        data = {
            "fecha": ["2025-11-01", "2025-11-02", "2025-11-03"],
            "descripcion": ["Supermercado", "Salario", "Uber"],
            "monto": [-100.50, 3000.00, -15.50],
        }
        df = pd.DataFrame(data)
        df.to_csv(self.test_csv, index=False)

    def tearDown(self):
        """Limpieza después de cada test"""
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)

    def test_load_file(self):
        """Test: Carga un archivo CSV"""
        success, message = self.processor.load_file(self.test_csv)
        self.assertTrue(success)

    def test_validate_columns(self):
        """Test: Valida columnas del archivo"""
        self.processor.load_file(self.test_csv)
        success, message = self.processor.validate_columns()
        self.assertTrue(success)

    def test_clean_data(self):
        """Test: Limpia los datos"""
        self.processor.load_file(self.test_csv)
        self.processor.validate_columns()
        success, message = self.processor.clean_data()
        self.assertTrue(success)

    def test_get_processed_data(self):
        """Test: Obtiene datos procesados"""
        self.processor.load_file(self.test_csv)
        self.processor.validate_columns()
        self.processor.clean_data()

        # Crear categorías de prueba
        categories_map = {1: "Alimentación", 2: "Salario", 3: "Transporte"}
        self.processor.categorize_transactions(categories_map)

        data = self.processor.get_processed_data()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_get_summary(self):
        """Test: Obtiene resumen de datos"""
        self.processor.load_file(self.test_csv)
        self.processor.validate_columns()
        self.processor.clean_data()

        summary = self.processor.get_summary()
        self.assertIn("total_transactions", summary)
        self.assertIn("total_income", summary)
        self.assertIn("total_expenses", summary)


if __name__ == "__main__":
    unittest.main()
