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
                "aceite de cocina", "acelga (criolla/serrana)", "agua", "aguaje", "aji amarillo seco", 
                "aji escabeche fresco", "aji montaña", "aji paprika", "aji rocoto", "ajo", 
                "ajo criollo", "ajo morado", "albahaca", "albaricoque", "alcachofa", "almuerzo", 
                "antojito", "antojitos", "apio", "arroz", "arveja verde", "atun", "azúcar", 
                "bakery", "bases en sobre", "batido", "bebida", "beber", "bembos", "berenjena", 
                "beterraga", "bodega", "brocoli", "butcher", "caigua", "camote", "camu camu", 
                "carambola", "carne de res", "carniceria", "cebolla", "cebolla china", "cereales", 
                "chifles", "chirimoya", "chizitos", "chocolate", "chocolateria", 
                "chocolates", "chocolates y dulces", "choclo", "chuño", "ciruela", "coco", 
                "cocona", "col china", "col corazon", "coliflor", "comida", "coronta de maíz", 
                "culantro", "drink", "dulceria", "empanada", "esparrago fresco", "especias", 
                "espinaca", "fideos", "food", "frejol", "frejolito chino", "fresa", "frijol", 
                "frijol verde", "frozen yogurt", "frutas", "frutas tropicales", "galletas", 
                "galletas dulces", "galletas saladas", "gaseosa", "golosina", "golosinas", 
                "granadilla", "granada", "guanabana", "grocery", "haba verde", "harina", 
                "hierba buena", "higo", "holantau", "horganica", "hortalizas", "hortalizas de fruto", 
                "hortalizas de hoja o de tallo", "hortalizas de raíz", "hortalizas leguminosas verdes", 
                "hot dog", "hotdog", "huacatay", "huevos", "juice", "jugo", "kion", "kiwi", 
                "leche", "lechuga americana (criolla/serrana)", "lechuga criolla seda", 
                "lechuga romana hidropónica", "lenteja", "lima", "limon", "longapa", "lunch", 
                "lúcuma", "maiz marlo", "maiz morado", "mamey", "mandarina", "mango", "manzana", 
                "maracuyá", "market", "mass", "membrillo", "melon", "melon coquito", "melones", 
                "melocotón", "mercado", "metro", "milk", "nabo", "nachos", "naranja", "nueces", 
                "olluco", "pacchoy", "palta", "pallar verde", "panaderia", "panes y derivados", 
                "papa", "papa fritas", "papas a la francesa", "papas fritas", "papaya", "pepinillo", 
                "pepino", "pera", "perejil", "pescado", "picarones", "pimiento", "piqueo", 
                "piqueos", "piña", "platano", "plaza vea", "pollo", "poro", "rabanito", "refresco", 
                "refrescos", "restaurant", "salchipapa", "salchipapas", "salsas", "sandwich", 
                "sanguches", "sandia", "sazonadores", "smoothie", "snack", "snacks", "soda", 
                "spaguetti", "supermercado", "tamarindo", "tienda", "tomate", "toronja", "tottus", 
                "tuna", "uva", "vainita", "vegetales", "verduras", "water", "wong", "yacon", 
                "yogur", "yogurt", "yuca", "zapallo", "zapallo italiano", "zapallo loche", 
                "zapallo macre", "zanahoria"
            ],
            "Transporte": [
                "uber", "taxi", "cabify","beat", "gasolina", "gas", "petroleo",
                "grifo", "station", "parking", "estacionamiento", "peaje", "toll",
                "bus", "metro", "tren", "train", "vuelo", "flight", "avianca",
                "latam", "transporte", "transport", "movilidad", "pasaje", "ticket",
                "combustible", "fuel", "mecanico", "mechanic", "repuesto", "llanta",
                "tire", "revision", "tecnica" , "Metropolitano" 
            ],
            "Entretenimiento": [
                "cine", "cinema", "movie", "netflix", "spotify", "amazon prime",
                "disney", "hbo", "steam", "playstation", "xbox", "nintendo", "juego",
                "game", "concierto", "concert", "teatro", "theater", "club",
                "discoteca", "disco", "bar", "karaoke", "bowling", "gimnasio", "gym",
                "deporte", "sport", "entrada", "ticket", "suscripcion",
                "subscription", "youtube", "twitch",
                "pelicula", "film", "videojuego", "gaming", "partido", "match",
                "evento", "event", "festival", "festival de musica", "stand up",
                "comedia", "comedy", "museo", "museum", "exposicion", "exhibition"  
                
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
                "analisis", "botica", "clinic", "clinica", "consulta", "consulta particular", 
                "consultation", "dentist", "dentista", "doctor", "exam", "examen", "farmacia", 
                "glasses", "hospital", "inkafarma", "laboratory", "laboratorio", "lentes", 
                "medicina", "medicine", "medico", "mifarma", "odontologo", "optica", 
                "pastilla", "pharmacy", "pill", "terapia", "therapy", "vitamin", "vitamina"
            ],
            "Educación": [
                "academia", "ADEX", "Alas Peruanas", "AprendeLibre", "book", "bookstore", 
                "capacitacion", "Cayetano Heredia", "CENFOTEC", "certification", "certificacion", 
                "César Vallejo", "CIBERTEC", "class", "clase", "colegio", "colegio primaria", 
                "colegio secundaria", "course", "curso", "Crehana", "cuota", "Cursera", 
                "Domestika", "estudios", "IDAT", "IESTP", "INFOCAP", "institute", "Instituto", 
                "Instituto continental", "ISAT", "ISIL", "libreria", "libro", "materiales", 
                "matricula", "mensualidad", "pension", "school", "SENATI", "SISE", "supplies", 
                "tesis", "training", "tuition", "UCSP", "UCSM", "UCV", "UNALM", "UNE", 
                "UNFV", "UNI", "UNMSM", "universidad", "university", "Universidad Nacional del Callao", 
                "Universidad privada", "Universidad pública", "UNTELS", "UPN", "utiles", "UTP"
            ],
            "Vivienda": [
                "aire acondicionado", "albanil", "albañil", "alicates", "alfombra", 
                "alquiler", "apartment", "arrendamiento", "aspiradora", "bombilla", 
                "cafetera", "calentador", "cama", "casa", "clavos", "cocina", "colchón", 
                "condominio", "constructor", "copas", "cómoda", "cortinas", "cuadro", 
                "cubiertos", "decoracion", "decoración", "departamento", "destornillador", 
                "electrician", "electricista", "electrodomésticos", "enseres", "equipo de sonido", 
                "equipos", "escalera", "escritorio", "espejo", "estante", "estufa", 
                "ferreteria", "ferretería", "foco", "furniture", "gasfitero", "hardware", 
                "herramientas", "hielera", "hipoteca", "hogar", "iluminación", "inmobiliaria", 
                "jardinería", "lámpara", "lavadora", "licuadora", "librero", "limpieza", 
                "llave inglesa", "mantenimiento", "martillo", "menajería", "mesa", 
                "microondas", "mueble", "muebles", "ollas", "paint", "parlante", "pintado", 
                "pintura", "platos", "plumber", "pyrex", "refrigeradora", "rent", "renta", 
                "reparacion", "reparaciones", "ropero", "sartenes", "secadora", "silla", 
                "sillón", "sofá", "taladro", "táper", "terma", "televisor", "tornillos", 
                "utensilios", "vajilla", "vasos", "ventilador", "vivienda"
            ],
            "Vestimenta": [
                "abrigo", "accesorio", "accesorios", "accessory", "amazon", "anillo", 
                "aretes", "arreglo", "bañador", "bata", "bermuda", "bikini", "billetera", 
                "blusa", "bolso", "botas", "botines", "boutique", "bóxer", "brasier", 
                "bufanda", "buzo", "calcetines", "calzado", "calzoncillo", "camisa", 
                "camiseta", "cartera", "casaca", "chaleco", "chaqueta", "chompa", 
                "cinturón", "clothes", "collar", "corbata", "correa", "costura", "denim", 
                "deporte", "ebay", "enterizo", "entrenamiento", "falabella", "falda", 
                "forever21", "gafas", "gift", "gorra", "gorro", "guantes", "gym", "h&m", 
                "jean", "jewelry", "jockey", "joya", "joyas", "joyería", "lavandería", 
                "leggings", "lentes", "makeup", "mall", "mantenimiento", "medias", 
                "mercadolibre", "moccasines", "mochila", "moda", "natación", "oechsle", 
                "outfit", "pantalón", "pantuflas", "paris", "pijama", "plaza", "polera", 
                "polo", "prenda", "pulsera", "real plaza", "regalo", "reloj", "ripley", 
                "ropa", "ropa deportiva", "ropa interior", "saco", "saga", "sandalias", 
                "sastre", "sastrería", "shoes", "short", "sombrero", "sostén", "store", 
                "suéter", "tacos", "terno", "textil", "tienda", "tintorería", "traje", 
                "truza", "vestido", "vestimenta", "vestir", "watch", "zapatillas", 
                "zapatero", "zapateria", "zapatos", "zara"
            ],

            "Comunicaciones": [ 
                "cable", "celular", "internet", "mobile", "phone", "telefono",
                "tv", "telfonía", "claro", "entel", "bitel", "movistar", "starlink",
                "cablevisión", "directv", 
                "fibertel", "telecom", "telefonía", "telefonía móvil", "telefonía fija"
            ],
            
            "Restaurantes y gastronomía": [
                "alfresco", "almuerzo", "anticuchería", "anticuchos", "antojito", "asado", 
                "bacán", "bar", "barra cevichera", "beber", "bembos", "blanca flor", 
                "bodega", "breakfast", "burger", "burger king", "butifarra", "caminos del inca", 
                "capriccio", "carl's jr", "carrito", "cebichería", "cevicheria", "ceviche", 
                "chicha", "chicha morada", "chifa", "china wok", "chinawok", "chicharrones", 
                "churros", "comida ambulante", "cena", "cerveza", "chicken", "d'onofrio", 
                "delivery", "desayuno", "desayuno al paso", "didi food", "dinner", 
                "domino's", "domo saltado", "don belisario", "donas", "donofrio", 
                "donuts", "doomo saltado", "drink", "dunkin", "el buen gusto", "el chinito", 
                "el muelle", "el pez on", "emoliente", "emolientero", "empanada", 
                "empanadas", "empanadas paulistas", "food truck", "galletas", "grimanesa", 
                "hamburguesa", "hamburguesería", "helados", "hikari", "ice cream", 
                "jockey plaza", "kentucky", "kfc", "kiosko", "la casa de las empanadas", 
                "la ibérica", "la iberica", "la leña", "la lucha", "la panca", "la rambla", 
                "larcomar", "las canastas", "leche de tigre", "listo", "little caesars", 
                "lunch", "macuca", "mall aventura", "mall del sur", "marisquería", 
                "mcdonald's", "mcdonalds", "mediterraneo", "megaplaza", "mi barrunto", 
                "minka", "minimarket", "munchis", "niqqu", "norky", "norkys", "open plaza", 
                "otto grill", "oxxo", "pan con chicharrón", "papa john's", "papa rellena", 
                "pardos chicken", "pasquale", "pecsa", "pedidosya", "perros y papas", 
                "pescados capitales", "picanteria", "picarones", "piqueo", "piqueos", 
                "pizza", "pizza hut", "plaza norte", "plaza san miguel", "pollo", 
                "pollo a la brasa", "polleria", "popeyes", "pub", "punto azul", "puruchuco", 
                "quiosco", "quinua", "rappi", "real plaza", "repsol shop", "restaurant", 
                "rockys", "salaverry", "salchipapa", "salchipapas", "sanguchería", 
                "sanguche", "sanguches", "santa anita", "sarita", "starbucks", "subway", 
                "sushi", "taco bell", "tamales", "tambo", "terminal pesquero", 
                "tía grimanesa", "tienda", "tío bobby", "villa chicken", "viva", "vlady"
            ],
            
            "Hospedaje y viajes": [
                "aeropuerto", "airbnb", "albergue", "alojamiento", "asia", "backpackers", 
                "boleto", "booking", "cama", "canta", "churín", "cial", "clase ejecutiva", 
                "costamar", "cruz del sur", "cusco", "despegar", "equipaje", "estancia", 
                "excursión", "expedia", "full day", "habitación", "hospedaje", "hostal", 
                "hotel", "inca rail", "itssa", "jetsmart", "jorge chávez", "lap", "latam", 
                "lunahuaná", "machu picchu", "mancora", "motel", "móvil bus", "nuevo mundo", 
                "oltursa", "paracas", "pasaje", "peru rail", "perubus", "posada", "redbus", 
                "resort", "sky", "soyuz", "star perú", "suite", "tarapoto", "tepsa", 
                "tour", "trivago", "turismo", "vacaciones", "viaje", "viva air", "vuelo"
                
            ],
            
            "Vicios y hobbies": [
                "cerveza", "beer", "alcohol", "tabaco", "juegos", "hobbies",
                "apuestas", "atlantic city", "bar", "betano", "betsson", "cartavio", 
                "casino", "cerveza", "cigarro", "cigarrillo", "cocktail", "corona", 
                "cristal", "cusqueña", "discoteca", "encendedor", "fiesta casino", 
                "flor de caña", "ganadiario", "gin", "hamilton", "heineken", "inkabet", 
                "inkabet", "johnnie walker", "licor", "lotería", "lucky strike", 
                "majestic", "marlboro", "pilsen", "pisco", "queirolo", "ron", 
                "tabaco", "tabernero", "tacama", "te apuesto", "tinka", "vape", 
                "vapeador", "vino", "vodka", "whisky"
                
            ],
            
            "Higiene/Cuidado personal": [
                "acondicionador", "afeitado", "algodón", "amarige", "aruma", "aussie", "avené", 
                "avene", "avon", "axe", "babysec", "barba", "barber shop", "barbería", 
                "belcorp", "belleza", "bioderma", "biogreen", "botica", "boticas perú", 
                "burt's bees", "calvin klein", "cantu", "carefree", "carol's daughter", 
                "cepa menstrual", "cepillo", "cerave", "cetaphil", "champú", "clean & clear", 
                "clínica", "clinique", "colgate", "copa menstrual", "cortaúñas", "crema", 
                "cuidado personal", "cyzone", "dentito", "dentífrico", "depilación", 
                "desodorante", "dove", "dove men+care", "dr. bronner's", "e.l.f. cosmetics", 
                "efasit", "elite", "elvive", "enjuague bucal", "ésika", "esika", "essence", 
                "especialista", "eucerin", "farmacia", "fenty beauty", "garnier", "gillette", 
                "glossier", "gnc", "h&s", "head & shoulders", "herbal essences", "herbivore", 
                "hies", "higiene", "higiene femenina", "hinds", "huggies", "inkafarma", 
                "isdin", "jabón", "johnson's", "johnsons", "kérastase", "kolynos", "kotex", 
                "l'bel", "lbel", "l'oreal", "labnutrition", "lactacyd", "lady speed stick", 
                "la roche posay", "laura mercier", "listerine", "loción", "lubriderm", 
                "lush", "manicura", "maquillaje", "marco aldany", "maybelline", "mifarma", 
                "montalvo", "moroccanoil", "natura", "neutrogena", "nivea", "nivea men", 
                "nosotras", "nyx", "ob", "old spice", "oral-b", "oriflame", "pacifica", 
                "pampers", "pantene", "pañales", "pañitos húmedos", "papel higiénico", 
                "paracas", "pasta dental", "pedicura", "peluquería", "perfume", "philosophy", 
                "pixi", "pro", "rekamier", "rexona", "sally beauty", "salón de belleza", 
                "savital", "schick", "sedal", "sensodyne", "sephora", "shampoo", "soho", 
                "spa", "speed stick", "st. ives", "suave", "talco", "tampones", "tarte", 
                "the body shop", "toallas higiénicas", "too faced", "unique", "urban decay", 
                "vasenol", "vichy", "yanbal", "yodora"
                
            ],
            
            "Otros Gastos": []  # Categoría por defecto para gastos
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