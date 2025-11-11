"""
Script para ejecutar tests y verificar la instalación
Archivo: run_tests.py
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
    print_header("Verificando Dependencias")

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
    print_header("Verificando Estructura del Proyecto")

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


def run_unit_tests():
    """Ejecuta los tests unitarios"""
    print_header("Ejecutando Tests Unitarios")

    # Descubrir y ejecutar tests
    loader = unittest.TestLoader()
    start_dir = "tests"

    if not os.path.exists(start_dir):
        print(f"{Colors.WARNING}⚠ Directorio de tests no encontrado{Colors.ENDC}")
        return False

    suite = loader.discover(start_dir)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print(f"\n{Colors.OKGREEN}✓ Todos los tests pasaron exitosamente{Colors.ENDC}")
        return True
    else:
        print(f"\n{Colors.FAIL}✗ Algunos tests fallaron{Colors.ENDC}")
        return False


def test_database_connection():
    """Prueba la conexión a la base de datos"""
    print_header("Probando Base de Datos")

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


def main():
    """Función principal"""
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║         TermoWallet - Sistema de Verificación            ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")

    results = []

    # Ejecutar verificaciones
    results.append(("Dependencias", check_dependencies()))
    results.append(("Estructura", check_structure()))
    results.append(("Base de Datos", test_database_connection()))

    # Preguntar si ejecutar tests unitarios
    print(
        f"\n{Colors.OKCYAN}¿Deseas ejecutar los tests unitarios? (s/n):{Colors.ENDC} ",
        end="",
    )
    response = input().lower()

    if response == "s":
        results.append(("Tests Unitarios", run_unit_tests()))

    # Resumen final
    print_header("Resumen de Verificación")

    all_passed = True
    for name, passed in results:
        status = (
            f"{Colors.OKGREEN}✓ PASS{Colors.ENDC}"
            if passed
            else f"{Colors.FAIL}✗ FAIL{Colors.ENDC}"
        )
        print(f"{name.ljust(20)}: {status}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print(
            f"{Colors.OKGREEN}{Colors.BOLD}🎉 ¡Todo está listo! Puedes ejecutar la aplicación con:{Colors.ENDC}"
        )
        print(f"{Colors.OKCYAN}   flet run src/main.py{Colors.ENDC}\n")
    else:
        print(
            f"{Colors.WARNING}{Colors.BOLD}⚠ Hay problemas que resolver antes de ejecutar{Colors.ENDC}\n"
        )

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
