"""
Script para diagnosticar la base de datos de TermoWallet
Ejecutar con: python src/tests/debug_db.py
"""

import sys
import os
import unittest

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime

# Importación ABSOLUTA (sin ..)
from src.data.database import DatabaseManager


def diagnose_database():
    """Diagnostica el estado de la base de datos"""
    db = DatabaseManager()

    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE BASE DE DATOS - TermoWallet")
    print("=" * 60)

    # 1. Estadísticas generales
    stats = db.get_database_stats()
    print("\n📊 ESTADÍSTICAS GENERALES:")
    print(f"   Total de transacciones: {stats.get('total_transactions', 0)}")
    print(f"   Total de categorías: {stats.get('total_categories', 0)}")
    print(f"   Categorías personalizadas: {stats.get('custom_categories', 0)}")
    print(f"   Ingresos totales: S/ {stats.get('total_income', 0):.2f}")
    print(f"   Gastos totales: S/ {stats.get('total_expenses', 0):.2f}")

    # 2. Todas las transacciones
    all_transactions = db.get_all_transactions()
    print(f"\n📝 TODAS LAS TRANSACCIONES ({len(all_transactions)}):")

    for t in all_transactions:
        tipo = "💰" if t.transaction_type == "income" else "💸"
        fecha = t.date.strftime("%d/%m/%Y")
        print(
            f"   {tipo} {fecha} | {t.description[:30]:30} | S/ {t.amount:8.2f} | Cat ID: {t.category_id}"
        )

    # 3. Transacciones por mes
    now = datetime.now()
    year = now.year
    month = now.month

    print(f"\n📅 TRANSACCIONES DE {now.strftime('%B %Y').upper()}:")
    monthly_trans = db.get_transactions_by_month(year, month)
    print(f"   Total: {len(monthly_trans)} transacciones")

    if monthly_trans:
        for t in monthly_trans:
            tipo = "💰" if t.transaction_type == "income" else "💸"
            fecha = t.date.strftime("%d/%m/%Y %H:%M")
            category = db.get_category_by_id(t.category_id)
            cat_name = category.name if category else "Sin categoría"
            print(
                f"   {tipo} {fecha} | {t.description[:25]:25} | S/ {t.amount:8.2f} | {cat_name}"
            )
    else:
        print("   ❌ No hay transacciones en este mes")

    # 4. Resumen mensual
    summary = db.get_monthly_summary(year, month)
    print(f"\n📈 RESUMEN DE {summary['month_name'].upper()} {year}:")
    print(f"   💰 Ingresos:  S/ {summary['total_income']:10.2f}")
    print(f"   💸 Gastos:    S/ {summary['total_expenses']:10.2f}")
    print(f"   💎 Ahorro:    S/ {summary['savings']:10.2f}")
    print(f"   📊 Tasa:      {summary['savings_rate']:10.1f}%")
    print(f"   🔢 Cantidad:  {summary['transaction_count']} transacciones")

    # 5. Verificar fechas
    print(f"\n🗓️  ANÁLISIS DE FECHAS:")
    print(f"   Fecha actual del sistema: {now.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"   Año actual: {year}")
    print(f"   Mes actual: {month} ({now.strftime('%B')})")

    if all_transactions:
        dates = [t.date for t in all_transactions]
        print(f"   Transacción más antigua: {min(dates).strftime('%d/%m/%Y')}")
        print(f"   Transacción más reciente: {max(dates).strftime('%d/%m/%Y')}")

        # Verificar si hay transacciones en el futuro
        future = [t for t in all_transactions if t.date > now]
        if future:
            print(
                f"   ⚠️  ADVERTENCIA: {len(future)} transacciones tienen fechas futuras!"
            )
            for t in future:
                print(f"      - {t.date.strftime('%d/%m/%Y %H:%M')} | {t.description}")

    # 6. Categorías
    print(f"\n🏷️  CATEGORÍAS:")
    expense_cats = db.get_all_categories("expense")
    income_cats = db.get_all_categories("income")

    print(f"   Gastos ({len(expense_cats)}):")
    for cat in expense_cats[:5]:  # Mostrar solo las primeras 5
        print(f"      {cat.icon} {cat.name} (ID: {cat.id})")

    print(f"   Ingresos ({len(income_cats)}):")
    for cat in income_cats[:5]:
        print(f"      {cat.icon} {cat.name} (ID: {cat.id})")

    # 7. Gastos por categoría del mes actual
    expenses_by_cat = db.get_expenses_by_category(year, month)
    if expenses_by_cat:
        print(f"\n💸 GASTOS POR CATEGORÍA (mes actual):")
        for item in expenses_by_cat:
            print(f"   {item['icon']} {item['category']:20} | S/ {item['total']:8.2f}")

    print("\n" + "=" * 60)
    print("✅ Diagnóstico completado")
    print("=" * 60)

    db.close()


if __name__ == "__main__":
    try:
        diagnose_database()
    except Exception as e:
        print(f"❌ Error durante el diagnóstico: {e}")
        import traceback
        traceback.print_exc()