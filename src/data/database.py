"""
Gestor de Base de Datos - VERSIÓN COMPLETA CON LIMPIEZA
Archivo: src/data/database.py
"""

from sqlalchemy import create_engine, func, extract
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import List, Optional, Dict
import os
import sys

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.data.models import Base, Category, Transaction, MonthlyBudget
from src.utils.config import Config


class DatabaseManager:
    """Gestor principal de la base de datos"""

    def __init__(self, db_path: Optional[str] = None):
        """Inicializa la conexión a la base de datos"""
        self.db_path = db_path or Config.get_db_path()
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # Inicializar categorías por defecto si es primera vez
        self._initialize_default_categories()
        
        # ✅ NUEVO: Inicializar palabras clave después de categorías
        self._initialize_default_keywords()
    
        print("✅ Base de datos inicializada con categorías y palabras clave")
        
        

    def _initialize_default_categories(self):
        """Crea categorías predeterminadas si no existen"""
        if self.session.query(Category).count() == 0:
            default_categories = [
                # Categorías de Gastos
                Category(
                    name="Alimentación",
                    icon="🍔",
                    color="#ef4444",
                    category_type="expense",
                    is_default=True,
                    description="Comida, restaurantes, supermercado",
                ),
                Category(
                    name="Transporte",
                    icon="🚗",
                    color="#f97316",
                    category_type="expense",
                    is_default=True,
                    description="Uber, gasolina, taxi, bus",
                ),
                Category(
                    name="Entretenimiento",
                    icon="🎮",
                    color="#a855f7",
                    category_type="expense",
                    is_default=True,
                    description="Cine, streaming, juegos",
                ),
                Category(
                    name="Servicios",
                    icon="💡",
                    color="#eab308",
                    category_type="expense",
                    is_default=True,
                    description="Luz, agua, internet, teléfono",
                ),
                Category(
                    name="Salud",
                    icon="⚕️",
                    color="#22c55e",
                    category_type="expense",
                    is_default=True,
                    description="Farmacia, doctor, clínica",
                ),
                Category(
                    name="Educación",
                    icon="📚",
                    color="#3b82f6",
                    category_type="expense",
                    is_default=True,
                    description="Cursos, libros, universidad",
                ),
                Category(
                    name="Vivienda",
                    icon="🏠",
                    color="#84cc16",
                    category_type="expense",
                    is_default=True,
                    description="Alquiler, reparaciones, mantenimiento",
                ),
                Category(
                    name="Compras",
                    icon="🛍️",
                    color="#ec4899",
                    category_type="expense",
                    is_default=True,
                    description="Ropa, zapatos, accesorios",
                ),
                Category(
                    name="Otros Gastos",
                    icon="💸",
                    color="#6b7280",
                    category_type="expense",
                    is_default=True,
                    description="Gastos varios",
                ),
                # Categorías de Ingresos
                Category(
                    name="Salario",
                    icon="💰",
                    color="#10b981",
                    category_type="income",
                    is_default=True,
                    description="Sueldo mensual",
                ),
                Category(
                    name="Freelance",
                    icon="💼",
                    color="#06b6d4",
                    category_type="income",
                    is_default=True,
                    description="Trabajos independientes",
                ),
                Category(
                    name="Inversiones",
                    icon="📈",
                    color="#8b5cf6",
                    category_type="income",
                    is_default=True,
                    description="Dividendos, intereses",
                ),
                Category(
                    name="Otros Ingresos",
                    icon="💵",
                    color="#14b8a6",
                    category_type="income",
                    is_default=True,
                    description="Ingresos varios",
                ),
            ]

            self.session.add_all(default_categories)
            self.session.commit()

    """
    AGREGAR ESTOS MÉTODOS A DatabaseManager EN database.py
    Insertar después del método _initialize_default_categories() (línea ~115)
    """

    def _initialize_default_keywords(self):
        """
        ✅ ACTUALIZADO: Inicializa palabras clave por defecto en categorías predeterminadas
        Se ejecuta automáticamente después de crear las categorías
        """
        # Diccionario de palabras clave por defecto para GASTOS
        default_expense_keywords = {
            "Alimentación": [
                "restaurant", "comida", "food", "pizza", "burger", "cafe", "cafeteria",
                "supermercado", "market", "panaderia", "bakery", "almuerzo", "lunch",
                "cena", "dinner", "desayuno", "breakfast", "bar", "pub", "mcdonalds",
                "kfc", "starbucks", "subway", "pollo", "chicken", "bebida", "drink",
                "cerveza", "beer", "mercado", "bodega", "tienda", "grocery", "bembos",
                "norky", "china wok", "delivery", "papa rellena", "cevicheria",
                "polleria", "hamburgueseria", "ceviche", "pollo a la brasa", "chifa",
                "hamburguesa", "sushi", "anticuchos", "picanteria", "empanadas",
                "tamales", "churros", "donas", "donuts", "helados", "ice cream",
                "yogurt", "frozen yogurt", "frutas", "verduras", "vegetales",
                "carniceria", "butcher", "picarones", "chocolateria", "dulceria",
                "snacks", "antojitos", "chocolates", "golosinas", "chocolate",
                "golosina", "snack", "antojito", "salchipapa", "salchipapas",
                "empanada", "piqueo", "piqueos", "chifles", "papas fritas",
                "papas a la francesa", "chicharrones", "nachos", "hot dog", "hotdog",
                "sandwich", "sanguches", "chizitos", "gaseosa", "soda", "refresco",
                "refrescos", "jugo", "juice", "smoothie", "batido", "agua", "water",
                "leche", "milk", "yogur", "metro", "wong", "tottus", "plaza vea", "mass"
            ],
            "Transporte": [
                "uber", "taxi", "cabify", "beat", "gasolina", "gas", "petroleo",
                "grifo", "station", "parking", "estacionamiento", "peaje", "toll",
                "bus", "metro", "tren", "train", "vuelo", "flight", "avianca",
                "latam", "transporte", "transport", "movilidad", "pasaje", "ticket",
                "combustible", "fuel", "mecanico", "mechanic", "repuesto", "llanta",
                "tire", "revision", "tecnica"
            ],
            "Entretenimiento": [
                "cine", "cinema", "movie", "netflix", "spotify", "amazon prime",
                "disney", "hbo", "steam", "playstation", "xbox", "nintendo", "juego",
                "game", "concierto", "concert", "teatro", "theater", "club",
                "discoteca", "disco", "bar", "karaoke", "bowling", "gimnasio", "gym",
                "deporte", "sport", "entrada", "ticket", "suscripcion",
                "subscription", "youtube", "twitch"
            ],
            "Servicios": [
                "luz", "electricity", "agua", "water", "internet", "telefono",
                "phone", "celular", "mobile", "cable", "tv", "netflix", "sedapal",
                "enel", "luz del sur", "claro", "movistar", "entel", "bitel", "gas",
                "natural", "mantenimiento", "maintenance", "reparacion", "repair",
                "limpieza", "cleaning", "lavanderia", "laundry", "tintoreria",
                "peluqueria", "salon", "barberia"
            ],
            "Salud": [
                "farmacia", "pharmacy", "doctor", "medico", "clinica", "clinic",
                "hospital", "dentista", "dentist", "odontologo", "medicina",
                "medicine", "pastilla", "pill", "vitamina", "vitamin", "laboratorio",
                "laboratory", "analisis", "examen", "exam", "consulta",
                "consultation", "terapia", "therapy", "inkafarma", "mifarma",
                "botica", "optica", "lentes", "glasses"
            ],
            "Educación": [
                "universidad", "university", "colegio", "school", "academia",
                "institute", "curso", "course", "clase", "class", "libro", "book",
                "libreria", "bookstore", "capacitacion", "training", "certificacion",
                "certification", "matricula", "tuition", "pension", "mensualidad",
                "cuota", "estudios", "tesis", "materiales", "utiles", "supplies"
            ],
            "Vivienda": [
                "alquiler", "rent", "arrendamiento", "inmobiliaria", "casa",
                "departamento", "apartment", "condominio", "mantenimiento",
                "reparacion", "pintura", "paint", "constructor", "albanil",
                "gasfitero", "plumber", "electricista", "electrician", "ferreteria",
                "hardware", "mueble", "furniture", "decoracion"
            ],
            "Compras": [
                "ropa", "clothes", "zapateria", "shoes", "tienda", "store", "mall",
                "plaza", "boutique", "zara", "h&m", "forever21", "saga", "ripley",
                "falabella", "oechsle", "paris", "amazon", "ebay", "mercadolibre",
                "jockey", "real plaza", "cosmetico", "perfume", "maquillaje",
                "makeup", "accesorio", "accessory", "reloj", "watch", "joya",
                "jewelry", "regalo", "gift"
            ],
            "Otros Gastos": []
        }
        
        # Diccionario de palabras clave por defecto para INGRESOS
        default_income_keywords = {
            "Salario": [
                "salario", "sueldo", "salary", "pago", "nomina", "payroll",
                "planilla", "remuneracion", "quincena", "mensualidad",
                "pago mensual", "haberes", "emolumento", "stipend", "empresa",
                "company", "employer", "empleador", "trabajo", "work", "job",
                "aguinaldo", "gratificacion", "bonificacion", "bonus", "cts",
                "compensacion"
            ],
            "Freelance": [
                "freelance", "free lance", "independiente", "proyecto", "project",
                "consultoria", "consulting", "honorarios", "fee", "fees",
                "servicio", "service", "trabajo independiente", "contractor",
                "contrato", "cliente", "client", "factura", "invoice",
                "pago por proyecto", "diseño", "design", "desarrollo",
                "development", "programacion", "programming", "redaccion",
                "writing", "traduccion", "translation", "asesoria", "advisory"
            ],
            "Inversiones": [
                "inversion", "investment", "dividendo", "dividend", "interes",
                "interest", "rendimiento", "yield", "ganancia", "profit",
                "utilidad", "acciones", "stocks", "bolsa", "mercado", "fondo",
                "fund", "mutual", "etf", "bonos", "bonds", "cripto", "crypto",
                "bitcoin", "ethereum", "trading", "forex", "plusvalia", "renta",
                "pasiva", "passive income"
            ],
            "Otros Ingresos": [
                "venta", "sale", "sold", "vendido", "regalo", "gift", "donacion",
                "donation", "reembolso", "refund", "devolucion", "return",
                "reintegro", "cashback", "premio", "prize", "award", "ganancia",
                "loteria", "lottery", "rifa", "sorteo", "herencia", "inheritance",
                "pension", "retirement", "jubilacion", "alquiler", "renta", "rent",
                "arrendamiento", "prestamo", "loan", "transferencia", "transfer",
                "deposito", "deposit", "ingreso extra", "extra income", "propina",
                "tip", "comision", "commission", "incentivo", "incentive", "rebate",
                "descuento"
            ]
        }
        
        try:
            # Obtener todas las categorías predeterminadas
            default_categories = self.session.query(Category).filter(
                Category.is_default == True
            ).all()
            
            updated_count = 0
            
            for category in default_categories:
                # ✅ CORRECCIÓN: Solo actualizar si NO tiene keywords O si están vacías
                current_keywords = category.get_keywords_list()
                
                # Determinar qué diccionario usar según el tipo
                if category.category_type == "income":
                    keywords_dict = default_income_keywords
                else:
                    keywords_dict = default_expense_keywords
                
                # Si la categoría existe en el diccionario y no tiene keywords válidas
                if category.name in keywords_dict and len(current_keywords) == 0:
                    category.set_keywords_list(keywords_dict[category.name])
                    updated_count += 1
                    print(f"  ✅ Keywords asignadas a: {category.name}")
            
            if updated_count > 0:
                self.session.commit()
                print(f"✅ {updated_count} categorías actualizadas con palabras clave por defecto")
            else:
                print("ℹ️  Las categorías ya tienen palabras clave asignadas")
            
        except Exception as e:
            print(f"⚠️ Error al inicializar palabras clave: {e}")
            self.session.rollback()

    
    
    def restore_default_keywords(self, category_id: Optional[int] = None) -> Dict:
        """
        ✅ NUEVO: Restaura palabras clave predeterminadas
        
        Args:
            category_id: ID de categoría específica, o None para todas
            
        Returns:
            Dict con resultado: {
                "success": bool,
                "updated_count": int,
                "categories_updated": List[str],
                "message": str
            }
        """
        # Diccionarios de palabras clave por defecto (mismo que en _initialize_default_keywords)
        default_expense_keywords = {
            "Alimentación": [
                "restaurant", "comida", "food", "pizza", "burger", "cafe", "cafeteria",
                "supermercado", "market", "panaderia", "bakery", "almuerzo", "lunch",
                "cena", "dinner", "desayuno", "breakfast", "bar", "pub", "mcdonalds",
                "kfc", "starbucks", "subway", "pollo", "chicken", "bebida", "drink",
                "cerveza", "beer", "mercado", "bodega", "tienda", "grocery", "bembos",
                "norky", "china wok", "delivery", "papa rellena", "cevicheria",
                "polleria", "hamburgueseria", "ceviche", "pollo a la brasa", "chifa",
                "hamburguesa", "sushi", "anticuchos", "picanteria", "empanadas",
                "tamales", "churros", "donas", "donuts", "helados", "ice cream",
                "yogurt", "frozen yogurt", "frutas", "verduras", "vegetales",
                "carniceria", "butcher", "picarones", "chocolateria", "dulceria",
                "snacks", "antojitos", "chocolates", "golosinas", "chocolate",
                "golosina", "snack", "antojito", "salchipapa", "salchipapas",
                "empanada", "piqueo", "piqueos", "chifles", "papas fritas",
                "papas a la francesa", "chicharrones", "nachos", "hot dog", "hotdog",
                "sandwich", "sanguches", "chizitos", "gaseosa", "soda", "refresco",
                "refrescos", "jugo", "juice", "smoothie", "batido", "agua", "water",
                "leche", "milk", "yogur", "metro", "wong", "tottus", "plaza vea", "mass"
            ],
            "Transporte": [
                "uber", "taxi", "cabify", "beat", "gasolina", "gas", "petroleo",
                "grifo", "station", "parking", "estacionamiento", "peaje", "toll",
                "bus", "metro", "tren", "train", "vuelo", "flight", "avianca",
                "latam", "transporte", "transport", "movilidad", "pasaje", "ticket",
                "combustible", "fuel", "mecanico", "mechanic", "repuesto", "llanta",
                "tire", "revision", "tecnica"
            ],
            "Entretenimiento": [
                "cine", "cinema", "movie", "netflix", "spotify", "amazon prime",
                "disney", "hbo", "steam", "playstation", "xbox", "nintendo", "juego",
                "game", "concierto", "concert", "teatro", "theater", "club",
                "discoteca", "disco", "bar", "karaoke", "bowling", "gimnasio", "gym",
                "deporte", "sport", "entrada", "ticket", "suscripcion",
                "subscription", "youtube", "twitch"
            ],
            "Servicios": [
                "luz", "electricity", "agua", "water", "internet", "telefono",
                "phone", "celular", "mobile", "cable", "tv", "netflix", "sedapal",
                "enel", "luz del sur", "claro", "movistar", "entel", "bitel", "gas",
                "natural", "mantenimiento", "maintenance", "reparacion", "repair",
                "limpieza", "cleaning", "lavanderia", "laundry", "tintoreria",
                "peluqueria", "salon", "barberia"
            ],
            "Salud": [
                "farmacia", "pharmacy", "doctor", "medico", "clinica", "clinic",
                "hospital", "dentista", "dentist", "odontologo", "medicina",
                "medicine", "pastilla", "pill", "vitamina", "vitamin", "laboratorio",
                "laboratory", "analisis", "examen", "exam", "consulta",
                "consultation", "terapia", "therapy", "inkafarma", "mifarma",
                "botica", "optica", "lentes", "glasses"
            ],
            "Educación": [
                "universidad", "university", "colegio", "school", "academia",
                "institute", "curso", "course", "clase", "class", "libro", "book",
                "libreria", "bookstore", "capacitacion", "training", "certificacion",
                "certification", "matricula", "tuition", "pension", "mensualidad",
                "cuota", "estudios", "tesis", "materiales", "utiles", "supplies"
            ],
            "Vivienda": [
                "alquiler", "rent", "arrendamiento", "inmobiliaria", "casa",
                "departamento", "apartment", "condominio", "mantenimiento",
                "reparacion", "pintura", "paint", "constructor", "albanil",
                "gasfitero", "plumber", "electricista", "electrician", "ferreteria",
                "hardware", "mueble", "furniture", "decoracion"
            ],
            "Compras": [
                "ropa", "clothes", "zapateria", "shoes", "tienda", "store", "mall",
                "plaza", "boutique", "zara", "h&m", "forever21", "saga", "ripley",
                "falabella", "oechsle", "paris", "amazon", "ebay", "mercadolibre",
                "jockey", "real plaza", "cosmetico", "perfume", "maquillaje",
                "makeup", "accesorio", "accessory", "reloj", "watch", "joya",
                "jewelry", "regalo", "gift"
            ],
            "Otros Gastos": []
        }
        
        default_income_keywords = {
            "Salario": [
                "salario", "sueldo", "salary", "pago", "nomina", "payroll",
                "planilla", "remuneracion", "quincena", "mensualidad",
                "pago mensual", "haberes", "emolumento", "stipend", "empresa",
                "company", "employer", "empleador", "trabajo", "work", "job",
                "aguinaldo", "gratificacion", "bonificacion", "bonus", "cts",
                "compensacion"
            ],
            "Freelance": [
                "freelance", "free lance", "independiente", "proyecto", "project",
                "consultoria", "consulting", "honorarios", "fee", "fees",
                "servicio", "service", "trabajo independiente", "contractor",
                "contrato", "cliente", "client", "factura", "invoice",
                "pago por proyecto", "diseño", "design", "desarrollo",
                "development", "programacion", "programming", "redaccion",
                "writing", "traduccion", "translation", "asesoria", "advisory"
            ],
            "Inversiones": [
                "inversion", "investment", "dividendo", "dividend", "interes",
                "interest", "rendimiento", "yield", "ganancia", "profit",
                "utilidad", "acciones", "stocks", "bolsa", "mercado", "fondo",
                "fund", "mutual", "etf", "bonos", "bonds", "cripto", "crypto",
                "bitcoin", "ethereum", "trading", "forex", "plusvalia", "renta",
                "pasiva", "passive income"
            ],
            "Otros Ingresos": [
                "venta", "sale", "sold", "vendido", "regalo", "gift", "donacion",
                "donation", "reembolso", "refund", "devolucion", "return",
                "reintegro", "cashback", "premio", "prize", "award", "ganancia",
                "loteria", "lottery", "rifa", "sorteo", "herencia", "inheritance",
                "pension", "retirement", "jubilacion", "alquiler", "renta", "rent",
                "arrendamiento", "prestamo", "loan", "transferencia", "transfer",
                "deposito", "deposit", "ingreso extra", "extra income", "propina",
                "tip", "comision", "commission", "incentivo", "incentive", "rebate",
                "descuento"
            ]
        }
        
        try:
            updated_count = 0
            categories_updated = []
            
            # Determinar qué categorías procesar
            if category_id:
                # Restaurar una categoría específica
                category = self.get_category_by_id(category_id)
                if not category:
                    return {
                        "success": False,
                        "updated_count": 0,
                        "categories_updated": [],
                        "message": "Categoría no encontrada"
                    }
                
                if not category.is_default:
                    return {
                        "success": False,
                        "updated_count": 0,
                        "categories_updated": [],
                        "message": "Solo se pueden restaurar categorías predeterminadas"
                    }
                
                categories_to_process = [category]
            else:
                # Restaurar todas las categorías predeterminadas
                categories_to_process = self.session.query(Category).filter(
                    Category.is_default == True
                ).all()
            
            # Procesar categorías
            for category in categories_to_process:
                # Determinar qué diccionario usar
                if category.category_type == "income":
                    keywords_dict = default_income_keywords
                else:
                    keywords_dict = default_expense_keywords
                
                # Si la categoría existe en el diccionario de defaults
                if category.name in keywords_dict:
                    # Restaurar keywords (sobrescribir las actuales)
                    category.set_keywords_list(keywords_dict[category.name])
                    updated_count += 1
                    categories_updated.append(category.name)
                    print(f"  🔄 Keywords restauradas: {category.name}")
            
            if updated_count > 0:
                self.session.commit()
                message = f"✅ {updated_count} categoría(s) restaurada(s) correctamente"
            else:
                message = "ℹ️ No hay categorías para restaurar"
            
            return {
                "success": True,
                "updated_count": updated_count,
                "categories_updated": categories_updated,
                "message": message
            }
            
        except Exception as e:
            print(f"❌ Error al restaurar keywords: {e}")
            self.session.rollback()
            return {
                "success": False,
                "updated_count": 0,
                "categories_updated": [],
                "message": f"Error: {str(e)}"
            }

    
    
    
    
    # ========== LIMPIEZA DE BASE DE DATOS ==========

    def clear_all_transactions(self) -> bool:
        """Elimina TODAS las transacciones de la base de datos"""
        try:
            self.session.query(Transaction).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error al limpiar transacciones: {e}")
            return False

    def clear_custom_categories(self) -> bool:
        """Elimina SOLO las categorías personalizadas (mantiene las predeterminadas)"""
        try:
            self.session.query(Category).filter(Category.is_default == False).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error al limpiar categorías personalizadas: {e}")
            return False

    def reset_database(self) -> bool:
        """Resetea completamente la base de datos (transacciones + categorías personalizadas)"""
        try:
            # Eliminar transacciones
            self.session.query(Transaction).delete()
            # Eliminar categorías personalizadas
            self.session.query(Category).filter(Category.is_default == False).delete()
            # Eliminar presupuestos
            self.session.query(MonthlyBudget).delete()
            
            # ✅ NUEVO: Limpiar palabras clave de categorías predeterminadas
            default_categories = self.session.query(Category).filter(
                Category.is_default == True
            ).all()
            
            for category in default_categories:
                category.keywords = None  # Limpiar palabras clave existentes
            
            self.session.commit()
            
            # ✅ NUEVO: Re-inicializar palabras clave por defecto
            self._initialize_default_keywords()
            
            print("✅ Base de datos reseteada y palabras clave reinicializadas")
            return True
            
        except Exception as e:
            print(f"❌ Error al resetear base de datos: {e}")
            self.session.rollback()

    def get_database_stats(self) -> Dict:
        """Obtiene estadísticas de la base de datos"""
        try:
            return {
                "total_transactions": self.session.query(Transaction).count(),
                "total_categories": self.session.query(Category).count(),
                "custom_categories": self.session.query(Category)
                .filter(Category.is_default == False)
                .count(),
                "default_categories": self.session.query(Category)
                .filter(Category.is_default == True)
                .count(),
                "total_expenses": self.session.query(func.sum(Transaction.amount))
                .filter(Transaction.transaction_type == "expense")
                .scalar()
                or 0.0,
                "total_income": self.session.query(func.sum(Transaction.amount))
                .filter(Transaction.transaction_type == "income")
                .scalar()
                or 0.0,
            }
        except Exception as e:
            print(f"Error al obtener estadísticas: {e}")
            return {}

    # ========== TRANSACCIONES ==========

    def add_transaction(
        self,
        date: datetime,
        description: str,
        amount: float,
        category_id: int,
        transaction_type: str,
        notes: Optional[str] = None,
        source: str = "manual",
        original_description: Optional[str] = None,
    ) -> Transaction:
        """Añade una nueva transacción"""
        transaction = Transaction(
            date=date,
            description=description,
            amount=amount,
            category_id=category_id,
            transaction_type=transaction_type,
            notes=notes,
            source=source,
            original_description=original_description,
        )

        self.session.add(transaction)
        self.session.commit()
        return transaction

    def add_transactions_bulk(self, transactions_data: List[Dict]) -> int:
        """Añade múltiples transacciones de una vez"""
        count = 0
        for data in transactions_data:
            try:
                self.add_transaction(**data)
                count += 1
            except Exception as e:
                print(f"Error al añadir transacción: {e}")
                continue

        return count

    def get_all_transactions(self) -> List[Transaction]:
        """Obtiene todas las transacciones ordenadas por fecha descendente"""
        return self.session.query(Transaction).order_by(Transaction.date.desc()).all()

    def get_transactions_by_month(self, year: int, month: int) -> List[Transaction]:
        """Obtiene transacciones de un mes específico"""
        return (
            self.session.query(Transaction)
            .filter(
                extract("year", Transaction.date) == year,
                extract("month", Transaction.date) == month,
            )
            .order_by(Transaction.date.desc())
            .all()
        )

    def get_transactions_by_type(
        self,
        transaction_type: str,
        year: Optional[int] = None,
        month: Optional[int] = None,
    ) -> List[Transaction]:
        """Obtiene transacciones por tipo (expense/income)"""
        query = self.session.query(Transaction).filter(
            Transaction.transaction_type == transaction_type
        )

        if year and month:
            query = query.filter(
                extract("year", Transaction.date) == year,
                extract("month", Transaction.date) == month,
            )

        return query.order_by(Transaction.date.desc()).all()

    def delete_transaction(self, transaction_id: int) -> bool:
        """Elimina una transacción"""
        transaction = (
            self.session.query(Transaction)
            .filter(Transaction.id == transaction_id)
            .first()
        )

        if transaction:
            self.session.delete(transaction)
            self.session.commit()
            return True
        return False

    def update_transaction(
            self,
            transaction_id: int,
            date: datetime,
            description: str,
            amount: float,
            category_id: int,
            notes: str = "",
        ) -> bool:
            """
            Actualiza una transacción existente.
            
            Args:
                transaction_id: ID de la transacción a actualizar
                date: Nueva fecha
                description: Nueva descripción
                amount: Nuevo monto
                category_id: Nuevo ID de categoría
                notes: Nuevas notas
                
            Returns:
                bool: True si se actualizó correctamente
            """
            try:
                # Buscar la transacción
                transaction = self.session.query(Transaction).filter_by(id=transaction_id).first()
                
                if not transaction:
                    print(f"❌ Transacción {transaction_id} no encontrada")
                    return False
                
                # Actualizar campos
                transaction.date = date
                transaction.description = description
                transaction.amount = amount
                transaction.category_id = category_id
                transaction.notes = notes
                transaction.updated_at = datetime.now()
                
                # Guardar cambios
                self.session.commit()
                print(f"✅ Transacción {transaction_id} actualizada correctamente")
                return True
                
            except Exception as e:
                self.session.rollback()
                print(f"❌ Error al actualizar transacción: {e}")
                import traceback
                traceback.print_exc()
                return False


    # ========== CATEGORÍAS ==========

    def get_all_categories(self, category_type: Optional[str] = None) -> List[Category]:
        """Obtiene todas las categorías, opcionalmente filtradas por tipo"""
        query = self.session.query(Category)

        if category_type:
            query = query.filter(Category.category_type == category_type)

        return query.order_by(Category.name).all()

    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Obtiene una categoría por ID"""
        return self.session.query(Category).filter(Category.id == category_id).first()

    def get_category_by_name(
        self, name: str, category_type: str = "expense"
    ) -> Optional[Category]:
        """Obtiene una categoría por nombre"""
        return (
            self.session.query(Category)
            .filter(Category.name == name, Category.category_type == category_type)
            .first()
        )

    def add_category(
        self,
        name: str,
        icon: str,
        color: str,
        category_type: str = "expense",
        description: Optional[str] = None,
    ) -> Category:
        """Añade una nueva categoría"""
        category = Category(
            name=name,
            icon=icon,
            color=color,
            category_type=category_type,
            description=description,
            is_default=False,
        )

        self.session.add(category)
        self.session.commit()
        return category

    def update_category(self, category_id: int, **kwargs) -> Optional[Category]:
        """Actualiza una categoría"""
        category = self.get_category_by_id(category_id)

        if category:
            for key, value in kwargs.items():
                if hasattr(category, key):
                    setattr(category, key, value)

            self.session.commit()
            return category

        return None

    def delete_category(self, category_id: int) -> bool:
        """Elimina una categoría (solo si no es predeterminada)"""
        category = self.get_category_by_id(category_id)

        if category and category.is_default is False:
            self.session.delete(category)
            self.session.commit()
            return True
        return False

    # ========== ANÁLISIS Y REPORTES ==========

    def get_monthly_summary(self, year: int, month: int) -> Dict:
        """Obtiene resumen financiero del mes"""
        # Ingresos totales
        total_income = (
            self.session.query(func.sum(Transaction.amount))
            .filter(
                Transaction.transaction_type == "income",
                extract("year", Transaction.date) == year,
                extract("month", Transaction.date) == month,
            )
            .scalar()
            or 0.0
        )

        # Gastos totales
        total_expenses = (
            self.session.query(func.sum(Transaction.amount))
            .filter(
                Transaction.transaction_type == "expense",
                extract("year", Transaction.date) == year,
                extract("month", Transaction.date) == month,
            )
            .scalar()
            or 0.0
        )

        # Cálculos
        savings = total_income - total_expenses
        savings_rate = (savings / total_income * 100) if total_income > 0 else 0

        return {
            "year": year,
            "month": month,
            "month_name": datetime(year, month, 1).strftime("%B"),
            "total_income": total_income,
            "total_expenses": total_expenses,
            "savings": savings,
            "savings_rate": savings_rate,
            "transaction_count": self.session.query(Transaction)
            .filter(
                extract("year", Transaction.date) == year,
                extract("month", Transaction.date) == month,
            )
            .count(),
        }

    def get_expenses_by_category(self, year: int, month: int) -> List[Dict]:
        """Obtiene gastos agrupados por categoría"""
        results = (
            self.session.query(
                Category.name,
                Category.icon,
                Category.color,
                func.sum(Transaction.amount).label("total"),
            )
            .join(Transaction)
            .filter(
                Transaction.transaction_type == "expense",
                extract("year", Transaction.date) == year,
                extract("month", Transaction.date) == month,
            )
            .group_by(Category.id)
            .order_by(func.sum(Transaction.amount).desc())
            .all()
        )

        return [
            {
                "category": r.name,
                "icon": r.icon,
                "color": r.color,
                "total": float(r.total),
            }
            for r in results
        ]

    def get_income_by_category(self, year: int, month: int) -> List[Dict]:
        """Obtiene ingresos agrupados por categoría"""
        results = (
            self.session.query(
                Category.name,
                Category.icon,
                Category.color,
                func.sum(Transaction.amount).label("total"),
            )
            .join(Transaction)
            .filter(
                Transaction.transaction_type == "income",
                extract("year", Transaction.date) == year,
                extract("month", Transaction.date) == month,
            )
            .group_by(Category.id)
            .order_by(func.sum(Transaction.amount).desc())
            .all()
        )

        return [
            {
                "category": r.name,
                "icon": r.icon,
                "color": r.color,
                "total": float(r.total),
            }
            for r in results
        ]

    def get_monthly_trend(self, months: int = 6) -> List[Dict]:
        """Obtiene tendencia de ingresos/gastos de los últimos N meses"""
        results = []
        current_date = datetime.now()

        for i in range(months):
            year = current_date.year
            month = current_date.month - i

            if month <= 0:
                month += 12
                year -= 1

            summary = self.get_monthly_summary(year, month)
            results.append(summary)

        return list(reversed(results))

    """
    NUEVOS MÉTODOS PARA AGREGAR A: src/data/database.py
    Agregar estos métodos dentro de la clase DatabaseManager, 
    justo antes del método close() al final del archivo
    """

    def get_top_expenses(self, year: int, month: int, limit: int = 5) -> List[Dict]:
        """Obtiene los gastos más grandes del mes"""
        results = (
            self.session.query(Transaction, Category)
            .join(Category)
            .filter(
                Transaction.transaction_type == "expense",
                extract("year", Transaction.date) == year,
                extract("month", Transaction.date) == month,
            )
            .order_by(Transaction.amount.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "description": t.description,
                "amount": float(t.amount),
                "date": t.date,
                "category_name": c.name,
                "category_icon": c.icon,
                "category_color": c.color,
            }
            for t, c in results
        ]

    def get_daily_average(self, year: int, month: int) -> Dict:
        """Calcula el promedio de gasto diario del mes"""
        from calendar import monthrange

        total_expenses = (
            self.session.query(func.sum(Transaction.amount))
            .filter(
                Transaction.transaction_type == "expense",
                extract("year", Transaction.date) == year,
                extract("month", Transaction.date) == month,
            )
            .scalar()
            or 0.0
        )

        # Obtener días del mes
        days_in_month = monthrange(year, month)[1]

        # Obtener día actual si es el mes actual
        now = datetime.now()
        if year == now.year and month == now.month:
            days_passed = now.day
        else:
            days_passed = days_in_month

        daily_avg = total_expenses / days_passed if days_passed > 0 else 0
        projected_total = daily_avg * days_in_month

        return {
            "total_expenses": total_expenses,
            "days_passed": days_passed,
            "days_in_month": days_in_month,
            "daily_average": daily_avg,
            "projected_monthly": projected_total,
        }

    def get_week_comparison(self, year: int, month: int) -> Dict:
        """Compara el gasto de esta semana con la semana pasada"""
        from datetime import timedelta

        now = datetime.now()

        # Semana actual (últimos 7 días)
        week_start = now - timedelta(days=7)
        current_week_total = (
            self.session.query(func.sum(Transaction.amount))
            .filter(
                Transaction.transaction_type == "expense",
                Transaction.date >= week_start,
                Transaction.date <= now,
            )
            .scalar()
            or 0.0
        )

        # Semana anterior (días 8-14 atrás)
        prev_week_start = now - timedelta(days=14)
        prev_week_end = now - timedelta(days=7)
        previous_week_total = (
            self.session.query(func.sum(Transaction.amount))
            .filter(
                Transaction.transaction_type == "expense",
                Transaction.date >= prev_week_start,
                Transaction.date < prev_week_end,
            )
            .scalar()
            or 0.0
        )

        # Calcular cambio porcentual
        if previous_week_total > 0:
            change_pct = (
                (current_week_total - previous_week_total) / previous_week_total
            ) * 100
        else:
            change_pct = 0 if current_week_total == 0 else 100

        return {
            "current_week": current_week_total,
            "previous_week": previous_week_total,
            "change_amount": current_week_total - previous_week_total,
            "change_percentage": change_pct,
            "is_increasing": current_week_total > previous_week_total,
        }

    def get_category_budget_status(self, year: int, month: int) -> List[Dict]:
        """Obtiene el estado de gasto por categoría con límites sugeridos"""
        expenses = self.get_expenses_by_category(year, month)

        # Límites sugeridos por categoría (% del total)
        suggested_limits = {
            "Alimentación": 30,
            "Transporte": 15,
            "Vivienda": 30,
            "Entretenimiento": 10,
            "Servicios": 10,
            "Salud": 5,
            "Educación": 10,
            "Compras": 15,
            "Otros Gastos": 5,
        }

        if not expenses:
            return []

        total = sum(e["total"] for e in expenses)

        result = []
        for expense in expenses:
            cat_name = expense["category"]
            suggested_pct = suggested_limits.get(cat_name, 10)
            suggested_amount = total * (suggested_pct / 100)
            actual_pct = (expense["total"] / total * 100) if total > 0 else 0

            result.append(
                {
                    "category": cat_name,
                    "icon": expense["icon"],
                    "color": expense["color"],
                    "spent": expense["total"],
                    "suggested_limit": suggested_amount,
                    "percentage": actual_pct,
                    "suggested_percentage": suggested_pct,
                    "is_over_budget": actual_pct
                    > (suggested_pct * 1.1),  # 10% de margen
                    "budget_health": (
                        "good"
                        if actual_pct <= suggested_pct
                        else (
                            "warning" if actual_pct <= suggested_pct * 1.2 else "danger"
                        )
                    ),
                }
            )

        return result

    def get_spending_trend_last_days(self, days: int = 7) -> List[Dict]:
        """Obtiene el gasto de los últimos N días para graficar tendencia"""
        from datetime import timedelta

        now = datetime.now()
        results = []

        for i in range(days):
            target_date = now - timedelta(days=days - i - 1)

            daily_total = (
                self.session.query(func.sum(Transaction.amount))
                .filter(
                    Transaction.transaction_type == "expense",
                    func.date(Transaction.date) == target_date.date(),
                )
                .scalar()
                or 0.0
            )

            results.append(
                {
                    "date": target_date.date(),
                    "day_name": target_date.strftime("%a"),
                    "amount": float(daily_total),
                }
            )

        return results

    def get_transaction_count_by_type(self, year: int, month: int) -> Dict:
        """Obtiene el conteo de transacciones por tipo"""
        expense_count = (
            self.session.query(func.count(Transaction.id))
            .filter(
                Transaction.transaction_type == "expense",
                extract("year", Transaction.date) == year,
                extract("month", Transaction.date) == month,
            )
            .scalar()
            or 0
        )

        income_count = (
            self.session.query(func.count(Transaction.id))
            .filter(
                Transaction.transaction_type == "income",
                extract("year", Transaction.date) == year,
                extract("month", Transaction.date) == month,
            )
            .scalar()
            or 0
        )

        return {
            "total": expense_count + income_count,
            "expenses": expense_count,
            "income": income_count,
        }
        
    # ========== AGREGAR ESTOS MÉTODOS A DatabaseManager EN database.py ==========
    # Agregar después de los métodos existentes, antes del método close()

    def get_monthly_budget(self, year: int, month: int) -> Optional[MonthlyBudget]:
        """Obtiene el presupuesto de un mes específico"""
        return (
            self.session.query(MonthlyBudget)
            .filter(MonthlyBudget.year == year, MonthlyBudget.month == month)
            .first()
        )


    def get_all_budgets(self) -> List[MonthlyBudget]:
        """Obtiene todos los presupuestos ordenados por fecha descendente"""
        return (
            self.session.query(MonthlyBudget)
            .order_by(MonthlyBudget.year.desc(), MonthlyBudget.month.desc())
            .all()
        )


    def create_or_update_budget(
        self,
        year: int,
        month: int,
        income_goal: float = 0.0,
        expense_limit: float = 0.0,
        savings_goal: float = 0.0,
        notes: Optional[str] = None,
    ) -> MonthlyBudget:
        """Crea o actualiza el presupuesto de un mes"""
        budget = self.get_monthly_budget(year, month)

        if budget:
            # Actualizar existente
            budget.income_goal = income_goal
            budget.expense_limit = expense_limit
            budget.savings_goal = savings_goal
            budget.notes = notes
            budget.updated_at = datetime.now()
        else:
            # Crear nuevo
            budget = MonthlyBudget(
                year=year,
                month=month,
                income_goal=income_goal,
                expense_limit=expense_limit,
                savings_goal=savings_goal,
                notes=notes,
            )
            self.session.add(budget)

        self.session.commit()
        return budget


    def delete_budget(self, year: int, month: int) -> bool:
        """Elimina un presupuesto mensual"""
        budget = self.get_monthly_budget(year, month)
        if budget:
            self.session.delete(budget)
            self.session.commit()
            return True
        return False


    def get_budget_status(self, year: int, month: int) -> Dict:
        """
        Obtiene el estado actual del presupuesto comparado con lo real.
        
        Returns:
            Dict con comparación entre presupuesto y realidad:
            - budget_exists (bool)
            - income_goal, expense_limit, savings_goal (float)
            - actual_income, actual_expenses, actual_savings (float)
            - income_progress, expense_progress, savings_progress (float) %
            - is_under_budget (bool)
            - days_left (int)
        """
        from calendar import monthrange

        budget = self.get_monthly_budget(year, month)
        summary = self.get_monthly_summary(year, month)

        # Calcular días restantes
        now = datetime.now()
        if year == now.year and month == now.month:
            days_in_month = monthrange(year, month)[1]
            days_left = days_in_month - now.day
        else:
            days_left = 0

        if not budget:
            return {
                "budget_exists": False,
                "income_goal": 0.0,
                "expense_limit": 0.0,
                "savings_goal": 0.0,
                "actual_income": summary["total_income"],
                "actual_expenses": summary["total_expenses"],
                "actual_savings": summary["savings"],
                "income_progress": 0.0,
                "expense_progress": 0.0,
                "savings_progress": 0.0,
                "is_under_budget": True,
                "days_left": days_left,
                "notes": None,
            }

        # Calcular progreso
        income_progress = (
            (summary["total_income"] / budget.income_goal * 100)
            if budget.income_goal > 0
            else 0
        )

        expense_progress = (
            (summary["total_expenses"] / budget.expense_limit * 100)
            if budget.expense_limit > 0
            else 0
        )

        savings_progress = (
            (summary["savings"] / budget.savings_goal * 100)
            if budget.savings_goal > 0
            else 0
        )

        is_under_budget = (
            summary["total_expenses"] <= budget.expense_limit
            if budget.expense_limit > 0
            else True
        )

        return {
            "budget_exists": True,
            "income_goal": budget.income_goal,
            "expense_limit": budget.expense_limit,
            "savings_goal": budget.savings_goal,
            "actual_income": summary["total_income"],
            "actual_expenses": summary["total_expenses"],
            "actual_savings": summary["savings"],
            "income_progress": income_progress,
            "expense_progress": expense_progress,
            "savings_progress": savings_progress,
            "is_under_budget": is_under_budget,
            "days_left": days_left,
            "notes": budget.notes,
            "expense_remaining": budget.expense_limit - summary["total_expenses"],
            "savings_remaining": budget.savings_goal - summary["savings"],
        }


    def get_budget_alerts(self, year: int, month: int) -> List[Dict]:
        """
        Genera alertas sobre el estado del presupuesto.
        
        Returns:
            Lista de diccionarios con alertas:
            - type (str): "warning", "danger", "success"
            - message (str): Mensaje de la alerta
            - icon (str): Ícono sugerido
        """
        status = self.get_budget_status(year, month)
        alerts = []

        if not status["budget_exists"]:
            alerts.append({
                "type": "info",
                "message": "No has configurado un presupuesto para este mes",
                "icon": "💡",
            })
            return alerts

        # Alerta de gastos
        if status["expense_progress"] >= 100:
            alerts.append({
                "type": "danger",
                "message": f"¡Has excedido tu límite de gastos en {status['expense_progress'] - 100:.1f}%!",
                "icon": "🚨",
            })
        elif status["expense_progress"] >= 90:
            alerts.append({
                "type": "warning",
                "message": f"Estás al {status['expense_progress']:.1f}% de tu límite de gastos",
                "icon": "⚠️",
            })
        elif status["expense_progress"] >= 75:
            alerts.append({
                "type": "warning",
                "message": f"Has usado el {status['expense_progress']:.1f}% de tu presupuesto",
                "icon": "📊",
            })

        # Alerta de ahorros
        if status["savings_goal"] > 0:
            if status["savings_progress"] >= 100:
                alerts.append({
                    "type": "success",
                    "message": f"¡Felicidades! Alcanzaste tu meta de ahorro",
                    "icon": "🎉",
                })
            elif status["savings_progress"] >= 75:
                alerts.append({
                    "type": "success",
                    "message": f"Llevas {status['savings_progress']:.1f}% de tu meta de ahorro",
                    "icon": "💰",
                })
            elif status["savings_progress"] < 30 and status["days_left"] < 10:
                alerts.append({
                    "type": "warning",
                    "message": f"Solo llevas {status['savings_progress']:.1f}% de tu meta de ahorro y quedan {status['days_left']} días",
                    "icon": "⏰",
                })

        # Alerta de ingresos
        if status["income_goal"] > 0 and status["income_progress"] < 50 and status["days_left"] < 15:
            alerts.append({
                "type": "info",
                "message": f"Llevas {status['income_progress']:.1f}% de tu meta de ingresos",
                "icon": "📈",
            })

        return alerts


    def get_budget_history(self, months: int = 6) -> List[Dict]:
        """Obtiene el historial de presupuestos y su cumplimiento"""
        results = []
        current_date = datetime.now()

        for i in range(months):
            year = current_date.year
            month = current_date.month - i

            if month <= 0:
                month += 12
                year -= 1

            status = self.get_budget_status(year, month)
            status["year"] = year
            status["month"] = month
            status["month_name"] = datetime(year, month, 1).strftime("%B %Y")

            results.append(status)

        return results

    def close(self):
        """Cierra la conexión a la base de datos"""
        self.session.close()
