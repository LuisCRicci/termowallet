"""
Categorizador Automático de Transacciones - CON SOPORTE PARA INGRESOS
Archivo: src/business/categorizer.py
"""

import re
from typing import Dict, List


class TransactionCategorizer:
    """Categoriza transacciones basándose en palabras clave en la descripción"""

    def __init__(self):
        # ✅ Diccionario de palabras clave para GASTOS
        self.expense_keywords = {
            "Alimentación": [
                "restaurant", "comida", "food","pizza","burger","cafe","cafeteria","supermercado","market",
                "panaderia","bakery", "almuerzo","lunch","cena","dinner","desayuno","breakfast","bar","pub",
                "mcdonalds", "kfc", "starbucks", "subway","pollo","chicken", "bebida","drink", "cerveza", "beer",
                "mercado","bodega","tienda","grocery","bembos","norky","china wok","delivery","papa rellena", 
                "cevicheria", "polleria", "hamburgueseria", "ceviche", "pollo a la brasa", "chifa", "hamburguesa",
                "sushi", "anticuchos" , "picanteria" , "empanadas" , "tamales", "churros",  "donas", "donuts", 
                "helados", "ice cream", "yogurt","frozen yogurt", "frutas","verduras","vegetales","carniceria",
                "butcher","picarones","chocolateria", "dulceria","snacks","antojitos", "chocolates", "golosinas",
                "chocolate" , "golosina", "snack" , "antojito", "salchipapa", "salchipapas", "empanada", "piqueo", 
                "piqueos","chifles","papas fritas","papas a la francesa", "chicharrones","nachos","hot dog","hotdog",
                "sandwich","sanguches", "chizitos","gaseosa","soda","refresco","refrescos", "jugo","juice","smoothie",
                "batido","agua","water","leche","milk","yogur", "metro", "wong", "tottus", "plaza vea", "mass"
            ],
            "Transporte": [
                "uber", "taxi","cabify","beat","gasolina","gas","petroleo", "grifo", "station", "parking",
                "estacionamiento", "peaje","toll","bus","metro","tren","train", "vuelo","flight", "avianca",
                "latam","transporte","transport","movilidad","pasaje", "ticket", "combustible", "fuel",
                "mecanico","mechanic","repuesto", "llanta", "tire","revision","tecnica"
            ],
            "Entretenimiento": [
                "cine","cinema","movie","netflix","spotify", "amazon prime", "disney", "hbo", "steam","playstation",
                "xbox","nintendo","juego", "game", "concierto","concert","teatro", "theater", "club","discoteca",
                "disco","bar","karaoke","bowling","gimnasio","gym","deporte","sport","entrada","ticket","suscripcion",
                "subscription","youtube","twitch",
            ],
            "Servicios": [
                "luz","electricity", "agua", "water","internet","telefono","phone","celular","mobile","cable",
                "tv","netflix","sedapal","enel","luz del sur","claro","movistar","entel","bitel","gas","natural",
                "mantenimiento","maintenance","reparacion","repair","limpieza","cleaning","lavanderia","laundry",
                "tintoreria","peluqueria","salon","barberia",
            ],
            "Salud": [
                "farmacia","pharmacy","doctor", "medico", "clinica", "clinic", "hospital", "dentista", "dentist",
                "odontologo", "medicina", "medicine", "pastilla", "pill", "vitamina", "vitamin", "laboratorio",
                "laboratory","analisis","examen","exam","consulta","consultation","terapia","therapy","inkafarma",
                "mifarma","botica","optica","lentes","glasses",
            ],
            "Educación": [
                "universidad","university","colegio","school","academia","institute","curso","course","clase",
                "class","libro","book","libreria","bookstore","capacitacion","training","certificacion","certification",
                "matricula","tuition","pension","mensualidad","cuota","estudios","tesis","materiales","utiles","supplies",
            ],
            "Vivienda": [
                "alquiler","rent","arrendamiento","inmobiliaria","casa","departamento","apartment","condominio",
                "mantenimiento", "reparacion", "pintura","paint","constructor","albanil","gasfitero","plumber",
                "electricista","electrician","ferreteria","hardware","mueble","furniture","decoracion",
            ],
            "Compras": [
                "ropa","clothes","zapateria","shoes","tienda","store","mall","plaza","boutique","zara","h&m","forever21",
                "saga","ripley", "falabella", "oechsle", "paris","amazon","ebay","mercadolibre","jockey","real plaza",
                "cosmetico","perfume","maquillaje","makeup","accesorio","accessory","reloj","watch","joya","jewelry",
                "regalo","gift",
            ],
            "Belleza": [
                "Cremas","clothes","zapateria","shoes","tienda","store","mall","plaza","boutique","zara","h&m","forever21",
                "saga","ripley", "falabella", "oechsle", "paris","amazon","ebay","mercadolibre","jockey","real plaza",
                "cosmetico","perfume","maquillaje","makeup","accesorio","accessory","reloj","watch","joya","jewelry",
                "regalo","gift",
            ],
            
            "Otros Gastos": [],  # Categoría por defecto para gastos
        }

        # ✅ NUEVO: Diccionario de palabras clave para INGRESOS
        self.income_keywords = {
            "Salario": [
                "salario", "sueldo", "salary", "pago", "nomina", "payroll", "planilla", "remuneracion",
                "quincena", "mensualidad", "pago mensual", "haberes", "emolumento", "stipend",
                "empresa", "company", "employer", "empleador", "trabajo", "work", "job",
                "aguinaldo", "gratificacion", "bonificacion", "bonus", "cts", "compensacion"
            ],
            "Freelance": [
                "freelance", "free lance", "independiente", "proyecto", "project", "consultoria",
                "consulting", "honorarios", "fee", "fees", "servicio", "service", "trabajo independiente",
                "contractor", "contrato", "cliente", "client", "factura", "invoice", "pago por proyecto",
                "diseño", "design", "desarrollo", "development", "programacion", "programming",
                "redaccion", "writing", "traduccion", "translation", "asesoría", "advisory"
            ],
            "Inversiones": [
                "inversion", "investment", "dividendo", "dividend", "interes", "interest", "rendimiento",
                "yield", "ganancia", "profit", "utilidad", "acciones", "stocks", "bolsa", "mercado",
                "fondo", "fund", "mutual", "etf", "bonos", "bonds", "cripto", "crypto", "bitcoin",
                "ethereum", "trading", "forex", "plusvalia", "renta", "pasiva", "passive income"
            ],
            "Otros Ingresos": [
                "venta", "sale", "sold", "vendido", "regalo", "gift", "donacion", "donation",
                "reembolso", "refund", "devolucion", "return", "reintegro", "cashback",
                "premio", "prize", "award", "ganancia", "loteria", "lottery", "rifa", "sorteo",
                "herencia", "inheritance", "pension", "retirement", "jubilacion", "alquiler",
                "renta", "rent", "arrendamiento", "prestamo", "loan", "transferencia", "transfer",
                "deposito", "deposit", "ingreso extra", "extra income", "propina", "tip",
                "comision", "commission", "incentivo", "incentive", "rebate", "descuento"
            ],
        }

        # ✅ Mantener compatibilidad con código antiguo
        self.keywords = self.expense_keywords

    def categorize(self, description: str, transaction_type: str = "expense") -> str:
        """
        Categoriza una transacción basándose en su descripción y tipo
        
        Args:
            description: Descripción de la transacción
            transaction_type: "expense" o "income"
            
        Returns: 
            Nombre de la categoría
        """
        if not description:
            return "Otros Ingresos" if transaction_type == "income" else "Otros Gastos"

        # Convertir a minúsculas y limpiar
        desc_lower = description.lower().strip()

        # ✅ Elegir el diccionario correcto según el tipo
        if transaction_type == "income":
            keywords_dict = self.income_keywords
            default_category = "Otros Ingresos"
        else:
            keywords_dict = self.expense_keywords
            default_category = "Otros Gastos"

        # Buscar coincidencias en cada categoría
        matches = {}
        for category, keywords in keywords_dict.items():
            if category in ["Otros", "Otros Gastos", "Otros Ingresos"]:
                continue

            # Contar cuántas keywords coinciden
            match_count = sum(1 for keyword in keywords if keyword in desc_lower)
            if match_count > 0:
                matches[category] = match_count

        # Retornar la categoría con más coincidencias
        if matches:
            return max(matches, key=lambda k: matches[k])

        return default_category

    def add_keyword(self, category: str, keyword: str, transaction_type: str = "expense"):
        """
        Añade una palabra clave a una categoría
        
        Args:
            category: Nombre de la categoría
            keyword: Palabra clave a añadir
            transaction_type: "expense" o "income"
        """
        keywords_dict = self.income_keywords if transaction_type == "income" else self.expense_keywords
        
        if category in keywords_dict:
            if keyword.lower() not in keywords_dict[category]:
                keywords_dict[category].append(keyword.lower())
    
    def remove_keyword(self, category: str, keyword: str, transaction_type: str = "expense") -> bool:
        """
        Elimina una palabra clave de una categoría
        
        Args:
            category: Nombre de la categoría
            keyword: Palabra clave a eliminar
            transaction_type: "expense" o "income"
            
        Returns:
            bool: True si se eliminó correctamente
        """
        keywords_dict = self.income_keywords if transaction_type == "income" else self.expense_keywords
        
        if category in keywords_dict:
            keyword_lower = keyword.lower()
            if keyword_lower in keywords_dict[category]:
                keywords_dict[category].remove(keyword_lower)
                return True
        return False
    
    def set_keywords(self, category: str, keywords: List[str], transaction_type: str = "expense"):
        """
        Establece todas las palabras clave de una categoría (reemplaza las existentes)
        
        Args:
            category: Nombre de la categoría
            keywords: Lista de palabras clave
            transaction_type: "expense" o "income"
        """
        keywords_dict = self.income_keywords if transaction_type == "income" else self.expense_keywords
        
        if category not in keywords_dict:
            keywords_dict[category] = []
        
        # Convertir todas a minúsculas y eliminar duplicados
        keywords_dict[category] = list(set([k.lower().strip() for k in keywords if k.strip()]))
    
    def get_keywords_for_category(self, category: str, transaction_type: str = "expense") -> List[str]:
        """
        Obtiene las palabras clave de una categoría específica
        
        Args:
            category: Nombre de la categoría
            transaction_type: "expense" o "income"
            
        Returns:
            Lista de palabras clave
        """
        keywords_dict = self.income_keywords if transaction_type == "income" else self.expense_keywords
        return keywords_dict.get(category, [])

    def get_categories(self, transaction_type: str = "expense") -> list:
        """
        Retorna la lista de categorías disponibles según el tipo
        
        Args:
            transaction_type: "expense" o "income"
            
        Returns:
            Lista de nombres de categorías
        """
        if transaction_type == "income":
            return list(self.income_keywords.keys())
        else:
            return list(self.expense_keywords.keys())

    def get_all_keywords(self, transaction_type: str = "expense") -> Dict[str, List[str]]:
        """
        Retorna el diccionario completo de palabras clave
        
        Args:
            transaction_type: "expense" o "income"
            
        Returns:
            Diccionario con categorías y sus palabras clave
        """
        return self.income_keywords if transaction_type == "income" else self.expense_keywords