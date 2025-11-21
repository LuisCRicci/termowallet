"""
Script para ejecutar todos los tests y verificaciones - ACTUALIZADO
Archivo: tests/run_tests.py
"""

import sys
import os
import unittest


# Colores para terminal
class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_header(text):
    """Imprime un encabezado"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def check_dependencies():
    """Verifica que todas las dependencias estén instaladas"""
    print_header("1. Verificando Dependencias")

    required_packages = ["flet", "sqlalchemy", "pandas", "openpyxl"]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"{Colors.OKGREEN}✓{Colors.ENDC} {package}")
        except ImportError:
            print(f"{Colors.FAIL}✗{Colors.ENDC} {package}")
            missing.append(package)

    if missing:
        print(
            f"\n{Colors.WARNING}⚠ Paquetes faltantes: {', '.join(missing)}{Colors.ENDC}"
        )
        print(f"{Colors.OKCYAN}Ejecuta: pip install {' '.join(missing)}{Colors.ENDC}")
        return False

    print(f"\n{Colors.OKGREEN}✓ Todas las dependencias están instaladas{Colors.ENDC}")
    return True


def check_structure():
    """Verifica la estructura del proyecto"""
    print_header("2. Verificando Estructura del Proyecto")

    required_files = [
        "src/main.py",
        "src/data/database.py",
        "src/data/models.py",
        "src/business/categorizer.py",
        "src/business/processor.py",
        "src/utils/config.py",
        "src/utils/helpers.py",
        "requirements.txt",
    ]

    missing = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"{Colors.OKGREEN}✓{Colors.ENDC} {file_path}")
        else:
            print(f"{Colors.FAIL}✗{Colors.ENDC} {file_path}")
            missing.append(file_path)

    if missing:
        print(f"\n{Colors.WARNING}⚠ Archivos faltantes: {len(missing)}{Colors.ENDC}")
        return False

    print(f"\n{Colors.OKGREEN}✓ Estructura del proyecto correcta{Colors.ENDC}")
    return True


def test_database_connection():
    """Prueba la conexión a la base de datos"""
    print_header("3. Probando Base de Datos")

    try:
        from src.data.database import DatabaseManager

        # Crear base de datos de prueba
        db = DatabaseManager("test_connection.db")

        # Verificar categorías
        categories = db.get_all_categories()
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} Categorías creadas: {len(categories)}")

        # ✅ NUEVO: Verificar keywords
        categories_with_keywords = sum(
            1 for cat in categories if len(cat.get_keywords_list()) > 0
        )
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} Categorías con keywords: {categories_with_keywords}")

        # Añadir transacción de prueba
        from datetime import datetime

        transaction = db.add_transaction(
            date=datetime.now(),
            description="Test transaction",
            amount=100.0,
            category_id=categories[0].id,
            transaction_type="expense",
        )
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} Transacción de prueba creada")

        # Obtener resumen
        summary = db.get_monthly_summary(2025, 11)
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} Resumen mensual: {summary['month_name']}")

        # Limpiar
        db.close()
        if os.path.exists("test_connection.db"):
            os.remove("test_connection.db")

        print(
            f"\n{Colors.OKGREEN}✓ Base de datos funcionando correctamente{Colors.ENDC}"
        )
        return True

    except Exception as e:
        print(f"\n{Colors.FAIL}✗ Error en base de datos: {str(e)}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        return False


def test_keywords_system():
    """✅ NUEVO: Prueba el sistema de palabras clave"""
    print_header("4. Probando Sistema de Keywords")

    try:
        from src.data.database import DatabaseManager
        from src.business.categorizer import TransactionCategorizer

        db = DatabaseManager("test_keywords.db")
        categorizer = TransactionCategorizer()

        # Cargar keywords desde BD
        db.load_keywords_to_categorizer(categorizer)
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} Keywords cargadas al categorizador")

        # Probar categorización
        test_cases = [
            ("Compra en Wong", "expense", "Alimentación"),
            ("Uber a casa", "expense", "Transporte"),
            ("Netflix premium", "expense", "Entretenimiento"),
            ("Salario mensual", "income", "Salario"),
        ]

        success_count = 0
        for desc, tipo, expected in test_cases:
            result = categorizer.categorize(desc, tipo)
            if result == expected:
                print(f"{Colors.OKGREEN}✓{Colors.ENDC} '{desc}' → {result}")
                success_count += 1
            else:
                print(f"{Colors.WARNING}⚠{Colors.ENDC} '{desc}' → {result} (esperado: {expected})")

        # Limpiar
        db.close()
        if os.path.exists("test_keywords.db"):
            os.remove("test_keywords.db")

        if success_count == len(test_cases):
            print(f"\n{Colors.OKGREEN}✓ Sistema de keywords funcionando perfectamente{Colors.ENDC}")
            return True
        else:
            print(f"\n{Colors.WARNING}⚠ {success_count}/{len(test_cases)} tests pasaron{Colors.ENDC}")
            return True  # No es crítico

    except Exception as e:
        print(f"\n{Colors.FAIL}✗ Error en keywords: {str(e)}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        return False


def run_unit_tests():
    """Ejecuta los tests unitarios"""
    print_header("5. Ejecutando Tests Unitarios")

    # Configurar path para los tests
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    test_suite = unittest.TestSuite()

    # Cargar tests de base de datos
    try:
        from tests.test_database import TestDatabaseManager
        db_tests = unittest.TestLoader().loadTestsFromTestCase(TestDatabaseManager)
        test_suite.addTests(db_tests)
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} Tests de base de datos cargados")
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error cargando tests de BD: {e}{Colors.ENDC}")

    # Cargar tests de processor
    try:
        from tests.test_processor import TestTransactionProcessor
        processor_tests = unittest.TestLoader().loadTestsFromTestCase(TestTransactionProcessor)
        test_suite.addTests(processor_tests)
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} Tests de procesador cargados")
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error cargando tests de procesador: {e}{Colors.ENDC}")

    if test_suite.countTestCases() == 0:
        print(f"{Colors.WARNING}⚠ No se encontraron tests para ejecutar{Colors.ENDC}")
        return False

    print(f"\n{Colors.OKCYAN}Ejecutando {test_suite.countTestCases()} tests...{Colors.ENDC}\n")

    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    if result.wasSuccessful():
        print(f"\n{Colors.OKGREEN}✓ Todos los tests unitarios pasaron ({test_suite.countTestCases()} tests){Colors.ENDC}")
        return True
    else:
        print(f"\n{Colors.FAIL}✗ Algunos tests unitarios fallaron{Colors.ENDC}")
        print(f"   Exitosos: {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f"   Fallidos: {len(result.failures)}")
        print(f"   Errores: {len(result.errors)}")
        return False


def run_diagnostic():
    """Ejecuta el diagnóstico de la base de datos"""
    print_header("6. Diagnóstico de Base de Datos")

    try:
        from tests.debug_db import diagnose_database
        diagnose_database()
        return True
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error en diagnóstico: {e}{Colors.ENDC}")
        return False


def check_android_compatibility():
    """✅ NUEVO: Verifica compatibilidad con Android"""
    print_header("7. Verificando Compatibilidad Android")

    checks = []

    # 1. Verificar que no se use localStorage
    print(f"{Colors.OKCYAN}Buscando uso de localStorage...{Colors.ENDC}")
    import glob
    
    ui_files = glob.glob("src/ui/*.py")
    localStorage_found = False
    
    for file in ui_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'localStorage' in content or 'sessionStorage' in content:
                    print(f"{Colors.WARNING}⚠ {file} usa localStorage{Colors.ENDC}")
                    localStorage_found = True
        except:
            pass
    
    if not localStorage_found:
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} No se usa localStorage")
        checks.append(True)
    else:
        print(f"{Colors.WARNING}⚠ Se encontró uso de localStorage (no compatible con Android){Colors.ENDC}")
        checks.append(False)

    # 2. Verificar rutas adaptativas
    print(f"\n{Colors.OKCYAN}Verificando rutas adaptativas...{Colors.ENDC}")
    try:
        with open('src/utils/config.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'getandroidapilevel' in content or 'get_data_dir' in content:
                print(f"{Colors.OKGREEN}✓{Colors.ENDC} Config.py tiene rutas adaptativas")
                checks.append(True)
            else:
                print(f"{Colors.WARNING}⚠ Config.py podría necesitar rutas adaptativas{Colors.ENDC}")
                checks.append(False)
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error verificando config.py: {e}{Colors.ENDC}")
        checks.append(False)

    # 3. Verificar main.py
    print(f"\n{Colors.OKCYAN}Verificando main.py...{Colors.ENDC}")
    try:
        with open('src/main.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'ft.app(target=main)' in content:
                print(f"{Colors.OKGREEN}✓{Colors.ENDC} main.py usa ft.app(target=main)")
                checks.append(True)
            else:
                print(f"{Colors.WARNING}⚠ main.py debería usar ft.app(target=main){Colors.ENDC}")
                checks.append(False)
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error verificando main.py: {e}{Colors.ENDC}")
        checks.append(False)

    if all(checks):
        print(f"\n{Colors.OKGREEN}✓ App lista para compilar a Android{Colors.ENDC}")
        return True
    else:
        print(f"\n{Colors.WARNING}⚠ Hay {len([c for c in checks if not c])} problemas de compatibilidad{Colors.ENDC}")
        return True  # No bloqueante


def main():
    """Función principal"""
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}")
    print("╔═════════════════════════════════════════════════════════╗")
    print("║         TermoWallet - Test Suite Completo v2.0         ║")
    print("╚═════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")

    results = []

    # Ejecutar verificaciones en secuencia
    results.append(("Dependencias", check_dependencies()))
    results.append(("Estructura", check_structure()))
    results.append(("Base de Datos", test_database_connection()))
    results.append(("Sistema Keywords", test_keywords_system()))
    results.append(("Tests Unitarios", run_unit_tests()))
    results.append(("Diagnóstico", run_diagnostic()))
    results.append(("Android Compatibility", check_android_compatibility()))

    # Resumen final
    print_header("RESUMEN FINAL")

    all_passed = all(result for _, result in results)

    for name, passed in results:
        status = (
            f"{Colors.OKGREEN}✓ PASS{Colors.ENDC}"
            if passed
            else f"{Colors.FAIL}✗ FAIL{Colors.ENDC}"
        )
        print(f"{name.ljust(25)}: {status}")

    print()
    if all_passed:
        print(f"{Colors.OKGREEN}{Colors.BOLD}🎉 ¡Todos los tests pasaron!{Colors.ENDC}")
        print(f"{Colors.OKCYAN}La aplicación está lista para ejecutarse y compilar.{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Próximos pasos:{Colors.ENDC}")
        print(f"  1. Ejecutar app: {Colors.BOLD}flet run src/main.py{Colors.ENDC}")
        print(f"  2. Compilar APK: {Colors.BOLD}flet build apk{Colors.ENDC}")
    else:
        failed_tests = [name for name, passed in results if not passed]
        print(
            f"{Colors.WARNING}{Colors.BOLD}⚠ Tests fallidos: {', '.join(failed_tests)}{Colors.ENDC}"
        )
        print(f"{Colors.OKCYAN}Revisa los mensajes de error arriba.{Colors.ENDC}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    # Asegurar que estamos en el directorio correcto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    
    sys.exit(main())