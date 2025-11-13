"""
Tests para el módulo de base de datos
Archivo: tests/test_database.py
"""

import unittest
from datetime import datetime
from typing import List
import os
import sys
from src.data.models import Category, Transaction

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.database import DatabaseManager


class TestDatabaseManager(unittest.TestCase):
    """Tests para DatabaseManager"""

    def setUp(self):
        """Configuración antes de cada test"""
        self.db = DatabaseManager("test_database.db")

    def tearDown(self):
        """Limpieza después de cada test"""
        self.db.close()
        if os.path.exists("test_database.db"):
            os.remove("test_database.db")

    def test_initialize_default_categories(self):
        """Test: Verifica que se creen categorías por defecto"""
        categories = self.db.get_all_categories()
        self.assertGreater(len(categories), 0)

    def test_add_transaction(self):
        """Test: Añade una transacción"""
        categories = self.db.get_all_categories("expense")
        transaction = self.db.add_transaction(
            date=datetime.now(),
            description="Test transaction",
            amount=100.50,
            category_id=categories[0].id,
            transaction_type="expense",
        )
        self.assertIsNotNone(transaction.id)
        self.assertEqual(transaction.amount, 100.50)

    def test_get_monthly_summary(self):
        """Test: Obtiene resumen mensual"""
        summary = self.db.get_monthly_summary(2025, 11)
        self.assertIn("total_income", summary)
        self.assertIn("total_expenses", summary)
        self.assertIn("savings", summary)

    def test_add_category(self):
        """Test: Añade una categoría personalizada"""
        category = self.db.add_category(
            name="Test Category",
            icon="🧪",
            color="#ff0000",
            category_type="expense",
            description="Test description",
        )
        self.assertIsNotNone(category.id)
        self.assertEqual(category.name, "Test Category")

    def test_delete_transaction(self):
        """Test: Elimina una transacción"""
        categories = self.db.get_all_categories("expense")
        # Validación simple por si no hay categorías
        if not categories:
            self.fail("No se encontraron categorías de gasto para la prueba.")

        transaction = self.db.add_transaction(
            date=datetime.now(),
            description="To be deleted",
            amount=50.00,
            category_id=categories[0].id,
            transaction_type="expense",
        )
        result = self.db.delete_transaction(transaction.id)
        self.assertTrue(result)
