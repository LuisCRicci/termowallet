"""
Categorizador Automático de Transacciones
Archivo: src/business/categorizer.py
"""

import re
from typing import Dict, List


class TransactionCategorizer:
    """Categoriza transacciones basándose en palabras clave en la descripción"""

    def __init__(self):
        # Diccionario de palabras clave por categoría
        self.keywords = {
            "Alimentación": [
                "restaurant", "comida", "food","pizza","burger","cafe","cafeteria","supermercado","market",
                "panaderia","bakery", "almuerzo","lunch","cena","dinner","desayuno","breakfast","bar","pub",
                "mcdonalds", "kfc", "starbucks", "subway","pollo","chicken", "bebida","drink", "cerveza", "beer",
                "mercado","bodega","tienda","grocery","bembos","norky","china wok","delivery","papa rellena", 
                "cevicheria", "polleria", "hamburgueseria", "ceviche", "pollo a la brasa", "chifa", "hamburguesa",
                "sushi", "anticuchos" , "picanteria" , "empanadas" , "tamales", "churros",  "donas", "donuts", "helados", "ice cream",
                "yogurt","frozen yogurt", "frutas","verduras","vegetales","carniceria","butcher","picarones","chocolateria",
                "dulceria","snacks","antojitos", "chocolates", "golosinas" , "chocolate" , "golosina", "snack" , "antojito",
                "salchipapa", "salchipapas", "empanada", "empanadas", "piqueo", "piqueos","chifles","papas fritas","papas a la francesa",
                "chicharrones","nachos","hot dog","hotdog","sandwich","sanguches", "chizitos","gaseosa","soda","refresco","refrescos",
                "jugo","juice","smoothie","batido","agua","water","leche","milk","yogur","yogurt"
            
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
                "cosmetico","perfume","maquillaje","makeup","accesorio","accessory","reloj","watch","joya","jewelry","regalo","gift",
            ],
            "Otros": [],  # Categoría por defecto
        }

    def categorize(self, description: str) -> str:
        """
        Categoriza una transacción basándose en su descripción
        Returns: Nombre de la categoría
        """
        if not description:
            return "Otros"

        # Convertir a minúsculas y limpiar
        desc_lower = description.lower().strip()

        # Buscar coincidencias en cada categoría
        matches = {}
        for category, keywords in self.keywords.items():
            if category == "Otros":
                continue

            # Contar cuántas keywords coinciden
            match_count = sum(1 for keyword in keywords if keyword in desc_lower)
            if match_count > 0:
                matches[category] = match_count

        # Retornar la categoría con más coincidencias
        if matches:
            return max(matches, key=lambda k: matches[k])

        return "Otros"

    def add_keyword(self, category: str, keyword: str):
        """Añade una palabra clave a una categoría"""
        if category in self.keywords:
            if keyword.lower() not in self.keywords[category]:
                self.keywords[category].append(keyword.lower())

    def get_categories(self) -> list:
        """Retorna la lista de categorías disponibles"""
        return [cat for cat in self.keywords.keys() if cat != "Otros"] + ["Otros"]
