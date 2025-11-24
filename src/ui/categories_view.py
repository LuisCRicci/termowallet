"""
Vista de gestión de categorías - SOLUCIÓN DEFINITIVA
Archivo: src/ui/categories_view.py

✅ SOLUCIÓN: Picker integrado en el mismo diálogo (NO diálogos anidados)
✅ CORREGIDO: Selección de colores coherente y grilla 8x5
✅ CORREGIDO: Uso de colores nativos de Flet (ft.Colors.*) para compatibilidad total
"""

import flet as ft
from .base_view import BaseView
from src.utils.config import Config


class CategoriesView(BaseView):
    """Vista de gestión de categorías con picker integrado"""
    
    def __init__(self, page: ft.Page, db_manager, show_snackbar_callback):
        super().__init__(page, db_manager, show_snackbar_callback)
        self.is_saving = False
    
    # ✅ Mapeo de colores Flet a sus nombres para la UI
    FLET_COLORS = {
        # Rojos
        ft.Colors.RED_700: "Rojo oscuro",
        ft.Colors.RED_600: "Rojo",
        ft.Colors.RED_500: "Rojo medio",
        ft.Colors.RED_400: "Rojo claro",
        ft.Colors.RED_200: "Rojo pálido",
        # Naranjas
        ft.Colors.DEEP_ORANGE_700: "Naranja oscuro",
        ft.Colors.DEEP_ORANGE_600: "Naranja",
        ft.Colors.DEEP_ORANGE_500: "Naranja medio",
        ft.Colors.DEEP_ORANGE_400: "Naranja claro",
        ft.Colors.DEEP_ORANGE_200: "Naranja pálido",
        # Amarillos/Ámbar
        ft.Colors.AMBER_700: "Amarillo oscuro",
        ft.Colors.AMBER_600: "Amarillo",
        ft.Colors.AMBER_500: "Amarillo medio",
        ft.Colors.AMBER_400: "Amarillo claro",
        ft.Colors.AMBER_200: "Amarillo pálido",
        # Verdes
        ft.Colors.GREEN_700: "Verde oscuro",
        ft.Colors.GREEN_600: "Verde",
        ft.Colors.GREEN_500: "Verde medio",
        ft.Colors.GREEN_400: "Verde claro",
        ft.Colors.GREEN_200: "Verde pálido",
        # Azules
        ft.Colors.BLUE_700: "Azul oscuro",
        ft.Colors.BLUE_600: "Azul",
        ft.Colors.BLUE_500: "Azul medio",
        ft.Colors.BLUE_400: "Azul claro",
        ft.Colors.BLUE_200: "Azul pálido",
        # Púrpuras
        ft.Colors.PURPLE_700: "Púrpura oscuro",
        ft.Colors.PURPLE_600: "Púrpura",
        ft.Colors.PURPLE_500: "Púrpura medio",
        ft.Colors.PURPLE_400: "Púrpura claro",
        ft.Colors.PURPLE_200: "Púrpura pálido",
        # Rosas
        ft.Colors.PINK_700: "Rosa oscuro",
        ft.Colors.PINK_600: "Rosa",
        ft.Colors.PINK_500: "Rosa medio",
        ft.Colors.PINK_400: "Rosa claro",
        ft.Colors.PINK_200: "Rosa pálido",
        # Grises
        ft.Colors.GREY_700: "Gris oscuro",
        ft.Colors.GREY_600: "Gris",
        ft.Colors.GREY_500: "Gris medio",
        ft.Colors.GREY_400: "Gris claro",
        ft.Colors.GREY_200: "Gris pálido",
    }

    def _create_category_tile(self, category):
        """Crea un tile para una categoría CON indicador de palabras clave"""
        keywords_list = category.get_keywords_list()
        keywords_count = len(keywords_list)
        
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text(category.icon, size=32),
                        width=60,
                        height=60,
                        border_radius=30,
                        bgcolor=category.color,  # ✅ Color directo de Flet
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                category.name if category.name else "Sin categoría",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                category.description if category.description else "Sin descripción",
                                size=12,
                                color=ft.Colors.GREY_600,
                            ),
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.KEY, size=14, color="#3b82f6"),
                                        ft.Text(
                                            f"{keywords_count} palabras clave",
                                            size=11,
                                            color="#3b82f6",
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                    ],
                                    spacing=5,
                                ),
                                padding=ft.padding.only(top=5),
                            ) if keywords_count > 0 else ft.Container(),
                        ],
                        expand=True,
                        spacing=2,
                    ),
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.LABEL,
                                icon_size=20,
                                tooltip="Palabras clave",
                                icon_color="#667eea",
                                on_click=lambda e, cat=category: self.show_keywords_dialog(cat),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_size=20,
                                tooltip="Editar",
                                on_click=lambda e, cat=category: self.show_edit_category_dialog(cat),
                                disabled=category.is_default,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_size=20,
                                tooltip="Eliminar",
                                on_click=lambda e, cat=category: self.delete_category(cat),
                                disabled=category.is_default,
                            ),
                        ]
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            margin=ft.margin.only(bottom=10),
        )

    def show_keywords_dialog(self, category):
        """Muestra diálogo para gestionar palabras clave"""
        keywords_list = category.get_keywords_list()
        
        new_keyword_field = ft.TextField(
            label="Nueva palabra clave",
            hint_text="Escribe una palabra y presiona Enter",
            bgcolor=ft.Colors.WHITE,
            on_submit=lambda e: add_keyword(e),
        )
        
        keywords_chips = ft.Row(
            wrap=True,
            spacing=5,
            run_spacing=5,
        )
        
        def update_chips():
            keywords_chips.controls.clear()
            current_keywords = category.get_keywords_list()
            
            if not current_keywords:
                keywords_chips.controls.append(
                    ft.Text(
                        "No hay palabras clave. Agrega algunas para mejorar la categorización automática.",
                        size=12,
                        color=ft.Colors.GREY_600,
                        italic=True,
                    )
                )
            else:
                for keyword in sorted(current_keywords):
                    keywords_chips.controls.append(
                        ft.Chip(
                            label=ft.Text(keyword, size=12),
                            on_delete=lambda e, k=keyword: remove_keyword(k),
                            bgcolor=ft.Colors.LIGHT_BLUE_100,
                            delete_icon_color=ft.Colors.RED_400,
                        )
                    )
            self.page.update()
        
        def add_keyword(e):
            if not new_keyword_field.value or not new_keyword_field.value.strip():
                return
            
            keyword = new_keyword_field.value.strip().lower()
            current_keywords = category.get_keywords_list()
            
            if keyword in current_keywords:
                self.show_snackbar("Esta palabra clave ya existe", error=True)
                return
            
            current_keywords.append(keyword)
            category.set_keywords_list(current_keywords)
            self.db.session.commit()
            
            new_keyword_field.value = ""
            update_chips()
        
        def remove_keyword(keyword):
            current_keywords = category.get_keywords_list()
            if keyword in current_keywords:
                current_keywords.remove(keyword)
                category.set_keywords_list(current_keywords)
                self.db.session.commit()
                update_chips()
        
        def restore_defaults(e):
            def confirm_restore(e):
                result = self.db.restore_default_keywords(category.id)
                self.close_dialog()

                if result["success"] and result["updated_count"] > 0:
                    update_chips()
                    self._reload_view()
                    self.show_snackbar(f"✅ Keywords restauradas: {category.name}")
                else:
                    self.show_snackbar(result["message"], error=True)
            
            confirm_dialog = ft.AlertDialog(
                title=ft.Text("Confirmar Restauración"),
                content=ft.Column(
                    [
                        ft.Text(
                            f"¿Restaurar las palabras clave predeterminadas de '{category.name}'?",
                            size=14,
                        ),
                        ft.Container(height=10),
                        ft.Container(
                            content=ft.Text(
                                "⚠️ Se perderán las palabras clave personalizadas actuales",
                                size=12,
                                color="#f59e0b",
                                weight=ft.FontWeight.BOLD,
                            ),
                            padding=10,
                            bgcolor="#fef3c7",
                            border_radius=8,
                        ),
                    ],
                    tight=True,
                ),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                    ft.ElevatedButton(
                        "Restaurar",
                        on_click=confirm_restore,
                        style=ft.ButtonStyle(bgcolor="#3b82f6", color=ft.Colors.WHITE),
                    ),
                ],
            )
            
            self.show_dialog(confirm_dialog)
        
        def save_and_close(e):
            self.close_dialog()
            self.show_snackbar("✅ Palabras clave actualizadas")
            self._reload_view()
        
        update_chips()
        
        restore_button = None
        if category.is_default:
            restore_button = ft.OutlinedButton(
                "Restaurar defaults",
                icon=ft.Icons.RESTORE,
                on_click=restore_defaults,
                style=ft.ButtonStyle(color="#3b82f6"),
            )
        
        dialog = ft.AlertDialog(
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.LABEL, color=category.color, size=28),
                    ft.Text(
                        f"Palabras clave: {category.name}",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                spacing=10,
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "💡 Las palabras clave ayudan a categorizar automáticamente las transacciones",
                                        size=12,
                                        color=ft.Colors.BLUE_700,
                                    ),
                                    ft.Text(
                                        "Ejemplo: Para 'Alimentación' agrega: pizza, restaurant, supermercado, etc.",
                                        size=11,
                                        color=ft.Colors.GREY_600,
                                        italic=True,
                                    ),
                                ],
                                spacing=5,
                            ),
                            padding=10,
                            bgcolor=ft.Colors.BLUE_50,
                            border_radius=8,
                        ),
                        ft.Divider(height=20),
                        new_keyword_field,
                        ft.ElevatedButton(
                            "Agregar",
                            icon=ft.Icons.ADD,
                            on_click=add_keyword,
                            style=ft.ButtonStyle(
                                bgcolor=category.color,
                                color=ft.Colors.WHITE,
                            ),
                        ),
                        ft.Divider(height=20),
                        ft.Row(
                            [
                                ft.Text(
                                    f"🔑 Palabras clave actuales ({len(category.get_keywords_list())})",
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                (
                                    ft.Container(
                                        content=ft.Text(
                                            "Default",
                                            size=10,
                                            color=ft.Colors.WHITE,
                                        ),
                                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                        bgcolor="#3b82f6",
                                        border_radius=10,
                                    )
                                    if category.is_default
                                    else ft.Container()
                                ),
                            ],
                            spacing=10,
                        ),
                        ft.Container(
                            height=200,
                            padding=10,
                            bgcolor=ft.Colors.GREY_50,
                            border_radius=8,
                            content=ft.ListView(
                                controls=[keywords_chips],
                                spacing=5,
                                auto_scroll=False,
                                expand=True,
                            ),
                        ),
                    ],
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=550,
                height=500,
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=save_and_close),
                restore_button if restore_button else ft.Container(),
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN if restore_button else ft.MainAxisAlignment.END,
        )
        
        self.show_dialog(dialog)

    def show_add_category_dialog(self, e):
        """✅ SOLUCIÓN CORREGIDA: Picker con colores nativos de Flet y grilla 8x5"""
        self.is_saving = False
        
        # Estado actual con colores nativos de Flet
        current_state = {
            "emoji": "💰",
            "color": ft.Colors.BLUE_600
        }
        show_emoji_picker = [False]
        show_color_picker = [False]
        
        name_field = ft.TextField(label="Nombre", autofocus=True, bgcolor=ft.Colors.WHITE)
        desc_field = ft.TextField(label="Descripción", multiline=True, bgcolor=ft.Colors.WHITE)
        
        # Preview
        icon_preview = ft.Container(
            content=ft.Text(current_state["emoji"], size=48),
            width=80,
            height=80,
            bgcolor=current_state["color"],  # ✅ Color directo de Flet
            border_radius=40,
            alignment=ft.alignment.center,
        )
        
        preview_text = ft.Column(
            [
                ft.Text(f"Emoji: {current_state['emoji']}", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(
                    self.FLET_COLORS.get(current_state["color"], "Color personalizado"),
                    size=12,
                    color=ft.Colors.GREY_600
                ),
            ],
            spacing=5,
        )
        
        # EMOJIS
        emoji_categories = {
            "Cuerpo": [
                "🤸🏻‍♂️", "👩🏻‍🎨", "👰🏻‍♀️", "🥊", "👩🏻‍⚕️", "🏄", "👩‍❤️‍👨", "🛀",
                "🚵🏻‍♀️",  "👼🏻", "🧑🏻‍🎤", "👃🏻", "🤝🏻", "🙏🏻", "🫵🏻","🧘‍♂️"
                "🍀", "🫁", "🫀", "🧠", "🦷", "👄", "💅🏻", "💪🏼"],
            "Finanzas": [
                "💰", "💵", "💴", "💶", "💷", "💳", "💸", "💎", 
                "💲", "🪙", "🤑", "📈", "📉"],
            "Eventos": [
                "🎉", "🎊", "🎈", "🎁", "🎀", "🎂", "🎄","🎅🏻", "🎃",
                "🎆", "🎇", "🧨", "✨", "🎋", "🎍", "🎑", "🎏"
            ],
            "Animales": [
                "🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼",
                "🐨", "🐯", "🦁", "🐮", "🐷", "🐸", "🐵", "🐔",
                "🐧", "🐦", "🐤", "🐣", "🐥", "🦆", "🦅", "🦉",
                "🦇", "🐺", "🐗", "🐴", "🦄", "🐝", "🐛", "🦋"
            ],
            "Comida": [
                "🍕", "🍔", "🍟", "🌮", "🌯", "🥙", "🥗", "🍝",
                "🍜", "🍲", "🍱", "🍣", "🍤", "🍙", "🥟", "🍞",
                "🥐", "🧀", "🥚", "🍳", "🥓", "🥩", "🍗", "🍖",
                "🍛", "🍠", "🥘", "🍢", "🧆", "🥪", "🌭", "🍿",
                "🥫", "🫔", "🧈", "🥞", "🧇", "🥯", "🍩", "🍪",
                "🎂", "🍰", "🧁", "🍫", "🍬", "🍭", "🍮", "🍯"],
            "Entretenimiento": [
                "🎮", "🕹️", "🎯", "🎲", "🎰", "🎳", "🎾", "🏀",
                "⚽", "⚾", "🥎", "🏐", "🏈", "🏉", "🎱", "🥏",
                "🎭", "🎪", "🎨", "🎬", "🎤", "🎧", "🎼", "🎹",
                "🥁", "🎷", "🎺", "🎸", "🪕", "🎻", "🎟️", "🎫",
                "🤺", "🏇", "⛷️", "🚵", "🏊‍♂️", "🏄‍♀️", "🤼", "🏋️‍♀️"
            ],
            "Hogar": [
                "🏠", "🏡", "🏘️", "🏚️", "🏗️", "🏭", "🏢", "🏬",
                "🏣", "🏤", "🏥", "🏦", "🏨", "🏪", "🏫", "🏩",
                "💒", "🛏️", "🛋️", "🪑", "🚪", "🪟", "🚿", "🛁",
                "🚽", "🧻", "🧼", "🧽", "🧹", "🧺", "🔑", "🗝️"],
            "Salud": [
                "💊", "💉", "🩹", "🩺", "🌡️", "🩻", "🩼", "🦷",
                "🧬", "🧪", "🧫", "🧴", "🧯", "🩸", "🏥", "⚕️"],
            "Educación": [
                "📚", "🗞️", "📝", "✏️", "✒️", "🖊️", "🖍️", "📑",
                "📕", "📗", "📘", "📙", "📓", "📄", "📊", "🎓",
                "📰", "🎒", "🖌️", "📐", "📏", "🧮", "🔬", "🔭"],
            "Emociones": [
                "😀", "😃", "😄", "😁", "😆", "😅", "🤣", "😂",
                "🙂", "🙃", "😉", "😊", "😇", "🥰", "😍", "🤩",
                "😘", "😗", "😚", "😙", "🥲", "😋", "😛", "😜",
                "🤪", "😝", "🤑", "🤗", "🤭", "🤫", "🤔", "🤐"
            ],
            "Naturaleza": [
                "🌸", "🌺", "🌻", "🌹", "🥀", "🌷", "🌼", "🌱",
                "🪴", "🌲", "🌳", "🌴", "🌵", "🌾", "🌿", "☘️",
                "🍀", "🍁", "🍂", "🍃", "🪹", "🪺", "🌾", "💐"
            ],
            "Frutas": [
                "🍎", "🍏", "🍊", "🍋", "🍌", "🍉", "🍇", "🍓",
                "🫐", "🍈", "🍒", "🍑", "🥭", "🍍", "🥥", "🥝",
                "🍅", "🥑", "🫒", "🌶️", "🫑", "🥒", "🥬", "🥦"],
            "Bebidas": [
                "☕", "🍵", "🧃", "🥤", "🧋", "🍼", "🥛", "🍺",
                "🍻", "🍷", "🥂", "🍾", "🍹", "🍸", "🧉", "🥃"],
            "viajes": [
                "🚗", "🚕", "🚙", "🚌", "🚎", "🏎️", "🚓", "🚑",
                "🚒", "🚐", "🛻", "🚚", "🚛", "🚜", "🦯", "🦽",
                "🦼", "🛴", "🚲", "🛵", "🏍️", "🛺", "🚨", "🚔",
                "🚍", "🚘", "🚖", "🚡", "🚠", "🚟", "🚃", "🚋",
                "🚞", "🚝", "🚄", "🚅", "🚈", "🚂", "🚆", "🚇",
                "🚊", "🚉", "✈️", "🛫", "🛬", "🛩️", "💺", "🚁",
                "🛸", "🚀", "🛰️", "🚢", "⛵", "🛶", "⛴️", "🛥️"],
            "Ropa": [
                "👕", "👔", "👗", "👘", "🥻", "🩱", "🩲", "🩳",
                "👖", "👚", "👙", "🧥", "🥼", "🦺", "⛑️", "🎩",
                "🧢", "👒", "🎓", "👑", "💍", "👞", "👟", "🥾",
                "🥿", "👠", "👡", "🩰", "👢", "👜", "👝", "🎒",
                "👛", "💼", "🧳", "👓", "🕶️", "🥽", "🌂", "🧣"],
            "Trabajo": [
                "💼", "📁", "📂", "🗂️", "📋", "📊", "📈", "📉",
                "📇", "📌", "📍", "📎", "🖇️", "📏", "📐", "✂️",
                "🗃️", "🗄️", "🗑️", "🔒", "🔓", "🔐", "🔏", "🖊️"
            ],
            "Compras": [
                "🎁", "🛍️", "🛒", "💳", "🏪", "🏬", "🏢", "💰",
                "💵", "💴", "💶", "💷", "🪙", "💸", "🧾", "🎀"
            ],
            "Servicios": [
                "⚡", "💡", "🔌", "🔋", "💻", "⌨️", "🖱️", "🖥️",
                "📱", "☎️", "📞", "📟", "📠", "📺", "📻", "🎙️",
                "🔊", "🔉", "🔇", "📡", "🛜", "📶", "📳", "📴"
            ]
        }
        
        emoji_grid = ft.GridView(
            runs_count=8,
            max_extent=50,
            spacing=8,
            run_spacing=8,
            height=300,
        )
        
        emoji_tabs = ft.Tabs(
            selected_index=0,
            scrollable=True,
            tabs=[ft.Tab(text=name.strip()) for name in emoji_categories.keys()],
        )
        
        def load_emojis(category_index):
            emoji_grid.controls.clear()
            category_name = list(emoji_categories.keys())[category_index]
            emojis = emoji_categories[category_name]
            
            for emoji in emojis:
                is_selected = emoji == current_state["emoji"]
                emoji_grid.controls.append(
                    ft.Container(
                        content=ft.Text(emoji, size=28),
                        width=45,
                        height=45,
                        border_radius=8,
                        bgcolor=ft.Colors.LIGHT_BLUE_100 if is_selected else ft.Colors.WHITE,
                        border=ft.border.all(2, ft.Colors.BLUE_400 if is_selected else ft.Colors.GREY_300),
                        alignment=ft.alignment.center,
                        on_click=lambda e, em=emoji: select_emoji(em),
                        ink=True,
                    )
                )
            try:
                if emoji_grid.page:
                    emoji_grid.update()
            except:
                pass
        
        def select_emoji(emoji):
            current_state["emoji"] = emoji
            icon_preview.content.value = emoji
            preview_text.controls[0].value = f"Emoji: {emoji}"
            try:
                if icon_preview.page:
                    icon_preview.update()
                if preview_text.page:
                    preview_text.update()
            except:
                pass
            load_emojis(emoji_tabs.selected_index)
        
        emoji_tabs.on_change = lambda e: load_emojis(e.control.selected_index)
        
        # ✅ COLORES - Grilla 8x5 con colores nativos de Flet
        colors = [
            # Rojos (5 tonos)
            ft.Colors.RED_700, ft.Colors.RED_600, ft.Colors.RED_500, ft.Colors.RED_400, ft.Colors.RED_200,
            # Naranjas (5 tonos)
            ft.Colors.DEEP_ORANGE_700, ft.Colors.DEEP_ORANGE_600, ft.Colors.DEEP_ORANGE_500, ft.Colors.DEEP_ORANGE_400, ft.Colors.DEEP_ORANGE_200,
            # Amarillos (5 tonos)
            ft.Colors.AMBER_700, ft.Colors.AMBER_600, ft.Colors.AMBER_500, ft.Colors.AMBER_400, ft.Colors.AMBER_200,
            # Verdes (5 tonos)
            ft.Colors.GREEN_700, ft.Colors.GREEN_600, ft.Colors.GREEN_500, ft.Colors.GREEN_400, ft.Colors.GREEN_200,
            # Azules (5 tonos)
            ft.Colors.BLUE_700, ft.Colors.BLUE_600, ft.Colors.BLUE_500, ft.Colors.BLUE_400, ft.Colors.BLUE_200,
            # Púrpuras (5 tonos)
            ft.Colors.PURPLE_700, ft.Colors.PURPLE_600, ft.Colors.PURPLE_500, ft.Colors.PURPLE_400, ft.Colors.PURPLE_200,
            # Rosas (5 tonos)
            ft.Colors.PINK_700, ft.Colors.PINK_600, ft.Colors.PINK_500, ft.Colors.PINK_400, ft.Colors.PINK_200,
            # Grises (5 tonos)
            ft.Colors.GREY_700, ft.Colors.GREY_600, ft.Colors.GREY_500, ft.Colors.GREY_400, ft.Colors.GREY_200,
        ]
        
        color_grid = ft.GridView(
            runs_count=5,  # ✅ 5 columnas = grilla 8x5
            max_extent=50,
            spacing=10,
            run_spacing=10,
            height=400,  # ✅ Altura para 8 filas
        )
        
        def load_colors():
            color_grid.controls.clear()
            for color in colors:
                is_selected = color == current_state["color"]
                color_grid.controls.append(
                    ft.Container(
                        width=45,
                        height=45,
                        bgcolor=color,  # ✅ Color nativo de Flet
                        border_radius=22.5,
                        border=ft.border.all(
                            width=3 if is_selected else 1,
                            color=ft.Colors.BLACK if is_selected else ft.Colors.GREY_400
                        ),
                        on_click=lambda e, c=color: select_color(c),
                        ink=True,
                        tooltip=self.FLET_COLORS.get(color, ""),
                    )
                )
            try:
                if color_grid.page:
                    color_grid.update()
            except:
                pass
        
        def select_color(color):
            current_state["color"] = color
            icon_preview.bgcolor = color  # ✅ Asignación directa
            preview_text.controls[1].value = self.FLET_COLORS.get(color, "Color personalizado")
            try:
                if icon_preview.page:
                    icon_preview.update()
                if preview_text.page:
                    preview_text.update()
            except:
                pass
            load_colors()
        
        # Contenedor de pickers
        picker_container = ft.Container(visible=False)
        
        def toggle_pickers(e):
            if show_emoji_picker[0]:
                picker_container.content = ft.Column([emoji_tabs, emoji_grid], spacing=10)
                picker_container.visible = True
                load_emojis(0)
            elif show_color_picker[0]:
                picker_container.content = color_grid
                picker_container.visible = True
                load_colors()
            else:
                picker_container.visible = False
            try:
                if picker_container.page:
                    picker_container.update()
            except:
                pass
        
        emoji_checkbox = ft.Checkbox(
            label="Seleccionar emoji",
            value=False,
            on_change=lambda e: [
                show_emoji_picker.__setitem__(0, e.control.value),
                show_color_picker.__setitem__(0, False) if e.control.value else None,
                color_checkbox.__setattr__("value", False) if e.control.value else None,
                toggle_pickers(e),
            ],
        )
        
        color_checkbox = ft.Checkbox(
            label="Seleccionar color",
            value=False,
            on_change=lambda e: [
                show_color_picker.__setitem__(0, e.control.value),
                show_emoji_picker.__setitem__(0, False) if e.control.value else None,
                emoji_checkbox.__setattr__("value", False) if e.control.value else None,
                toggle_pickers(e),
            ],
        )
        
        type_dropdown = ft.Dropdown(
            label="Tipo",
            options=[
                ft.dropdown.Option(key="expense", text="Gasto"),
                ft.dropdown.Option(key="income", text="Ingreso"),
            ],
            value="expense",
            bgcolor=ft.Colors.WHITE,
        )
        
        keywords_field = ft.TextField(
            label="Palabras clave (opcional)",
            hint_text="Ejemplo: pizza, restaurant, comida (separadas por comas)",
            multiline=True,
            min_lines=2,
            max_lines=2,
            bgcolor=ft.Colors.WHITE,
        )

        def save_category(e):
            if self.is_saving:
                return
            
            if not name_field.value:
                self.show_snackbar("El nombre es obligatorio", error=True)
                return

            self.is_saving = True
            
            try:
                existing = self.db.get_category_by_name(
                    name_field.value.strip(),
                    type_dropdown.value or "expense"
                )
                
                if existing:
                    self.show_snackbar("Ya existe una categoría con ese nombre", error=True)
                    self.is_saving = False
                    return
                
                category = self.db.add_category(
                    name=name_field.value.strip(),
                    icon=current_state["emoji"],
                    color=current_state["color"],
                    category_type=type_dropdown.value or "expense",
                    description=desc_field.value.strip() if desc_field.value else "",
                )
                
                if keywords_field.value and keywords_field.value.strip():
                    keywords = [k.strip() for k in keywords_field.value.split(',') if k.strip()]
                    category.set_keywords_list(keywords)
                    self.db.session.commit()
                
                self.close_dialog()
                self.show_snackbar("✅ Categoría creada exitosamente")
                self._reload_view()
                
            except Exception as ex:
                self.show_snackbar(f"Error: {str(ex)}", error=True)
                self.is_saving = False

        dialog = ft.AlertDialog(
            title=ft.Text("Nueva Categoría"),
            content=ft.Container(
                content=ft.Column(
                    [
                        name_field,
                        desc_field,
                        ft.Divider(height=5),
                        ft.Text("Apariencia", size=14, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Row([icon_preview, preview_text], spacing=15),
                            padding=15,
                            bgcolor=ft.Colors.GREY_50,
                            border_radius=10,
                        ),
                        ft.Row([emoji_checkbox, color_checkbox], spacing=20),
                        picker_container,
                        ft.Divider(height=10),
                        type_dropdown,
                        keywords_field,
                    ],
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                    spacing=10,
                ),
                height=650,
                width=550,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.ElevatedButton(
                    "Guardar",
                    on_click=save_category,
                    style=ft.ButtonStyle(bgcolor="#667eea", color=ft.Colors.WHITE),
                ),
            ],
        )

        self.show_dialog(dialog)

    def show_edit_category_dialog(self, category):
        """✅ Editar categoría con colores nativos de Flet y grilla 8x5"""
        self.is_saving = False
        
        # Estado actual (inicializado con valores de la categoría)
        current_state = {
            "emoji": category.icon,
            "color": category.color  # Ya debe ser un color de Flet
        }
        show_emoji_picker = [False]
        show_color_picker = [False]
        
        name_field = ft.TextField(label="Nombre", value=category.name, bgcolor=ft.Colors.WHITE)
        desc_field = ft.TextField(label="Descripción", value=category.description or "", multiline=True, bgcolor=ft.Colors.WHITE)
        
        # Preview
        icon_preview = ft.Container(
            content=ft.Text(current_state["emoji"], size=48),
            width=80,
            height=80,
            bgcolor=current_state["color"],  # ✅ Color directo de Flet
            border_radius=40,
            alignment=ft.alignment.center,
        )
        
        preview_text = ft.Column(
            [
                ft.Text(f"Emoji: {current_state['emoji']}", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(
                    self.FLET_COLORS.get(current_state["color"], "Color personalizado"),
                    size=12,
                    color=ft.Colors.GREY_600
                ),
            ],
            spacing=5,
        )
        
        # EMOJIS (misma estructura)
        emoji_categories = {
            "Cuerpo": [
                "🤸🏻‍♂️", "👩🏻‍🎨", "👰🏻‍♀️", "🥊", "👩🏻‍⚕️", "🏄", "👩‍❤️‍👨", "🛀",
                "🚵🏻‍♀️",  "👼🏻", "🧑🏻‍🎤", "👃🏻", "🤝🏻", "🙏🏻", "🫵🏻","🧘‍♂️"
                "🍀", "🫁", "🫀", "🧠", "🦷", "👄", "💅🏻", "💪🏼"],
            "Finanzas": [
                "💰", "💵", "💴", "💶", "💷", "💳", "💸", "💎", 
                "💲", "🪙", "🤑", "📈", "📉"],
            "Eventos": [
                "🎉", "🎊", "🎈", "🎁", "🎀", "🎂", "🎄","🎅🏻", "🎃",
                "🎆", "🎇", "🧨", "✨", "🎋", "🎍", "🎑", "🎏"
            ],
            "Animales": [
                "🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼",
                "🐨", "🐯", "🦁", "🐮", "🐷", "🐸", "🐵", "🐔",
                "🐧", "🐦", "🐤", "🐣", "🐥", "🦆", "🦅", "🦉",
                "🦇", "🐺", "🐗", "🐴", "🦄", "🐝", "🐛", "🦋"
            ],
            "Comida": [
                "🍕", "🍔", "🍟", "🌮", "🌯", "🥙", "🥗", "🍝",
                "🍜", "🍲", "🍱", "🍣", "🍤", "🍙", "🥟", "🍞",
                "🥐", "🧀", "🥚", "🍳", "🥓", "🥩", "🍗", "🍖",
                "🍛", "🍠", "🥘", "🍢", "🧆", "🥪", "🌭", "🍿",
                "🥫", "🫔", "🧈", "🥞", "🧇", "🥯", "🍩", "🍪",
                "🎂", "🍰", "🧁", "🍫", "🍬", "🍭", "🍮", "🍯"],
            "Entretenimiento": [
                "🎮", "🕹️", "🎯", "🎲", "🎰", "🎳", "🎾", "🏀",
                "⚽", "⚾", "🥎", "🏐", "🏈", "🏉", "🎱", "🥏",
                "🎭", "🎪", "🎨", "🎬", "🎤", "🎧", "🎼", "🎹",
                "🥁", "🎷", "🎺", "🎸", "🪕", "🎻", "🎟️", "🎫",
                "🤺", "🏇", "⛷️", "🚵", "🏊‍♂️", "🏄‍♀️", "🤼", "🏋️‍♀️",
            ],
            "Hogar": [
                "🏠", "🏡", "🏘️", "🏚️", "🏗️", "🏭", "🏢", "🏬",
                "🏣", "🏤", "🏥", "🏦", "🏨", "🏪", "🏫", "🏩",
                "💒", "🛏️", "🛋️", "🪑", "🚪", "🪟", "🚿", "🛁",
                "🚽", "🧻", "🧼", "🧽", "🧹", "🧺", "🔑", "🗝️"],
            "Salud": [
                "💊", "💉", "🩹", "🩺", "🌡️", "🩻", "🩼", "🦷",
                "🧬", "🧪", "🧫", "🧴", "🧯", "🩸", "🏥", "⚕️"],
            "Educación": [
                "📚", "🗞️", "📝", "✏️", "✒️", "🖊️", "🖍️", "📑",
                "📕", "📗", "📘", "📙", "📓", "📄", "📊", "🎓",
                "📰", "🎒", "🖌️", "📐", "📏", "🧮", "🔬", "🔭"],
            "Emociones": [
                "😀", "😃", "😄", "😁", "😆", "😅", "🤣", "😂",
                "🙂", "🙃", "😉", "😊", "😇", "🥰", "😍", "🤩",
                "😘", "😗", "😚", "😙", "🥲", "😋", "😛", "😜",
                "🤪", "😝", "🤑", "🤗", "🤭", "🤫", "🤔", "🤐"
            ],
            "Naturaleza": [
                "🌸", "🌺", "🌻", "🌹", "🥀", "🌷", "🌼", "🌱",
                "🪴", "🌲", "🌳", "🌴", "🌵", "🌾", "🌿", "☘️",
                "🍀", "🍁", "🍂", "🍃", "🪹", "🪺", "🌾", "💐"
            ],
            "Frutas": [
                "🍎", "🍏", "🍊", "🍋", "🍌", "🍉", "🍇", "🍓",
                "🫐", "🍈", "🍒", "🍑", "🥭", "🍍", "🥥", "🥝",
                "🍅", "🥑", "🫒", "🌶️", "🫑", "🥒", "🥬", "🥦"],
            "Bebidas": [
                "☕", "🍵", "🧃", "🥤", "🧋", "🍼", "🥛", "🍺",
                "🍻", "🍷", "🥂", "🍾", "🍹", "🍸", "🧉", "🥃"],
            "viajes": [
                "🚗", "🚕", "🚙", "🚌", "🚎", "🏎️", "🚓", "🚑",
                "🚒", "🚐", "🛻", "🚚", "🚛", "🚜", "🦯", "🦽",
                "🦼", "🛴", "🚲", "🛵", "🏍️", "🛺", "🚨", "🚔",
                "🚍", "🚘", "🚖", "🚡", "🚠", "🚟", "🚃", "🚋",
                "🚞", "🚝", "🚄", "🚅", "🚈", "🚂", "🚆", "🚇",
                "🚊", "🚉", "✈️", "🛫", "🛬", "🛩️", "💺", "🚁",
                "🛸", "🚀", "🛰️", "🚢", "⛵", "🛶", "⛴️", "🛥️"],
            "Ropa": [
                "👕", "👔", "👗", "👘", "🥻", "🩱", "🩲", "🩳",
                "👖", "👚", "👙", "🧥", "🥼", "🦺", "⛑️", "🎩",
                "🧢", "👒", "🎓", "👑", "💍", "👞", "👟", "🥾",
                "🥿", "👠", "👡", "🩰", "👢", "👜", "👝", "🎒",
                "👛", "💼", "🧳", "👓", "🕶️", "🥽", "🌂", "🧣"],
            "Trabajo": [
                "💼", "📁", "📂", "🗂️", "📋", "📊", "📈", "📉",
                "📇", "📌", "📍", "📎", "🖇️", "📏", "📐", "✂️",
                "🗃️", "🗄️", "🗑️", "🔒", "🔓", "🔐", "🔏", "🖊️"
            ],
            "Compras": [
                "🎁", "🛍️", "🛒", "💳", "🏪", "🏬", "🏢", "💰",
                "💵", "💴", "💶", "💷", "🪙", "💸", "🧾", "🎀"
            ],
            "Servicios": [
                "⚡", "💡", "🔌", "🔋", "💻", "⌨️", "🖱️", "🖥️",
                "📱", "☎️", "📞", "📟", "📠", "📺", "📻", "🎙️",
                "🔊", "🔉", "🔇", "📡", "🛜", "📶", "📳", "📴"
            ]
        }
        
        emoji_grid = ft.GridView(runs_count=8, max_extent=50, spacing=8, run_spacing=8, height=300)
        emoji_tabs = ft.Tabs(selected_index=0, scrollable=True, 
                             tabs=[ft.Tab(text=name.strip()) for name in emoji_categories.keys()])
        
        def load_emojis(category_index):
            emoji_grid.controls.clear()
            category_name = list(emoji_categories.keys())[category_index]
            emojis = emoji_categories[category_name]
            
            for emoji in emojis:
                is_selected = emoji == current_state["emoji"]
                emoji_grid.controls.append(
                    ft.Container(
                        content=ft.Text(emoji, size=28),
                        width=45,
                        height=45,
                        border_radius=8,
                        bgcolor=ft.Colors.LIGHT_BLUE_100 if is_selected else ft.Colors.WHITE,
                        border=ft.border.all(2, ft.Colors.BLUE_400 if is_selected else ft.Colors.GREY_300),
                        alignment=ft.alignment.center,
                        on_click=lambda e, em=emoji: select_emoji(em),
                        ink=True,
                    )
                )
            try:
                if emoji_grid.page:
                    emoji_grid.update()
            except:
                pass
        
        def select_emoji(emoji):
            current_state["emoji"] = emoji
            icon_preview.content.value = emoji
            preview_text.controls[0].value = f"Emoji: {emoji}"
            try:
                if icon_preview.page:
                    icon_preview.update()
                if preview_text.page:
                    preview_text.update()
            except:
                pass
            load_emojis(emoji_tabs.selected_index)
        
        emoji_tabs.on_change = lambda e: load_emojis(e.control.selected_index)
        
        # ✅ COLORES - Grilla 8x5 con colores nativos de Flet
        colors = [
            # Rojos (5 tonos)
            ft.Colors.RED_700, ft.Colors.RED_600, ft.Colors.RED_500, ft.Colors.RED_400, ft.Colors.RED_200,
            # Naranjas (5 tonos)
            ft.Colors.DEEP_ORANGE_700, ft.Colors.DEEP_ORANGE_600, ft.Colors.DEEP_ORANGE_500, ft.Colors.DEEP_ORANGE_400, ft.Colors.DEEP_ORANGE_200,
            # Amarillos (5 tonos)
            ft.Colors.AMBER_700, ft.Colors.AMBER_600, ft.Colors.AMBER_500, ft.Colors.AMBER_400, ft.Colors.AMBER_200,
            # Verdes (5 tonos)
            ft.Colors.GREEN_700, ft.Colors.GREEN_600, ft.Colors.GREEN_500, ft.Colors.GREEN_400, ft.Colors.GREEN_200,
            # Azules (5 tonos)
            ft.Colors.BLUE_700, ft.Colors.BLUE_600, ft.Colors.BLUE_500, ft.Colors.BLUE_400, ft.Colors.BLUE_200,
            # Púrpuras (5 tonos)
            ft.Colors.PURPLE_700, ft.Colors.PURPLE_600, ft.Colors.PURPLE_500, ft.Colors.PURPLE_400, ft.Colors.PURPLE_200,
            # Rosas (5 tonos)
            ft.Colors.PINK_700, ft.Colors.PINK_600, ft.Colors.PINK_500, ft.Colors.PINK_400, ft.Colors.PINK_200,
            # Grises (5 tonos)
            ft.Colors.GREY_700, ft.Colors.GREY_600, ft.Colors.GREY_500, ft.Colors.GREY_400, ft.Colors.GREY_200,
        ]
        
        color_grid = ft.GridView(
            runs_count=5,  # ✅ 5 columnas = grilla 8x5
            max_extent=50,
            spacing=10,
            run_spacing=10,
            height=400,  # ✅ Altura para 8 filas
        )
        
        def load_colors():
            color_grid.controls.clear()
            for color in colors:
                is_selected = color == current_state["color"]
                color_grid.controls.append(
                    ft.Container(
                        width=45,
                        height=45,
                        bgcolor=color,  # ✅ Color nativo de Flet
                        border_radius=22.5,
                        border=ft.border.all(
                            width=3 if is_selected else 1,
                            color=ft.Colors.BLACK if is_selected else ft.Colors.GREY_400
                        ),
                        on_click=lambda e, c=color: select_color(c),
                        ink=True,
                        tooltip=self.FLET_COLORS.get(color, ""),
                    )
                )
            try:
                if color_grid.page:
                    color_grid.update()
            except:
                pass
        
        def select_color(color):
            current_state["color"] = color
            icon_preview.bgcolor = color  # ✅ Asignación directa
            preview_text.controls[1].value = self.FLET_COLORS.get(color, "Color personalizado")
            try:
                if icon_preview.page:
                    icon_preview.update()
                if preview_text.page:
                    preview_text.update()
            except:
                pass
            load_colors()
        
        picker_container = ft.Container(visible=False)
        
        def toggle_pickers(e):
            if show_emoji_picker[0]:
                picker_container.content = ft.Column([emoji_tabs, emoji_grid], spacing=10)
                picker_container.visible = True
                load_emojis(0)
            elif show_color_picker[0]:
                picker_container.content = color_grid
                picker_container.visible = True
                load_colors()
            else:
                picker_container.visible = False
            try:
                if picker_container.page:
                    picker_container.update()
            except:
                pass
        
        emoji_checkbox = ft.Checkbox(
            label="Seleccionar emoji",
            value=False,
            on_change=lambda e: [
                show_emoji_picker.__setitem__(0, e.control.value),
                show_color_picker.__setitem__(0, False) if e.control.value else None,
                color_checkbox.__setattr__("value", False) if e.control.value else None,
                toggle_pickers(e),
            ],
        )
        
        color_checkbox = ft.Checkbox(
            label="Seleccionar color",
            value=False,
            on_change=lambda e: [
                show_color_picker.__setitem__(0, e.control.value),
                show_emoji_picker.__setitem__(0, False) if e.control.value else None,
                emoji_checkbox.__setattr__("value", False) if e.control.value else None,
                toggle_pickers(e),
            ],
        )

        def update_category(e):
            if self.is_saving:
                return
                
            if not name_field.value:
                self.show_snackbar("El nombre es obligatorio", error=True)
                return

            self.is_saving = True

            try:
                self.db.update_category(
                    category.id,
                    name=name_field.value.strip(),
                    icon=current_state["emoji"],
                    color=current_state["color"],
                    description=desc_field.value.strip() if desc_field.value else None,
                )
                
                self.close_dialog()
                self.show_snackbar("✅ Categoría actualizada")
                self._reload_view()
                
            except Exception as ex:
                self.show_snackbar(f"Error: {str(ex)}", error=True)
                self.is_saving = False

        dialog = ft.AlertDialog(
            title=ft.Text("Editar Categoría"),
            content=ft.Container(
                content=ft.Column(
                    [
                        name_field,
                        desc_field,
                        ft.Divider(height=5),
                        ft.Text("Apariencia", size=14, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Row([icon_preview, preview_text], spacing=15),
                            padding=15,
                            bgcolor=ft.Colors.GREY_50,
                            border_radius=10,
                        ),
                        ft.Row([emoji_checkbox, color_checkbox], spacing=20),
                        picker_container,
                    ],
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                    spacing=10,
                ),
                height=600,
                width=550,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.ElevatedButton(
                    "Guardar",
                    on_click=update_category,
                    style=ft.ButtonStyle(bgcolor="#667eea", color=ft.Colors.WHITE),
                ),
            ],
        )

        self.show_dialog(dialog)

    def delete_category(self, category):
        """Elimina una categoría"""
        def confirm_delete(e):
            if self.db.delete_category(category.id):
                self.close_dialog()
                self.show_snackbar("Categoría eliminada")
                self._reload_view()
            else:
                self.show_snackbar("No se puede eliminar esta categoría", error=True)

        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Estás seguro de eliminar '{category.name}'?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.TextButton("Eliminar", on_click=confirm_delete),
            ],
        )

        self.show_dialog(dialog)

    def _reload_view(self):
        """Recarga la vista correctamente"""
        try:
            new_content = self.build()
            
            if hasattr(self.page, 'controls') and len(self.page.controls) > 0:
                main_column = self.page.controls[0]
                if hasattr(main_column, 'controls') and len(main_column.controls) > 0:
                    main_container = main_column.controls[0]
                    main_container.content = new_content
            
            self.page.update()
            
        except Exception as e:
            print(f"❌ Error al recargar vista: {e}")

    def build(self) -> ft.Control:
        """Construye la vista de categorías"""
        expense_cats = self.db.get_all_categories("expense")
        income_cats = self.db.get_all_categories("income")

        tabs_content = []

        expense_tiles = [self._create_category_tile(cat) for cat in expense_cats]
        tabs_content.append(
            ft.Tab(
                text="Gastos",
                icon=ft.Icons.TRENDING_DOWN,
                content=ft.Column(expense_tiles, scroll=ft.ScrollMode.AUTO),
            )
        )

        income_tiles = [self._create_category_tile(cat) for cat in income_cats]
        tabs_content.append(
            ft.Tab(
                text="Ingresos",
                icon=ft.Icons.TRENDING_UP,
                content=ft.Column(income_tiles, scroll=ft.ScrollMode.AUTO),
            )
        )

        category_tabs = ft.Tabs(tabs=tabs_content, expand=True)

        return ft.Column(
            [
                ft.Text("🏷️ Categorías", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Text(
                        "💡 Tip: Haz clic en el icono 🏷️ para gestionar las palabras clave de cada categoría",
                        size=12,
                        color=ft.Colors.GREY_600,
                        italic=True,
                    ),
                    padding=10,
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=8,
                ),
                ft.Divider(),
                category_tabs,
            ],
            expand=True,
            spacing=10,
        )