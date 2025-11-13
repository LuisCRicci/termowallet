"""
Tests para TransactionProcessor - CORREGIDO
"""

import unittest
import os
import pandas as pd
from datetime import datetime
from src.business.processor import TransactionProcessor


class TestTransactionProcessor(unittest.TestCase):
    """Tests para el procesador de transacciones"""

    def setUp(self):
        """Configuración antes de cada test"""
        self.processor = TransactionProcessor()
        # Crear archivo CSV de prueba
        self.test_file = "test_transactions.csv"
        test_data = pd.DataFrame({
            "fecha": ["2025-11-01", "2025-11-02", "2025-11-03"],
            "descripcion": ["Supermercado", "Gasolina", "Salario"],
            "monto": [100.50, 15.50, 3000.00]
        })
        test_data.to_csv(self.test_file, index=False)

    def tearDown(self):
        """Limpieza después de cada test"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        self.processor.reset()

    def test_load_file(self):
        """Test: Carga un archivo CSV"""
        success, message = self.processor.load_file(self.test_file)
        self.assertTrue(success)
        self.assertIn("3", message)

    def test_validate_columns(self):
        """Test: Valida columnas del archivo"""
        self.processor.load_file(self.test_file)
        success, message = self.processor.validate_columns()
        self.assertTrue(success)

    def test_clean_data(self):
        """Test: Limpia los datos"""
        self.processor.load_file(self.test_file)
        self.processor.validate_columns()
        success, message = self.processor.clean_data()
        self.assertTrue(success)
        self.assertIsNotNone(self.processor.df)

    def test_get_summary(self):
        """Test: Obtiene resumen de datos - CORREGIDO"""
        self.processor.load_file(self.test_file)
        self.processor.validate_columns()
        self.processor.clean_data()
        
        summary = self.processor.get_summary()
        
        # Verificar campos que SÍ debe tener el summary del processor
        self.assertIn("total_transactions", summary)
        self.assertIn("processed_count", summary)
        self.assertIn("total_amount", summary)
        self.assertIn("average_amount", summary)
        
        # Verificar valores
        self.assertEqual(summary["total_transactions"], 3)
        self.assertGreater(summary["total_amount"], 0)

    def test_get_processed_data(self):
        """Test: Obtiene datos procesados"""
        self.processor.load_file(self.test_file)
        self.processor.validate_columns()
        self.processor.clean_data()
        
        # Categorizar antes de obtener datos procesados
        categories_map = {1: "Alimentación", 2: "Transporte", 10: "Salario"}
        self.processor.categorize_transactions(categories_map)
        
        data = self.processor.get_processed_data()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)


if __name__ == '__main__':
    unittest.main()