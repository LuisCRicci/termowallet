"""
Script para diagnosticar la base de datos de TermoWallet - ACTUALIZADO
Ejecutar con: python tests/debug_db.py
"""

import sys
import os
from datetime import datetime

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.database import DatabaseManager


def diagnose_database():
    """Diagnostica el estado de la base de datos"""
    db = DatabaseManager()

    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE BASE DE DATOS - TermoWallet v2.0")
    print("=" * 60)

    # 1. Estadísticas generales
    stats = db.get_database_stats()
    print("\n📊 ESTADÍSTICAS GENERALES:")
    print(f"   Total de transacciones: {stats.get('total_transactions', 0)}")
    print(f"   Total de categorías: {stats.get('total_categories', 0)}")
    print(f"   Categorías personalizadas: {stats.get('custom_categories', 0)}")
    print(f"   Ingresos totales: S/ {stats.get('total_income', 0):.2f}")
    print(f"   Gastos totales: S/ {stats.get('total_expenses', 0):.2f}")

    # ✅ NUEVO: 2. Verificación de keywords
    print("\n🔑 SISTEMA DE PALABRAS CLAVE:")
    all_categories = db.get_all_categories()
    
    categories_with_keywords = []
    categories_without_keywords = []
    total_keywords = 0
    
    for cat in all_categories:
        keywords = cat.get_keywords_list()
        total_keywords += len(keywords)
        
        if len(keywords) > 0:
            categories_with_keywords.append((cat.name, len(keywords)))
        else:
            categories_without_keywords.append(cat.name)
    
    print(f"   Categorías con keywords: {len(categories_with_keywords)}/{len(all_categories)}")
    print(f"   Total de palabras clave: {total_keywords}")
    
    if categories_with_keywords:
        print("\n   📝 Top 5 categorías por keywords:")
        sorted_cats = sorted(categories_with_keywords, key=lambda x: x[1], reverse=True)[:5]
        for cat_name, count in sorted_cats:
            print(f"      • {cat_name}: {count} keywords")
    
    if categories_without_keywords:
        print(f"\n   ⚠️  Categorías sin keywords: {', '.join(categories_without_keywords)}")

    # 3. Todas las transacciones
    all_transactions = db.get_all_transactions()
    print(f"\n📝 TODAS LAS TRANSACCIONES ({len(all_transactions)}):")

    if len(all_transactions) == 0:
        print("   ℹ️  No hay transacciones registradas")
    else:
        for t in all_transactions[:10]:  # Mostrar solo las primeras 10
            tipo = "💰" if t.transaction_type == "income" else "💸"
            fecha = t.date.strftime("%d/%m/%Y")
            category = db.get_category_by_id(t.category_id)
            cat_name = category.name if category else "Sin categoría"
            print(
                f"   {tipo} {fecha} | {t.description[:30]:30} | S/ {t.amount:8.2f} | {cat_name}"
            )
        
        if len(all_transactions) > 10:
            print(f"   ... y {len(all_transactions) - 10} transacciones más")

    # 4. Transacciones por mes actual
    now = datetime.now()
    year = now.year
    month = now.month

    print(f"\n📅 TRANSACCIONES DE {now.strftime('%B %Y').upper()}:")
    monthly_trans = db.get_transactions_by_month(year, month)
    print(f"   Total: {len(monthly_trans)} transacciones")

    if monthly_trans:
        expense_count = sum(1 for t in monthly_trans if t.transaction_type == "expense")
        income_count = sum(1 for t in monthly_trans if t.transaction_type == "income")
        print(f"   💸 Gastos: {expense_count} | 💰 Ingresos: {income_count}")
        
        for t in monthly_trans[:5]:  # Mostrar solo las primeras 5
            tipo = "💰" if t.transaction_type == "income" else "💸"
            fecha = t.date.strftime("%d/%m/%Y %H:%M")
            category = db.get_category_by_id(t.category_id)
            cat_name = category.name if category else "Sin categoría"
            print(
                f"   {tipo} {fecha} | {t.description[:25]:25} | S/ {t.amount:8.2f} | {cat_name}"
            )
    else:
        print("   ℹ️  No hay transacciones en este mes")

    # 5. Resumen mensual
    summary = db.get_monthly_summary(year, month)
    print(f"\n📈 RESUMEN DE {summary['month_name'].upper()} {year}:")
    print(f"   💰 Ingresos:  S/ {summary['total_income']:10.2f}")
    print(f"   💸 Gastos:    S/ {summary['total_expenses']:10.2f}")
    print(f"   💎 Ahorro:    S/ {summary['savings']:10.2f}")
    print(f"   📊 Tasa:      {summary['savings_rate']:10.1f}%")
    print(f"   🔢 Cantidad:  {summary['transaction_count']} transacciones")

    # 6. Verificar fechas
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
            for t in future[:3]:
                print(f"      - {t.date.strftime('%d/%m/%Y %H:%M')} | {t.description}")

    # 7. Categorías
    print(f"\n🏷️  CATEGORÍAS:")
    expense_cats = db.get_all_categories("expense")
    income_cats = db.get_all_categories("income")

    print(f"   💸 Gastos ({len(expense_cats)}):")
    for cat in expense_cats[:5]:  # Mostrar solo las primeras 5
        keywords_count = len(cat.get_keywords_list())
        keyword_info = f"({keywords_count} keywords)" if keywords_count > 0 else "(sin keywords)"
        print(f"      {cat.icon} {cat.name} {keyword_info} (ID: {cat.id})")
    
    if len(expense_cats) > 5:
        print(f"      ... y {len(expense_cats) - 5} categorías más")

    print(f"   💰 Ingresos ({len(income_cats)}):")
    for cat in income_cats:
        keywords_count = len(cat.get_keywords_list())
        keyword_info = f"({keywords_count} keywords)" if keywords_count > 0 else "(sin keywords)"
        print(f"      {cat.icon} {cat.name} {keyword_info} (ID: {cat.id})")

    # 8. Gastos por categoría del mes actual
    expenses_by_cat = db.get_expenses_by_category(year, month)
    if expenses_by_cat:
        print(f"\n💸 GASTOS POR CATEGORÍA (mes actual):")
        for item in expenses_by_cat:
            print(f"   {item['icon']} {item['category']:20} | S/ {item['total']:8.2f}")

    # ✅ NUEVO: 9. Presupuesto del mes
    budget_status = db.get_budget_status(year, month)
    print(f"\n💼 PRESUPUESTO DEL MES:")
    
    if budget_status["budget_exists"]:
        print(f"   ✅ Presupuesto configurado")
        print(f"   Meta de ingresos:  S/ {budget_status['income_goal']:.2f}")
        print(f"   Límite de gastos:  S/ {budget_status['expense_limit']:.2f}")
        print(f"   Meta de ahorro:    S/ {budget_status['savings_goal']:.2f}")
        print(f"\n   Progreso:")
        print(f"   💰 Ingresos:  {budget_status['income_progress']:.1f}%")
        print(f"   💸 Gastos:    {budget_status['expense_progress']:.1f}%")
        print(f"   💎 Ahorros:   {budget_status['savings_progress']:.1f}%")
        
        if budget_status["expense_progress"] >= 100:
            print(f"   ⚠️  ¡Has excedido tu límite de gastos!")
        elif budget_status["expense_progress"] >= 90:
            print(f"   ⚠️  Estás cerca de tu límite de gastos")
    else:
        print("   ℹ️  No hay presupuesto configurado para este mes")

    # ✅ NUEVO: 10. Test de categorización
    print(f"\n🧪 TEST DE CATEGORIZACIÓN:")
    from src.business.categorizer import TransactionCategorizer
    
    categorizer = TransactionCategorizer()
    db.load_keywords_to_categorizer(categorizer)
    
    test_descriptions = [
        ("Compra en Wong", "expense"),
        ("Uber a casa", "expense"),
        ("Netflix suscripción", "expense"),
        ("Salario mensual", "income"),
    ]
    
    for desc, tipo in test_descriptions:
        category_name = categorizer.categorize(desc, tipo)
        tipo_emoji = "💸" if tipo == "expense" else "💰"
        print(f"   {tipo_emoji} '{desc}' → {category_name}")

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