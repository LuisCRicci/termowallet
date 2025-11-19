"""
Tests para el módulo de base de datos - ACTUALIZADO CON KEYWORDS
Archivo: tests/test_database.py
"""

import unittest
from datetime import datetime
from typing import List
import os
import sys

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.database import DatabaseManager
from src.data.models import Category, Transaction


class TestDatabaseManager(unittest.TestCase):
    """Tests para DatabaseManager con soporte de keywords"""

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
        print(f"✅ {len(categories)} categorías creadas por defecto")

    def test_initialize_default_keywords(self):
        """✅ NUEVO: Verifica que las categorías tengan keywords por defecto"""
        categories = self.db.get_all_categories()
        
        categories_with_keywords = 0
        total_keywords = 0
        
        for category in categories:
            keywords = category.get_keywords_list()
            if len(keywords) > 0:
                categories_with_keywords += 1
                total_keywords += len(keywords)
        
        self.assertGreater(categories_with_keywords, 0, 
                          "Debe haber al menos una categoría con keywords")
        self.assertGreater(total_keywords, 0, 
                          "Debe haber al menos una palabra clave")
        
        print(f"✅ {categories_with_keywords} categorías con keywords")
        print(f"✅ {total_keywords} palabras clave en total")

    def test_category_keywords_methods(self):
        """✅ NUEVO: Verifica métodos de keywords en Category"""
        # Obtener una categoría
        alimentacion = self.db.get_category_by_name("Alimentación", "expense")
        self.assertIsNotNone(alimentacion, "Categoría 'Alimentación' debe existir")
        
        # Verificar que tenga keywords por defecto
        keywords_before = alimentacion.get_keywords_list()
        self.assertGreater(len(keywords_before), 0, 
                          "Alimentación debe tener keywords por defecto")
        
        # Agregar nueva keyword
        new_keywords = keywords_before + ["test_keyword"]
        alimentacion.set_keywords_list(new_keywords)
        self.db.session.commit()
        
        # Verificar que se guardó
        alimentacion_updated = self.db.get_category_by_id(alimentacion.id)
        keywords_after = alimentacion_updated.get_keywords_list()
        
        self.assertIn("test_keyword", keywords_after, 
                     "Nueva keyword debe estar en la lista")
        self.assertEqual(len(keywords_after), len(keywords_before) + 1,
                        "Debe haber una keyword más")
        
        print(f"✅ Keywords antes: {len(keywords_before)}, después: {len(keywords_after)}")

    def test_restore_default_keywords(self):
        """✅ NUEVO: Verifica restauración de keywords por defecto"""
        # Obtener una categoría y modificar sus keywords
        transporte = self.db.get_category_by_name("Transporte", "expense")
        self.assertIsNotNone(transporte)
        
        # Guardar keywords originales
        original_keywords = transporte.get_keywords_list()
        original_count = len(original_keywords)
        
        # Modificar keywords
        transporte.set_keywords_list(["test1", "test2"])
        self.db.session.commit()
        
        # Verificar que cambió
        modified_keywords = self.db.get_category_by_id(transporte.id).get_keywords_list()
        self.assertEqual(len(modified_keywords), 2)
        
        # Restaurar keywords por defecto
        result = self.db.restore_default_keywords(transporte.id)
        
        self.assertTrue(result["success"], "Restauración debe ser exitosa")
        self.assertEqual(result["updated_count"], 1, "Debe actualizar 1 categoría")
        
        # Verificar que se restauraron
        restored = self.db.get_category_by_id(transporte.id)
        restored_keywords = restored.get_keywords_list()
        
        self.assertEqual(len(restored_keywords), original_count,
                        "Debe tener la misma cantidad de keywords originales")
        
        print(f"✅ Keywords restauradas: {len(restored_keywords)}")

    def test_add_transaction(self):
        """Test: Añade una transacción"""
        categories = self.db.get_all_categories("expense")
        self.assertGreater(len(categories), 0, "Debe haber categorías de gasto")
        
        transaction = self.db.add_transaction(
            date=datetime.now(),
            description="Test transaction",
            amount=100.50,
            category_id=categories[0].id,
            transaction_type="expense",
        )
        
        self.assertIsNotNone(transaction.id)
        self.assertEqual(transaction.amount, 100.50)
        self.assertEqual(transaction.transaction_type, "expense")
        
        print(f"✅ Transacción creada: ID={transaction.id}, Monto={transaction.amount}")

    def test_get_monthly_summary(self):
        """Test: Obtiene resumen mensual"""
        summary = self.db.get_monthly_summary(2025, 11)
        
        self.assertIn("total_income", summary)
        self.assertIn("total_expenses", summary)
        self.assertIn("savings", summary)
        self.assertIn("month_name", summary)
        
        # Verificar que month_name está en español
        self.assertEqual(summary["month_name"], "Noviembre")
        
        print(f"✅ Resumen mensual: {summary['month_name']} {summary['year']}")

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
        self.assertFalse(category.is_default, "Categoría personalizada no debe ser default")
        
        print(f"✅ Categoría personalizada creada: {category.name}")

    def test_add_category_with_keywords(self):
        """✅ NUEVO: Añade categoría con keywords personalizadas"""
        category = self.db.add_category(
            name="Mascotas",
            icon="🐶",
            color="#f59e0b",
            category_type="expense",
            description="Gastos de mascotas",
        )
        
        # Agregar keywords
        keywords = ["veterinario", "comida perro", "pet shop", "gato"]
        category.set_keywords_list(keywords)
        self.db.session.commit()
        
        # Verificar
        category_check = self.db.get_category_by_id(category.id)
        saved_keywords = category_check.get_keywords_list()
        
        self.assertEqual(len(saved_keywords), 4, "Debe tener 4 keywords")
        self.assertIn("veterinario", saved_keywords)
        self.assertIn("comida perro", saved_keywords)
        
        print(f"✅ Categoría con keywords: {category.name} ({len(saved_keywords)} keywords)")

    def test_delete_transaction(self):
        """Test: Elimina una transacción"""
        categories = self.db.get_all_categories("expense")
        
        if not categories:
            self.fail("No se encontraron categorías de gasto para la prueba.")
        
        transaction = self.db.add_transaction(
            date=datetime.now(),
            description="To be deleted",
            amount=50.00,
            category_id=categories[0].id,
            transaction_type="expense",
        )
        
        transaction_id = transaction.id
        result = self.db.delete_transaction(transaction_id)
        
        self.assertTrue(result, "Eliminación debe ser exitosa")
        
        # Verificar que ya no existe
        deleted = self.db.session.query(Transaction).filter_by(id=transaction_id).first()
        self.assertIsNone(deleted, "Transacción debe estar eliminada")
        
        print(f"✅ Transacción eliminada correctamente")

    def test_update_transaction(self):
        """Test: Actualiza una transacción"""
        categories = self.db.get_all_categories("expense")
        
        # Crear transacción
        transaction = self.db.add_transaction(
            date=datetime.now(),
            description="Original description",
            amount=100.00,
            category_id=categories[0].id,
            transaction_type="expense",
        )
        
        # Actualizar
        new_date = datetime(2025, 12, 1)
        result = self.db.update_transaction(
            transaction_id=transaction.id,
            date=new_date,
            description="Updated description",
            amount=150.00,
            category_id=categories[0].id,
            notes="Updated notes"
        )
        
        self.assertTrue(result, "Actualización debe ser exitosa")
        
        # Verificar cambios
        updated = self.db.session.query(Transaction).filter_by(id=transaction.id).first()
        self.assertEqual(updated.description, "Updated description")
        self.assertEqual(updated.amount, 150.00)
        self.assertEqual(updated.notes, "Updated notes")
        
        print(f"✅ Transacción actualizada correctamente")

    def test_get_expenses_by_category(self):
        """Test: Obtiene gastos agrupados por categoría"""
        # Crear transacciones de prueba
        categories = self.db.get_all_categories("expense")[:3]
        
        for i, category in enumerate(categories):
            self.db.add_transaction(
                date=datetime.now(),
                description=f"Test expense {i}",
                amount=100.0 * (i + 1),
                category_id=category.id,
                transaction_type="expense",
            )
        
        # Obtener resumen
        expenses = self.db.get_expenses_by_category(
            datetime.now().year, 
            datetime.now().month
        )
        
        self.assertGreater(len(expenses), 0, "Debe haber gastos agrupados")
        
        for expense in expenses:
            self.assertIn("category", expense)
            self.assertIn("total", expense)
            self.assertGreater(expense["total"], 0)
        
        print(f"✅ {len(expenses)} categorías con gastos")

    def test_budget_operations(self):
        """Test: Operaciones de presupuesto"""
        year = datetime.now().year
        month = datetime.now().month
        
        # Crear presupuesto
        budget = self.db.create_or_update_budget(
            year=year,
            month=month,
            income_goal=5000.0,
            expense_limit=3000.0,
            savings_goal=2000.0,
            notes="Test budget"
        )
        
        self.assertIsNotNone(budget)
        self.assertEqual(budget.income_goal, 5000.0)
        
        # Obtener estado
        status = self.db.get_budget_status(year, month)
        
        self.assertTrue(status["budget_exists"])
        self.assertEqual(status["income_goal"], 5000.0)
        self.assertEqual(status["expense_limit"], 3000.0)
        
        print(f"✅ Presupuesto creado y verificado")

    def test_database_stats(self):
        """Test: Estadísticas de base de datos"""
        stats = self.db.get_database_stats()
        
        self.assertIn("total_transactions", stats)
        self.assertIn("total_categories", stats)
        self.assertIn("custom_categories", stats)
        self.assertIn("total_income", stats)
        self.assertIn("total_expenses", stats)
        
        self.assertGreaterEqual(stats["total_categories"], 13, 
                               "Debe haber al menos 13 categorías por defecto")
        
        print(f"✅ Estadísticas: {stats['total_categories']} categorías, "
              f"{stats['total_transactions']} transacciones")

    def test_clear_and_reset(self):
        """Test: Limpieza y reseteo de base de datos"""
        # Crear datos de prueba
        categories = self.db.get_all_categories("expense")
        self.db.add_transaction(
            date=datetime.now(),
            description="Test",
            amount=100.0,
            category_id=categories[0].id,
            transaction_type="expense",
        )
        
        # Limpiar transacciones
        result = self.db.clear_all_transactions()
        self.assertTrue(result, "Limpieza debe ser exitosa")
        
        transactions = self.db.get_all_transactions()
        self.assertEqual(len(transactions), 0, "No debe haber transacciones")
        
        # Verificar que categorías siguen existiendo
        categories_after = self.db.get_all_categories()
        self.assertGreater(len(categories_after), 0, "Categorías deben seguir existiendo")
        
        print(f"✅ Limpieza exitosa, categorías preservadas")


if __name__ == '__main__':
    # Configurar unittest para mejor output
    unittest.main(verbosity=2)