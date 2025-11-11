"""
Componentes UI Reutilizables
Archivo: src/ui/components.py
"""

import flet as ft
from datetime import datetime
from typing import Optional, Callable

# Importa List de la librería typing
from typing import List


class SummaryCard(ft.Container):
    """Tarjeta de resumen para mostrar métricas"""

    def __init__(
        self,
        title: str,
        value: str,
        icon: str,
        color: str,
        subtitle: Optional[str] = None,
        on_click: Optional[Callable] = None,
    ):
        self.title = title
        self.value = value
        self.icon_name = icon
        self.color = color
        self.subtitle = subtitle

        # Contenido de la tarjeta
        content_items = [
            ft.Icon(icon, size=40, color=color),
            ft.Text(
                title, size=14, color=ft.Colors.GREY_700, text_align=ft.TextAlign.CENTER
            ),
            ft.Text(
                value,
                size=20,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),
        ]

        if subtitle:
            content_items.append(
                ft.Text(
                    subtitle,
                    size=12,
                    color=ft.Colors.GREY_600,
                    text_align=ft.TextAlign.CENTER,
                )
            )

        super().__init__(
            content=ft.Column(
                content_items,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.SURFACE,
            expand=True,
            height=140 if subtitle else 120,
            on_click=on_click,
            ink=True if on_click else False,
        )


class TransactionTile(ft.Container):
    """Tile para mostrar una transacción"""

    def __init__(
        self,
        transaction,
        category,
        on_click: Optional[Callable] = None,
        show_date: bool = True,
        show_delete: bool = False,
        on_delete: Optional[Callable] = None,
    ):
        is_income = transaction.transaction_type == "income"

        # Columna de información
        info_column_items = [
            ft.Text(
                transaction.description,
                weight=ft.FontWeight.BOLD,
                size=14,
                max_lines=2,
                overflow=ft.TextOverflow.ELLIPSIS,
            )
        ]

        # Añadir categoría
        category_text = category.name
        if show_date:
            category_text += f" • {transaction.date.strftime('%d/%m/%Y')}"

        info_column_items.append(
            ft.Text(category_text, size=12, color=ft.Colors.GREY_700)
        )

        # Añadir notas si existen
        if transaction.notes:
            info_column_items.append(
                ft.Text(
                    transaction.notes,
                    size=11,
                    italic=True,
                    color=ft.Colors.GREY_500,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                )
            )

        # Fila principal
        main_row_items = [
            # Icono de categoría
            ft.Container(
                content=ft.Text(category.icon, size=24),
                width=50,
                height=50,
                border_radius=25,
                bgcolor=category.color + "30",
                alignment=ft.alignment.center,
            ),
            # Información
            ft.Column(
                info_column_items,
                expand=True,
                spacing=2,
            ),
            # Monto
            ft.Text(
                f"{'+ ' if is_income else '- '}S/ {transaction.amount:.2f}",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.GREEN if is_income else ft.Colors.RED,
            ),
        ]

        # Añadir botón de eliminar si se solicita
        if show_delete and on_delete:
            main_row_items.append(
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_size=18,
                    on_click=on_delete,
                    tooltip="Eliminar",
                )
            )

        super().__init__(
            content=ft.Row(
                main_row_items,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=10,
            border_radius=10,
            bgcolor=ft.Colors.SURFACE,
            margin=ft.margin.only(bottom=5),
            on_click=on_click,
            ink=True if on_click else False,
        )


class CategoryTile(ft.Container):
    """Tile para mostrar una categoría"""

    def __init__(
        self,
        category,
        on_edit: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        show_actions: bool = True,
    ):
        # Acciones
        actions = []
        if show_actions:
            if on_edit:
                actions.append(
                    ft.IconButton(
                        icon=ft.Icons.EDIT,
                        icon_size=20,
                        tooltip="Editar",
                        on_click=on_edit,
                        disabled=category.is_default,
                    )
                )
            if on_delete:
                actions.append(
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_size=20,
                        tooltip="Eliminar",
                        on_click=on_delete,
                        disabled=category.is_default,
                    )
                )

        super().__init__(
            content=ft.Row(
                [
                    # Icono
                    ft.Container(
                        content=ft.Text(category.icon, size=32),
                        width=60,
                        height=60,
                        border_radius=30,
                        bgcolor=category.color + "30",
                        alignment=ft.alignment.center,
                    ),
                    # Información
                    ft.Column(
                        [
                            ft.Text(category.name, size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(
                                category.description or "Sin descripción",
                                size=12,
                                color=ft.Colors.GREY_600,
                            ),
                        ],
                        expand=True,
                        spacing=2,
                    ),
                    # Acciones
                    ft.Row(actions) if actions else ft.Container(),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.SURFACE,
            margin=ft.margin.only(bottom=10),
        )


class MonthSelector(ft.Row):
    """Selector de mes con flechas"""

    def __init__(self, year: int, month: int, on_previous: Callable, on_next: Callable):
        month_names = [
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre",
        ]

        super().__init__(
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=on_previous,
                    tooltip="Mes anterior",
                ),
                ft.Text(
                    f"{month_names[month - 1]} {year}",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    expand=True,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.IconButton(
                    icon=ft.Icons.ARROW_FORWARD,
                    on_click=on_next,
                    tooltip="Mes siguiente",
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )


class EmptyState(ft.Container):
    """Estado vacío con icono y mensaje"""

    def __init__(
        self,
        icon: str,
        title: str,
        subtitle: Optional[str] = None,
        action_text: str = "",
        on_action: Optional[Callable] = None,
    ):
        content_items = [
            ft.Icon(icon, size=64, color=ft.Colors.GREY_400),
            ft.Text(
                title, size=18, color=ft.Colors.GREY_600, weight=ft.FontWeight.BOLD
            ),
        ]

        if subtitle:
            content_items.append(
                ft.Text(
                    subtitle,
                    size=14,
                    color=ft.Colors.GREY_500,
                    text_align=ft.TextAlign.CENTER,
                )
            )

        if action_text and on_action:
            content_items.append(
                ft.ElevatedButton(
                    action_text,
                    on_click=on_action,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.BLUE_700,
                        color=ft.Colors.WHITE,
                    ),
                )
            )

        super().__init__(
            content=ft.Column(
                content_items,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=40,
            alignment=ft.alignment.center,
        )


class LoadingIndicator(ft.Container):
    """Indicador de carga"""

    def __init__(self, message: str = "Cargando..."):
        super().__init__(
            content=ft.Column(
                [
                    ft.ProgressRing(),
                    ft.Text(message, size=14, color=ft.Colors.GREY_600),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=40,
            alignment=ft.alignment.center,
        )


class StatisticCard(ft.Container):
    """Tarjeta para mostrar estadística con comparación"""

    def __init__(
        self,
        title: str,
        value: str,
        change_percentage: Optional[float] = None,
        icon: Optional[str] = None,
        color: Optional[str] = None,
    ):
        content_items = [
            ft.Text(title, size=14, color=ft.Colors.GREY_700),
            ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
        ]

        # Añadir indicador de cambio si existe
        content_items: List[ft.Control] = []
        if change_percentage is not None:
            is_positive = change_percentage >= 0
            content_items.append(
                ft.Row(
                    [
                        ft.Icon(
                            (
                                ft.Icons.ARROW_UPWARD
                                if is_positive
                                else ft.Icons.ARROW_DOWNWARD
                            ),
                            size=16,
                            color=ft.Colors.GREEN if is_positive else ft.Colors.RED,
                        ),
                        ft.Text(
                            f"{abs(change_percentage):.1f}%",
                            size=12,
                            color=ft.Colors.GREEN if is_positive else ft.Colors.RED,
                        ),
                    ],
                    spacing=5,
                )
            )

        # Añadir icono si existe
        if icon:
            row_items = [
                ft.Column(content_items, expand=True, spacing=5),
                ft.Icon(icon, size=40, color=color or ft.Colors.BLUE_700),
            ]
            content = ft.Row(row_items, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        else:
            content = ft.Column(content_items, spacing=5)

        super().__init__(
            content=content,
            padding=20,
            border_radius=10,
            bgcolor=ft.Colors.SURFACE,
            expand=True,
        )


class ProgressIndicator(ft.Container):
    """Indicador de progreso con etiqueta"""

    def __init__(
        self,
        title: str,
        value: float,  # 0.0 a 1.0
        current_value: Optional[str] = None,
        target_value: Optional[str] = None,
        color: Optional[str] = None,
    ):
        # Determinar color automáticamente si no se proporciona
        if not color:
            if value >= 0.8:
                color = ft.Colors.GREEN
            elif value >= 0.5:
                color = ft.Colors.BLUE
            elif value >= 0.3:
                color = ft.Colors.ORANGE
            else:
                color = ft.Colors.RED

        content_items = [
            ft.Row(
                [
                    ft.Text(title, size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        f"{value * 100:.0f}%",
                        size=14,
                        color=ft.Colors.GREY_600,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.ProgressBar(
                value=max(0, min(value, 1)),
                color=color,
                bgcolor=ft.Colors.GREY_300,
                height=10,
            ),
        ]

        if current_value and target_value:
            content_items.append(
                ft.Row(
                    [
                        ft.Text(
                            f"Actual: {current_value}",
                            size=12,
                            color=ft.Colors.GREY_600,
                        ),
                        ft.Text(
                            f"Meta: {target_value}", size=12, color=ft.Colors.GREY_600
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            )

        super().__init__(
            content=ft.Column(content_items, spacing=5),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.SURFACE,
        )


class ChipButton(ft.Container):
    """Botón tipo chip para filtros o categorías"""

    def __init__(
        self,
        text: str,
        icon: Optional[str] = None,
        selected: bool = False,
        on_click: Optional[Callable] = None,
    ):
        content_items = []

        if icon:
            content_items.append(ft.Icon(icon, size=16))

        content_items.append(ft.Text(text, size=14))

        super().__init__(
            content=ft.Row(content_items, spacing=5),
            padding=ft.padding.symmetric(horizontal=15, vertical=8),
            border_radius=20,
            bgcolor=ft.Colors.BLUE_700 if selected else ft.Colors.SURFACE,
            border=ft.border.all(1, ft.Colors.BLUE_700) if selected else None,
            on_click=on_click,
            ink=True,
        )

        # Cambiar color del texto si está seleccionado
        if selected:
            for item in content_items:
                if isinstance(item, ft.Text):
                    item.color = ft.Colors.WHITE
                elif isinstance(item, ft.Icon):
                    item.color = ft.Colors.WHITE
