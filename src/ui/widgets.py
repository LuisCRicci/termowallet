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
from typing import Dict, Callable, Optional, List  
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
    ⭐ CORREGIDO: Detecta tipo de transacción y muestra color/signo correcto
    
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
        
        # ⭐ CORRECCIÓN: Detectar tipo de transacción
        transaction_type = (
            str(transaction.transaction_type)
            if hasattr(transaction, 'transaction_type') and transaction.transaction_type
            else "expense"
        )
        is_income = transaction_type == "income"

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
                # ⭐ CORRECCIÓN: Mostrar signo y color según el tipo
                ft.Text(
                    f"{'+ ' if is_income else '- '}{Config.CURRENCY_SYMBOL} {amount:.2f}",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color="#22c55e" if is_income else "#ef4444",
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
        
# ========== AGREGAR ESTOS WIDGETS AL FINAL DE widgets.py ==========

class BudgetProgressCard(ft.Container):
    """
    Tarjeta que muestra el progreso de un aspecto del presupuesto.
    
    Args:
        title (str): Título (ej: "Gastos", "Ahorros")
        goal (float): Meta establecida
        current (float): Valor actual
        icon: Ícono de Flet
        color (str): Color del tema
        is_reversed (bool): Si True, más es mejor (ej: ingresos)
    """

    def __init__(
        self,
        title: str,
        goal: float,
        current: float,
        icon,
        color: str,
        is_reversed: bool = False
    ):
        progress = (current / goal * 100) if goal > 0 else 0
        remaining = goal - current

        # Determinar estado
        if is_reversed:
            # Para ingresos/ahorros: más es mejor
            if progress >= 100:
                status_color = "#22c55e"
                status_icon = ft.Icons.CHECK_CIRCLE
                status_text = "¡Meta alcanzada!"
            elif progress >= 75:
                status_color = "#3b82f6"
                status_icon = ft.Icons.TRENDING_UP
                status_text = f"{progress:.1f}% completado"
            else:
                status_color = "#f59e0b"
                status_icon = ft.Icons.SCHEDULE
                status_text = f"{progress:.1f}% completado"
        else:
            # Para gastos: menos es mejor
            if progress >= 100:
                status_color = "#ef4444"
                status_icon = ft.Icons.WARNING
                status_text = f"¡{progress - 100:.1f}% excedido!"
            elif progress >= 90:
                status_color = "#f59e0b"
                status_icon = ft.Icons.ERROR_OUTLINE
                status_text = f"{progress:.1f}% usado"
            else:
                status_color = "#22c55e"
                status_icon = ft.Icons.CHECK_CIRCLE_OUTLINE
                status_text = f"{progress:.1f}% usado"

        content = ft.Column(
            [
                # Encabezado
                ft.Row(
                    [
                        ft.Icon(icon, size=28, color=color),
                        ft.Column(
                            [
                                ft.Text(title, size=14, color=ft.Colors.GREY_600),
                                ft.Text(
                                    f"{Config.CURRENCY_SYMBOL} {current:.2f}",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color=color,
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                    ],
                    spacing=10,
                ),
                # Barra de progreso
                ft.Column(
                    [
                        ft.ProgressBar(
                            value=min(progress / 100, 1.0),
                            color=status_color,
                            bgcolor=ft.Colors.GREY_200,
                            height=8,
                        ),
                        ft.Row(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(
                                            status_icon, 
                                            size=16, 
                                            color=status_color
                                        ),
                                        ft.Text(
                                            status_text,
                                            size=12,
                                            color=status_color,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                    ],
                                    spacing=5,
                                ),
                                ft.Text(
                                    f"Meta: {Config.CURRENCY_SYMBOL} {goal:.2f}",
                                    size=11,
                                    color=ft.Colors.GREY_600,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    ],
                    spacing=5,
                ),
                # Restante
                ft.Container(
                    content=ft.Text(
                        f"{'Faltan' if remaining > 0 else 'Excedido en'} {Config.CURRENCY_SYMBOL} {abs(remaining):.2f}",
                        size=12,
                        color=ft.Colors.GREY_700,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=8,
                    bgcolor=ft.Colors.GREY_100,
                    border_radius=8,
                ),
            ],
            spacing=12,
        )

        super().__init__(
            content=content,
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.GREY_200),
        )


class BudgetAlertBanner(ft.Container):
    """
    Banner de alerta para el presupuesto.
    
    Args:
        alert (Dict): Diccionario con:
            - type (str): "warning", "danger", "success", "info"
            - message (str): Mensaje
            - icon (str): Emoji
    """

    def __init__(self, alert: Dict):
        alert_type = alert.get("type", "info")
        
        colors = {
            "danger": {"bg": "#fee2e2", "border": "#ef4444", "text": "#991b1b"},
            "warning": {"bg": "#fef3c7", "border": "#f59e0b", "text": "#92400e"},
            "success": {"bg": "#d1fae5", "border": "#10b981", "text": "#065f46"},
            "info": {"bg": "#dbeafe", "border": "#3b82f6", "text": "#1e40af"},
        }

        theme = colors.get(alert_type, colors["info"])

        content = ft.Row(
            [
                ft.Text(alert.get("icon", "ℹ️"), size=24),
                ft.Text(
                    alert.get("message", ""),
                    size=14,
                    color=theme["text"],
                    weight=ft.FontWeight.BOLD,
                    expand=True,
                ),
            ],
            spacing=12,
        )

        super().__init__(
            content=content,
            padding=15,
            bgcolor=theme["bg"],
            border_radius=10,
            border=ft.border.all(2, theme["border"]),
            margin=ft.margin.only(bottom=10),
        )


class BudgetSummaryCard(ft.Container):
    """
    Tarjeta resumen del presupuesto mensual.
    
    Args:
        budget_status (Dict): Estado del presupuesto del mes
    """

    def __init__(self, budget_status: Dict):
        if not budget_status.get("budget_exists"):
            content = ft.Column(
                [
                    ft.Icon(
                        ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
                        size=48,
                        color=ft.Colors.GREY_400,
                    ),
                    ft.Text(
                        "No hay presupuesto configurado",
                        size=16,
                        color=ft.Colors.GREY_600,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )
        else:
            expense_progress = budget_status.get("expense_progress", 0)
            is_over = expense_progress >= 100

            content = ft.Column(
                [
                    # Título
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.ACCOUNT_BALANCE_WALLET,
                                size=28,
                                color="#667eea",
                            ),
                            ft.Text(
                                "Presupuesto del Mes",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.Divider(height=10),
                    # Estado de gastos
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text(
                                            "Gastos",
                                            size=13,
                                            color=ft.Colors.GREY_600,
                                        ),
                                        ft.Text(
                                            f"{expense_progress:.1f}%",
                                            size=16,
                                            weight=ft.FontWeight.BOLD,
                                            color="#ef4444" if is_over else "#22c55e",
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.ProgressBar(
                                    value=min(expense_progress / 100, 1.0),
                                    color="#ef4444" if is_over else "#22c55e",
                                    bgcolor=ft.Colors.GREY_200,
                                    height=6,
                                ),
                                ft.Row(
                                    [
                                        ft.Text(
                                            f"{Config.CURRENCY_SYMBOL} {budget_status.get('actual_expenses', 0):.2f}",
                                            size=12,
                                            color=ft.Colors.GREY_700,
                                        ),
                                        ft.Text(
                                            f"de {Config.CURRENCY_SYMBOL} {budget_status.get('expense_limit', 0):.2f}",
                                            size=12,
                                            color=ft.Colors.GREY_500,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                            ],
                            spacing=5,
                        ),
                        padding=10,
                        bgcolor=ft.Colors.GREY_50,
                        border_radius=8,
                    ),
                    # Días restantes
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.CALENDAR_TODAY, size=16, color=ft.Colors.GREY_500),
                            ft.Text(
                                f"Quedan {budget_status.get('days_left', 0)} días del mes",
                                size=12,
                                color=ft.Colors.GREY_600,
                            ),
                        ],
                        spacing=5,
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


class BudgetHistoryTile(ft.Container):
    """
    Tile para mostrar un mes en el historial de presupuestos.
    ✅ CORREGIDO: Detecta correctamente si hay actividad en el mes
    
    Args:
        budget_history (Dict): Datos del presupuesto histórico
    """

    def __init__(self, budget_history: Dict):
        expense_progress = budget_history.get("expense_progress", 0)
        savings_progress = budget_history.get("savings_progress", 0)
        actual_expenses = budget_history.get("actual_expenses", 0)
        actual_income = budget_history.get("actual_income", 0)
        
        # ✅ CORREGIDO: Determinar estado general de forma más precisa
        if not budget_history.get("budget_exists"):
            status_icon = ft.Icons.HELP_OUTLINE
            status_color = ft.Colors.GREY_400
            status_text = "Sin presupuesto"
        elif actual_expenses == 0 and actual_income == 0:
            # No hay movimientos en ese mes
            status_icon = ft.Icons.REMOVE_CIRCLE_OUTLINE
            status_color = ft.Colors.GREY_400
            status_text = "Sin actividad"
        elif expense_progress >= 100:
            status_icon = ft.Icons.CANCEL
            status_color = "#ef4444"
            status_text = "Excedido"
        elif expense_progress >= 90:
            status_icon = ft.Icons.WARNING
            status_color = "#f59e0b"
            status_text = "Ajustado"
        else:
            status_icon = ft.Icons.CHECK_CIRCLE
            status_color = "#22c55e"
            status_text = "Cumplido"

        content = ft.Row(
            [
                # Ícono de estado
                ft.Container(
                    content=ft.Icon(status_icon, size=24, color=status_color),
                    width=50,
                    height=50,
                    border_radius=25,
                    bgcolor=f"{status_color}20",
                    alignment=ft.alignment.center,
                ),
                # Detalles
                ft.Column(
                    [
                        ft.Text(
                            budget_history.get("month_name", ""),
                            size=15,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            status_text,
                            size=12,
                            color=status_color,
                        ),
                    ],
                    expand=True,
                    spacing=2,
                ),
                # Estadísticas
                ft.Column(
                    [
                        ft.Text(
                            f"Gastos: {expense_progress:.0f}%",
                            size=11,
                            color=ft.Colors.GREY_600,
                        ),
                        ft.Text(
                            f"Ahorros: {savings_progress:.0f}%",
                            size=11,
                            color=ft.Colors.GREY_600,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                    spacing=2,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        super().__init__(
            content=content,
            padding=15,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            margin=ft.margin.only(bottom=8),
            border=ft.border.all(1, ft.Colors.GREY_200),
        )
        
class EmojiPickerDialog(ft.AlertDialog):
    def __init__(self, on_select):
        super().__init__()
        self.on_select = on_select

        self.emoji_categories = {
            "Comida": ["🍔","🍕","🍟","🌮","🍜","🥗","🍱","🍩","🍦","🍫"],
            "Finanzas": ["💰","💵","💳","📈","📉","🏦","💲"],
            "Transporte": ["🚗","🚕","🚌","🚙","🚲","✈️","🚆"],
            "Casa": ["🏠","🏡","🛋️","💡","🚿","🧹"],
            "Entretenimiento": ["🎮","🎧","📺","🎟️","🎲", "🎤"],
        }

        self.category_tabs = ft.Tabs(
            tabs=[ft.Tab(text=cat) for cat in self.emoji_categories.keys()],
            selected_index=0,
            on_change=self.update_emojis,
        )

        self.emoji_grid = ft.GridView(
            expand=True,
            runs_count=6,
            max_extent=60,
            child_aspect_ratio=1,
            spacing=5,
            run_spacing=5,
        )

        self.content = ft.Container(
            padding=20,
            width=430,
            height=420,
            content=ft.Column(
                [
                    ft.Text("Selecciona un emoji", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    self.category_tabs,
                    ft.Container(height=10),
                    self.emoji_grid,
                ],
                expand=True,
            ),
        )

        self.update_emojis(None)

    def update_emojis(self, e):
        self.emoji_grid.controls.clear()
        category = list(self.emoji_categories.keys())[self.category_tabs.selected_index]
        for emoji in self.emoji_categories[category]:
            self.emoji_grid.controls.append(
                ft.TextButton(
                    emoji,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=10,
                        bgcolor="white"
                    ),
                    on_click=lambda e, em=emoji: self.select_emoji(em),
                )
            )
        self.update()

    def select_emoji(self, emoji):
        self.on_select(emoji)
        self.open = False
        self.update()
        
class ColorPickerDialog(ft.AlertDialog):
    def __init__(self, initial="#3b82f6", on_select=None):
        super().__init__()
        self.on_select = on_select
        self.selected = initial

        self.colors = [
            "#ef4444","#f97316","#f59e0b","#eab308","#84cc16",
            "#22c55e","#10b981","#06b6d4","#0ea5e9","#3b82f6",
            "#6366f1","#8b5cf6","#a855f7","#d946ef","#ec4899",
            "#f43f5e","#6b7280","#374151","#000000","#ffffff",
            "#fecaca","#fed7aa","#fde68a","#fef08a","#dcfce7",
            "#bbf7d0","#99f6e4","#bfdbfe","#c7d2fe","#ddd6fe",
            "#fae8ff","#fce7f3","#ffe4e6","#d1d5db","#e5e7eb",
            "#f3f4f6","#e6e6e6","#b91c1c","#7c2d12","#92400e",
            "#065f46","#0f766e","#0369a1"
        ]

        self.hex_input = ft.TextField(
            label="Código HEX",
            value=self.selected,
            on_submit=self.validate_hex,
            width=150
        )

        self.color_grid = ft.GridView(
            runs_count=8,
            max_extent=45,
            spacing=5,
            run_spacing=5,
            child_aspect_ratio=1,
        )

        for c in self.colors:
            self.color_grid.controls.append(
                ft.Container(
                    width=35,
                    height=35,
                    bgcolor=c,
                    border_radius=50,
                    on_click=lambda e, col=c: self.pick_color(col),
                    border=ft.border.all(2, ft.Colors.BLACK if c==self.selected else ft.Colors.WHITE)
                )
            )

        self.content = ft.Container(
            width=420,
            height=430,
            padding=20,
            content=ft.Column(
                [
                    ft.Text("Seleccionar color", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Row([self.hex_input]),
                    ft.Container(height=10),
                    self.color_grid,
                ],
                expand=True
            )
        )

    def pick_color(self, color):
        self.selected = color
        if self.on_select:
            self.on_select(color)
        self.open = False
        self.update()

    def validate_hex(self, e):
        v = self.hex_input.value.strip()
        if len(v) == 7 and v.startswith("#"):
            self.pick_color(v)
            
"""
✅ NUEVO WIDGET: CategoryBudgetDistributionEditor
Agregar a: src/ui/widgets.py (al final del archivo)
"""

class CategoryBudgetTile(ft.Container):
    """
    Tile individual para editar el porcentaje de una categoría
    
    Args:
        category_data: Dict con datos de la categoría
        on_change: Callback cuando cambia el porcentaje
    """
    
    def __init__(self, category_data: dict, on_change: Callable):  # ✅ Usar dict minúscula
        self.category_data = category_data
        self.on_change = on_change
        
        # Campo de porcentaje
        self.percentage_field = ft.TextField(
            value=str(category_data["percentage"]),
            width=80,
            text_align=ft.TextAlign.CENTER,
            suffix_text="%",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._handle_change,
            bgcolor=ft.Colors.WHITE,
        )
        
        # Barra de progreso del uso actual
        usage_percent = category_data.get("usage_percent", 0)
        is_over = category_data.get("is_over", False)
        
        content = ft.Column(
            [
                ft.Row(
                    [
                        # Ícono de categoría
                        ft.Container(
                            content=ft.Text(
                                category_data["icon"], 
                                size=24
                            ),
                            width=50,
                            height=50,
                            bgcolor=f"{category_data['color']}30",
                            border_radius=25,
                            alignment=ft.alignment.center,
                        ),
                        # Info de categoría
                        ft.Column(
                            [
                                ft.Text(
                                    category_data["name"],
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    f"Gastado: {Config.CURRENCY_SYMBOL} {category_data['actual_spent']:.2f}",
                                    size=11,
                                    color=ft.Colors.GREY_600,
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        # Campo de porcentaje
                        self.percentage_field,
                    ],
                    spacing=10,
                ),
                # Barra de uso vs sugerido
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    f"Sugerido: {Config.CURRENCY_SYMBOL} {category_data['suggested_amount']:.2f}",
                                    size=10,
                                    color=ft.Colors.GREY_600,
                                ),
                                ft.Text(
                                    f"Uso: {usage_percent:.0f}%",
                                    size=10,
                                    color="#ef4444" if is_over else "#22c55e",
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.ProgressBar(
                            value=min(usage_percent / 100, 1.0),
                            color="#ef4444" if is_over else "#22c55e",
                            bgcolor=ft.Colors.GREY_200,
                            height=4,
                        ),
                    ],
                    spacing=3,
                ) if category_data["suggested_amount"] > 0 else ft.Container(),
            ],
            spacing=8,
        )
        
        super().__init__(
            content=content,
            padding=15,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
    
    def _handle_change(self, e):
        """Maneja cambios en el campo de porcentaje"""
        try:
            new_value = float(self.percentage_field.value or 0)
            if 0 <= new_value <= 100:
                self.category_data["percentage"] = new_value
                if self.on_change:
                    self.on_change(self.category_data["id"], new_value)
        except ValueError:
            pass


class CategoryBudgetSummaryCard(ft.Container):
    """
    Tarjeta resumen de la distribución porcentual
    
    Args:
        distribution_data: Datos completos de la distribución
    """
    
    def __init__(self, distribution_data: dict):  # ✅ Usar dict minúscula
        total_pct = distribution_data["total_percentage"]
        is_valid = distribution_data["is_valid"]
        base_amount = distribution_data["base_amount"]
        base_source = distribution_data["base_source"]
        unassigned = distribution_data.get("unassigned_percentage", 0)
        
        # Determinar color y estado
        if is_valid:
            status_color = "#22c55e"
            status_icon = ft.Icons.CHECK_CIRCLE
            status_text = "✅ Distribución completa"
        elif total_pct > 100:
            status_color = "#ef4444"
            status_icon = ft.Icons.ERROR
            status_text = f"❌ Excede en {total_pct - 100:.1f}%"
        else:
            status_color = "#f59e0b"
            status_icon = ft.Icons.WARNING
            status_text = f"⚠️ Falta asignar {unassigned:.1f}%"
        
        # Texto de base
        if base_source == "presupuesto":
            base_text = f"Base: Presupuesto de gastos ({Config.CURRENCY_SYMBOL} {base_amount:.2f})"
        elif base_source == "ingresos_reales":
            base_text = f"Base: Ingresos del mes ({Config.CURRENCY_SYMBOL} {base_amount:.2f})"
        else:
            base_text = "⚠️ Sin base configurada (configura presupuesto o espera ingresos)"
        
        content = ft.Column(
            [
                # Título
                ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.PIE_CHART,
                            size=32,
                            color="#667eea",
                        ),
                        ft.Text(
                            "Distribución de Presupuesto",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    spacing=10,
                ),
                ft.Divider(height=5),
                # Base y estado
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                base_text,
                                size=12,
                                color=ft.Colors.GREY_700,
                            ),
                            ft.Row(
                                [
                                    ft.Icon(status_icon, size=20, color=status_color),
                                    ft.Text(
                                        status_text,
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=status_color,
                                    ),
                                ],
                                spacing=8,
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=12,
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=8,
                ),
                # Indicador visual de porcentaje
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    "Total asignado:",
                                    size=13,
                                    color=ft.Colors.GREY_600,
                                ),
                                ft.Text(
                                    f"{total_pct:.1f}%",
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color=status_color,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.ProgressBar(
                            value=min(total_pct / 100, 1.0),
                            color=status_color,
                            bgcolor=ft.Colors.GREY_200,
                            height=8,
                        ),
                    ],
                    spacing=5,
                ),
                # Advertencias
                *[
                    ft.Container(
                        content=ft.Text(
                            warning,
                            size=11,
                            color="#f59e0b",
                        ),
                        padding=8,
                        bgcolor="#fef3c7",
                        border_radius=6,
                    )
                    for warning in distribution_data.get("warnings", [])
                ],
            ],
            spacing=12,
        )
        
        super().__init__(
            content=content,
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.border.all(2, status_color),
        )


class CategoryBudgetDistributionChart(ft.Container):
    """
    Gráfico de torta simple para visualizar la distribución
    
    Args:
        categories: Lista de categorías con sus porcentajes
    """
    
    def __init__(self, categories: List[Dict]):
        # Filtrar solo categorías con porcentaje > 0
        active_categories = [c for c in categories if c["percentage"] > 0]
        
        if not active_categories:
            content = ft.Column(
                [
                    ft.Icon(
                        ft.Icons.PIE_CHART_OUTLINE,
                        size=48,
                        color=ft.Colors.GREY_400,
                    ),
                    ft.Text(
                        "No hay distribución configurada",
                        size=14,
                        color=ft.Colors.GREY_600,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )
        else:
            # Crear visualización simple con barras
            bars = []
            for cat in sorted(active_categories, key=lambda x: x["percentage"], reverse=True):
                bars.append(
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(cat["icon"], size=16),
                                    ft.Text(
                                        cat["name"],
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        f"{cat['percentage']:.1f}%",
                                        size=12,
                                        color=cat["color"],
                                    ),
                                ],
                                spacing=8,
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            # ✅ CORRECCIÓN: Eliminar 'width=None' y 'expand=True'
                            ft.Container(
                                height=6,
                                bgcolor=cat["color"],
                                border_radius=3,
                                # Ancho proporcional al porcentaje
                                width=cat["percentage"] * 3,  # Escala visual (0-300px)
                            ),
                        ],
                        spacing=4,
                    )
                )
            
            content = ft.Column(
                [
                    ft.Text(
                        "📊 Vista de Distribución",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Divider(height=5),
                    *bars,
                ],
                spacing=8,
            )
        
        super().__init__(
            content=content,
            padding=15,
            bgcolor=ft.Colors.GREY_50,
            border_radius=10,
        )
        
class CategoryBudgetAlertWidget(ft.Container):
    """
    Widget compacto que muestra alertas de presupuesto por categoría
    
    Args:
        alerts: Lista de alertas del mes actual
        on_click: Callback opcional cuando se hace clic en una alerta
    """
    
    def __init__(self, alerts: list, on_click=None):
        if not alerts:
            # Sin alertas - mostrar mensaje positivo
            content = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color="#22c55e", size=24),
                        ft.Text(
                            "✅ Todos tus presupuestos están bajo control",
                            size=13,
                            color="#22c55e",
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    spacing=10,
                ),
                padding=12,
                bgcolor="#d1fae5",
                border_radius=10,
                border=ft.border.all(1, "#22c55e"),
            )
        else:
            # Con alertas - mostrar resumen
            alert_tiles = []
            
            for alert in alerts[:3]:  # Mostrar máximo 3 alertas
                # Color según severidad
                if alert["alert_type"] == "over_budget":
                    bg_color = "#fee2e2"
                    border_color = "#ef4444"
                    text_color = "#991b1b"
                elif alert["alert_type"] == "danger":
                    bg_color = "#fef3c7"
                    border_color = "#f59e0b"
                    text_color = "#92400e"
                else:  # warning
                    bg_color = "#dbeafe"
                    border_color = "#3b82f6"
                    text_color = "#1e40af"
                
                alert_tiles.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(alert["icon"], size=20),
                                ft.Column(
                                    [
                                        ft.Text(
                                            alert["category_name"],
                                            size=13,
                                            weight=ft.FontWeight.BOLD,
                                            color=text_color,
                                        ),
                                        ft.Text(
                                            f"{alert['percentage_used']:.0f}% usado - "
                                            f"{Config.CURRENCY_SYMBOL} {abs(alert['remaining']):.2f} "
                                            f"{'disponible' if alert['remaining'] >= 0 else 'excedido'}",
                                            size=11,
                                            color=text_color,
                                        ),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        f"{alert['percentage_used']:.0f}%",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=text_color,
                                    ),
                                ),
                            ],
                            spacing=10,
                        ),
                        padding=10,
                        bgcolor=bg_color,
                        border_radius=8,
                        border=ft.border.all(1, border_color),
                        margin=ft.margin.only(bottom=5),
                        ink=True,
                        on_click=on_click if on_click else None,
                    )
                )
            
            # Mensaje de más alertas si hay
            if len(alerts) > 3:
                alert_tiles.append(
                    ft.Container(
                        content=ft.Text(
                            f"+ {len(alerts) - 3} alerta(s) más",
                            size=11,
                            color=ft.Colors.GREY_600,
                            text_align=ft.TextAlign.CENTER,
                            italic=True,
                        ),
                        padding=5,
                    )
                )
            
            content = ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.WARNING_AMBER, color="#f59e0b", size=20),
                            ft.Text(
                                f"⚡ {len(alerts)} Alerta(s) de Presupuesto",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color="#92400e",
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Container(height=5),
                    *alert_tiles,
                ],
                spacing=5,
            )
        
        super().__init__(
            content=content,
            padding=15,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.GREY_200),
        )
