"""
✅ MIGRACIÓN: Agregar tabla category_budgets
Ejecutar una sola vez después de actualizar models.py

Guardar como: migrations/add_category_budgets.py
Ejecutar: python migrations/add_category_budgets.py
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.database import DatabaseManager
from src.data.models import Base, CategoryBudget
from sqlalchemy import inspect


def migrate_add_category_budgets():
    """
    Crea la tabla category_budgets si no existe
    """
    print("\n" + "="*60)
    print("🔄 MIGRACIÓN: Agregar tabla category_budgets")
    print("="*60 + "\n")
    
    try:
        # Inicializar DB
        db = DatabaseManager()
        
        # Verificar si la tabla ya existe
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        if "category_budgets" in existing_tables:
            print("✅ La tabla 'category_budgets' ya existe")
            print("   No se requiere migración")
        else:
            print("📋 Creando tabla 'category_budgets'...")
            
            # Crear solo la tabla CategoryBudget
            CategoryBudget.__table__.create(db.engine)
            
            print("✅ Tabla 'category_budgets' creada exitosamente")
            print("\n📊 Estructura de la tabla:")
            print("   - id (PK)")
            print("   - year")
            print("   - month")
            print("   - category_id (FK)")
            print("   - percentage")
            print("   - suggested_amount")
            print("   - notes")
            print("   - created_at")
            print("   - updated_at")
        
        # Mostrar estadísticas
        print("\n" + "="*60)
        print("📈 ESTADÍSTICAS DE LA BASE DE DATOS")
        print("="*60)
        
        stats = db.get_database_stats()
        print(f"   Total de transacciones: {stats.get('total_transactions', 0)}")
        print(f"   Total de categorías: {stats.get('total_categories', 0)}")
        print(f"   Categorías predeterminadas: {stats.get('default_categories', 0)}")
        print(f"   Categorías personalizadas: {stats.get('custom_categories', 0)}")
        
        # Verificar distribuciones existentes
        from datetime import datetime
        now = datetime.now()
        
        budgets = db.get_category_budgets(now.year, now.month)
        print(f"\n   Distribuciones del mes actual: {len(budgets)}")
        
        if len(budgets) == 0:
            print("\n💡 TIP: Aún no has configurado distribución de presupuesto")
            print("   Ve a 'Categorías' > 'Distribución de Presupuesto' para comenzar")
        
        print("\n" + "="*60)
        print("✅ MIGRACIÓN COMPLETADA")
        print("="*60 + "\n")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR durante la migración: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = migrate_add_category_budgets()
    sys.exit(0 if success else 1)