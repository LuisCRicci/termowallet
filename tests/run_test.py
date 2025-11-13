"""
Script para ejecutar todos los tests y verificaciones
Archivo: tests/run_tests.py
"""

import sys
import os
import unittest
import subprocess


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


def print_step(step_num, description):
    """Imprime un paso del proceso"""
    print(f"{Colors.OKCYAN}[Paso {step_num}] {description}{Colors.ENDC}")


def check_dependencies():
    """Verifica que todas las dependencias estén instaladas"""
    print_header("1. Verificando Dependencias")

    required_packages = ["flet", "sqlalchemy", "pandas", "plotly", "openpyxl"]

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
        "README.md",
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
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} Resumen mensual obtenido")

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
        return False


def run_diagnostic():
    """Ejecuta el diagnóstico de la base de datos"""
    print_header("4. Diagnóstico de Base de Datos")

    try:
        # Ejecutar debug_db.py como módulo
        from debug_db import diagnose_database

        diagnose_database()
        return True
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error en diagnóstico: {e}{Colors.ENDC}")
        return False


def run_unit_tests():
    """Ejecuta los tests unitarios"""
    print_header("5. Ejecutando Tests Unitarios")

    # Configurar path para los tests
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Descubrir y ejecutar tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)

    if not os.path.exists(start_dir):
        print(f"{Colors.WARNING}⚠ Directorio de tests no encontrado{Colors.ENDC}")
        return False

    # Cargar tests específicos
    test_suite = unittest.TestSuite()

    # Cargar tests de base de datos
    try:
        from test_database import TestDatabaseManager

        db_tests = loader.loadTestsFromTestCase(TestDatabaseManager)
        test_suite.addTests(db_tests)
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} Tests de base de datos cargados")
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error cargando tests de BD: {e}{Colors.ENDC}")

    # Cargar tests de processor
    try:
        from test_processor import TestTransactionProcessor

        processor_tests = loader.loadTestsFromTestCase(TestTransactionProcessor)
        test_suite.addTests(processor_tests)
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} Tests de procesador cargados")
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error cargando tests de procesador: {e}{Colors.ENDC}")

    if test_suite.countTestCases() == 0:
        print(f"{Colors.WARNING}⚠ No se encontraron tests para ejecutar{Colors.ENDC}")
        return False

    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    if result.wasSuccessful():
        print(f"\n{Colors.OKGREEN}✓ Todos los tests unitarios pasaron{Colors.ENDC}")
        return True
    else:
        print(f"\n{Colors.FAIL}✗ Algunos tests unitarios fallaron{Colors.ENDC}")
        return False


def main():
    """Función principal"""
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║         TermoWallet - Ejecutor de Tests Completo         ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")

    results = []

    # Ejecutar verificaciones en secuencia
    results.append(("Dependencias", check_dependencies()))
    results.append(("Estructura", check_structure()))
    results.append(("Base de Datos", test_database_connection()))
    results.append(("Diagnóstico", run_diagnostic()))
    results.append(("Tests Unitarios", run_unit_tests()))

    # Resumen final
    print_header("RESUMEN FINAL")

    all_passed = all(result for _, result in results)

    for name, passed in results:
        status = (
            f"{Colors.OKGREEN}✓ PASS{Colors.ENDC}"
            if passed
            else f"{Colors.FAIL}✗ FAIL{Colors.ENDC}"
        )
        print(f"{name.ljust(20)}: {status}")

    print()
    if all_passed:
        print(f"{Colors.OKGREEN}{Colors.BOLD}🎉 ¡Todos los tests pasaron!{Colors.ENDC}")
        print(f"{Colors.OKCYAN}La aplicación está lista para ejecutarse.{Colors.ENDC}")
        print(f"\nEjecutar con: {Colors.BOLD}flet run src/main.py{Colors.ENDC}")
    else:
        failed_tests = [name for name, passed in results if not passed]
        print(
            f"{Colors.WARNING}{Colors.BOLD}⚠ Tests fallidos: {', '.join(failed_tests)}{Colors.ENDC}"
        )
        print(f"{Colors.OKCYAN}Revisa los mensajes de error arriba.{Colors.ENDC}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    # Asegurar que estamos en el directorio correcto
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.exit(main())
