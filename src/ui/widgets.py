"""
Widgets reutilizables para las vistas
Archivo: src/ui/widgets.py

Este módulo contiene todos los widgets personalizados que son utilizados
por múltiples vistas de la aplicación. Incluye:
- Selectores de mes
- Tarjetas de estadísticas
- Tiles de transacciones
- Gráficos y barras de progreso
"""

import flet as ft
from datetime import datetime
from typing import Dict, Callable, Optional
from src.utils.config import Config


class MonthSelector(ft.Row):
    """
    Widget para seleccionar mes y año con flechas de navegación.
    
    Attributes:
        month (int): Mes actual (1-12)
        year (int): Año actual
        on_previous (Callable): Callback al presionar flecha anterior
        on_next (Callable): Callback al presionar flecha siguiente
        month_name (str): Nombre del mes en texto
    """

    def __init__(
        self,
        month: int,
        year: int,
        on_previous: Callable,
        on_next: Callable,
        month_name: str
    ):
        super().__init__()
        self.alignment = ft.MainAxisAlignment.CENTER
        self.controls = [
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK_IOS,
                on_click=on_previous,
                icon_size=20,
                tooltip="Mes anterior"
            ),
            ft.Text(
                f"{month_name} {year}",
                size=22,
                weight=ft.FontWeight.BOLD,
                expand=True,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.IconButton(
                icon=ft.Icons.ARROW_FORWARD_IOS,
                on_click=on_next,
                icon_size=20,
                tooltip="Mes siguiente"
            ),
        ]


class MiniStatCard(ft.Container):
    """
    Tarjeta pequeña de estadística con ícono, valor y subtítulo.
    
    Args:
        title (str): Título de la estadística
        value (str): Valor a mostrar (ej: "S/ 150.00")
        icon: Ícono de Flet a mostrar
        color (str): Color del ícono y valor
        subtitle (str, optional): Subtítulo adicional
    """

    def __init__(
        self, 
        title: str, 
        value: str, 
        icon, 
        color: str, 
        subtitle: str = ""
    ):
        content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(icon, size=24, color=color),
                        ft.Text(title, size=11, color=ft.Colors.GREY_600),
                    ],
                    spacing=5,
                ),
                ft.Text(
                    value,
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=color,
                ),
                (
                    ft.Text(subtitle, size=10, color=ft.Colors.GREY_500)
                    if subtitle
                    else ft.Container(height=1)
                ),
            ],
            spacing=5,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        )

        super().__init__(
            content=content,
            padding=15,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            expand=True,
            border=ft.border.all(1, ft.Colors.GREY_200),
        )


class TopExpenseTile(ft.Container):
    """
    Tile para mostrar un gasto en el top 3.
    
    Args:
        expense (Dict): Diccionario con datos del gasto:
            - description (str): Descripción del gasto
            - amount (float): Monto
            - category_name (str): Nombre de la categoría
            - category_icon (str): Emoji de la categoría
            - category_color (str): Color de la categoría
            - date (datetime): Fecha del gasto
        rank (int): Posición en el ranking (1, 2, 3)
    """

    def __init__(self, expense: Dict, rank: int):
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}

        try:
            content = ft.Row(
                [
                    ft.Text(medals.get(rank, ""), size=24),
                    ft.Container(
                        content=ft.Text(
                            expense.get("category_icon", "💰"), size=20
                        ),
                        width=45,
                        height=45,
                        border_radius=22,
                        bgcolor=f"{expense.get('category_color', '#3b82f6')}20",
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                expense.get("description", "Sin descripción"),
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                f"{expense.get('category_name', 'Sin categoría')} • {expense.get('date', datetime.now()).strftime('%d %b')}",
                                size=11,
                                color=ft.Colors.GREY_600,
                            ),
                        ],
                        expand=True,
                        spacing=2,
                    ),
                    ft.Text(
                        f"{Config.CURRENCY_SYMBOL} {expense.get('amount', 0):.2f}",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color="#ef4444",
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )

            super().__init__(
                content=content,
                padding=10,
                border_radius=8,
                bgcolor="#f9fafb",
            )
        except Exception as e:
            print(f"❌ Error creando TopExpenseTile: {e}")
            super().__init__()


class CompactCategoryBar(ft.Row):
    """
    Barra compacta para mostrar una categoría con su gasto y progreso.
    
    Args:
        category (Dict): Diccionario con datos de la categoría:
            - category (str): Nombre de la categoría
            - icon (str): Emoji de la categoría
            - color (str): Color de la categoría
            - total (float): Total gastado
    """

    def __init__(self, category: Dict):
        total = category.get("total", 0)
        max_for_bar = 1000  # Valor máximo para normalizar la barra

        super().__init__()
        self.spacing = 10
        self.controls = [
            ft.Text(category.get("icon", "💰"), size=20),
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                category.get("category", "Sin categoría"),
                                size=13,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                f"{Config.CURRENCY_SYMBOL} {total:.2f}",
                                size=13,
                                color=ft.Colors.GREY_700,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.ProgressBar(
                        value=min(total / max_for_bar, 1),
                        color=category.get("color", "#3b82f6"),
                        bgcolor="#e5e7eb",
                        height=6,
                    ),
                ],
                expand=True,
                spacing=5,
            ),
        ]


class CompactTransactionTile(ft.Container):
    """
    Tile compacto para mostrar una transacción.
    
    Args:
        transaction: Objeto Transaction de la base de datos
        category: Objeto Category de la base de datos (puede ser None)
    """

    def __init__(self, transaction, category):
        # Valores seguros con manejo de None
        category_icon = "💰"
        category_name = "Sin categoría"
        category_color = "#3b82f6"

        if category:
            category_icon = str(category.icon) if category.icon else "💰"
            category_name = str(category.name) if category.name else "Sin categoría"
            category_color = str(category.color) if category.color else "#3b82f6"

        description = (
            str(transaction.description)
            if transaction.description
            else "Sin descripción"
        )
        amount = float(transaction.amount) if transaction.amount else 0.0
        date_str = transaction.date.strftime("%d %b") if transaction.date else ""

        content = ft.Row(
            [
                ft.Container(
                    content=ft.Text(category_icon, size=18),
                    width=40,
                    height=40,
                    border_radius=20,
                    bgcolor=f"{category_color}20",
                    alignment=ft.alignment.center,
                ),
                ft.Column(
                    [
                        ft.Text(
                            description,
                            size=13,
                            weight=ft.FontWeight.BOLD,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Text(
                            f"{category_name} • {date_str}",
                            size=11,
                            color=ft.Colors.GREY_600,
                        ),
                    ],
                    expand=True,
                    spacing=2,
                ),
                ft.Text(
                    f"- {Config.CURRENCY_SYMBOL} {amount:.2f}",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color="#ef4444",
                ),
            ],
            spacing=10,
        )

        super().__init__(
            content=content,
            padding=10,
            border_radius=8,
            bgcolor="#f9fafb",
        )


class ProjectionCard(ft.Container):
    """
    Tarjeta de proyección mensual de gastos.
    
    Muestra el gasto actual vs el proyectado para fin de mes.
    
    Args:
        daily_stats (Dict): Estadísticas diarias con:
            - projected_monthly (float): Proyección del mes
            - total_expenses (float): Gastos actuales
            - daily_average (float): Promedio diario
            - days_in_month (int): Días del mes
            - days_passed (int): Días transcurridos
        summary (Dict): Resumen mensual (puede no usarse directamente)
    """

    def __init__(self, daily_stats: Dict, summary: Dict):
        projected = daily_stats.get("projected_monthly", 0)
        current = daily_stats.get("total_expenses", 0)
        days_left = daily_stats.get("days_in_month", 30) - daily_stats.get(
            "days_passed", 1
        )

        content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.TRENDING_UP, size=22, color="#8b5cf6"),
                        ft.Text(
                            "📈 Proyección del Mes",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Divider(height=10),
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(
                                    "Gasto Actual",
                                    size=12,
                                    color=ft.Colors.GREY_600,
                                ),
                                ft.Text(
                                    f"{Config.CURRENCY_SYMBOL} {current:.2f}",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                            expand=True,
                        ),
                        ft.Icon(
                            ft.Icons.ARROW_FORWARD, color=ft.Colors.GREY_400
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    "Proyectado",
                                    size=12,
                                    color=ft.Colors.GREY_600,
                                ),
                                ft.Text(
                                    f"{Config.CURRENCY_SYMBOL} {projected:.2f}",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color="#8b5cf6",
                                ),
                            ],
                            expand=True,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                ),
                ft.Container(
                    content=ft.Text(
                        f"⏱️ Quedan {days_left} días • Promedio diario: {Config.CURRENCY_SYMBOL} {daily_stats.get('daily_average', 0):.2f}",
                        size=11,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=8,
                    bgcolor="#f3f4f6",
                    border_radius=8,
                ),
            ],
            spacing=10,
        )

        super().__init__(
            content=content,
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
        )


class EmptyStateWidget(ft.Container):
    """
    Widget para mostrar un estado vacío con ícono y mensaje.
    
    Args:
        icon: Ícono de Flet a mostrar
        message (str): Mensaje a mostrar
        action_button (ft.Control, optional): Botón de acción opcional
    """

    def __init__(
        self,
        icon,
        message: str,
        action_button: Optional[ft.Control] = None
    ):
        controls = [
            ft.Icon(icon, size=64, color=ft.Colors.GREY_400),
            ft.Text(
                message,
                size=16,
                color=ft.Colors.GREY_600,
                text_align=ft.TextAlign.CENTER,
            ),
        ]

        if action_button:
            controls.extend([
                ft.Container(height=10),
                action_button
            ])

        content = ft.Column(
            controls,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        super().__init__(
            content=content,
            padding=40,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
        )


class StatCard(ft.Container):
    """
    Tarjeta de estadística con título, valor y descripción opcional.
    
    Args:
        title (str): Título de la estadística
        value (str): Valor principal
        icon: Ícono de Flet
        color (str): Color del tema
        description (str, optional): Descripción adicional
    """

    def __init__(
        self,
        title: str,
        value: str,
        icon,
        color: str,
        description: str = ""
    ):
        content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(icon, size=32, color=color),
                        ft.Column(
                            [
                                ft.Text(
                                    title,
                                    size=12,
                                    color=ft.Colors.GREY_600,
                                ),
                                ft.Text(
                                    value,
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color=color,
                                ),
                            ],
                            expand=True,
                        ),
                    ],
                    spacing=10,
                ),
                (
                    ft.Text(
                        description,
                        size=11,
                        color=ft.Colors.GREY_500,
                    )
                    if description
                    else ft.Container(height=1)
                ),
            ],
            spacing=5,
        )

        super().__init__(
            content=content,
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.GREY_200),
        )


class CategoryIcon(ft.Container):
    """
    Widget para mostrar el ícono de una categoría con su color.
    
    Args:
        icon (str): Emoji o ícono
        color (str): Color de fondo
        size (int): Tamaño del contenedor
    """

    def __init__(self, icon: str, color: str, size: int = 50):
        super().__init__(
            content=ft.Text(icon, size=size * 0.6),
            width=size,
            height=size,
            border_radius=size / 2,
            bgcolor=f"{color}30",
            alignment=ft.alignment.center,
        )