"""
Vista de configuración y gestión de datos
Archivo: src/ui/settings_view.py
"""

import flet as ft
from .base_view import BaseView
from src.utils.config import Config

class SettingsView(BaseView):
    """Vista de configuración y gestión de datos"""

    def confirm_clear_transactions(self, e):
        """Confirma la limpieza de transacciones"""
        stats = self.db.get_database_stats()
        total_trans = stats.get("total_transactions", 0)

        dialog = ft.AlertDialog(
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.WARNING_AMBER, color="#f97316", size=28),
                    ft.Text("Confirmar Limpieza", weight=ft.FontWeight.BOLD),
                ],
                spacing=10,
            ),
            content=ft.Column(
                [
                    ft.Text(
                        f"Estás a punto de eliminar {total_trans} transacciones.",
                        size=16,
                    ),
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Text(
                            "⚠️ Esta acción NO se puede deshacer",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color="#ef4444",
                        ),
                        padding=10,
                        bgcolor="#fee2e2",
                        border_radius=8,
                    ),
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.ElevatedButton(
                    "Eliminar Todo",
                    on_click=self.clear_transactions,
                    style=ft.ButtonStyle(bgcolor="#ef4444", color=ft.Colors.WHITE),
                ),
            ],
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def clear_transactions(self, e):
        """Ejecuta la limpieza de transacciones"""
        if self.db.clear_all_transactions():
            self.close_dialog()
            self.show_snackbar("✅ Todas las transacciones han sido eliminadas")
            self.refresh()
            self.page.update()
        else:
            self.show_snackbar("❌ Error al limpiar transacciones", error=True)

    def confirm_clear_custom_categories(self, e):
        """Confirma la limpieza de categorías personalizadas"""
        stats = self.db.get_database_stats()
        custom_cats = stats.get("custom_categories", 0)

        if custom_cats == 0:
            self.show_snackbar("No hay categorías personalizadas para eliminar")
            return

        dialog = ft.AlertDialog(
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.WARNING_AMBER, color="#f97316", size=28),
                    ft.Text("Confirmar Limpieza", weight=ft.FontWeight.BOLD),
                ],
                spacing=10,
            ),
            content=ft.Column(
                [
                    ft.Text(
                        f"Estás a punto de eliminar {custom_cats} categorías personalizadas.",
                        size=16,
                    ),
                    ft.Container(height=10),
                    ft.Text(
                        "Las categorías predeterminadas se mantendrán intactas.",
                        size=14,
                        color=ft.Colors.GREY_600,
                    ),
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.ElevatedButton(
                    "Eliminar Categorías",
                    on_click=self.clear_custom_categories,
                    style=ft.ButtonStyle(bgcolor="#eab308", color=ft.Colors.WHITE),
                ),
            ],
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def clear_custom_categories(self, e):
        """Ejecuta la limpieza de categorías personalizadas"""
        if self.db.clear_custom_categories():
            self.close_dialog()
            self.show_snackbar("✅ Categorías personalizadas eliminadas")
            self.refresh()
            self.page.update()
        else:
            self.show_snackbar("❌ Error al limpiar categorías", error=True)

    def confirm_reset_database(self, e):
        """Confirma el reseteo completo de la base de datos"""
        stats = self.db.get_database_stats()

        dialog = ft.AlertDialog(
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.DANGEROUS, color="#ef4444", size=32),
                    ft.Text("⚠️ ADVERTENCIA CRÍTICA", weight=ft.FontWeight.BOLD),
                ],
                spacing=10,
            ),
            content=ft.Column(
                [
                    ft.Text(
                        "Esta acción eliminará:",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(height=5),
                    ft.Text(
                        f"• {stats.get('total_transactions', 0)} transacciones", size=14
                    ),
                    ft.Text(
                        f"• {stats.get('custom_categories', 0)} categorías personalizadas",
                        size=14,
                    ),
                    ft.Text("• Todos los presupuestos configurados", size=14),
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "⚠️ ESTA ACCIÓN ES IRREVERSIBLE",
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color="#ef4444",
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Text(
                                    "Solo se mantendrán las categorías predeterminadas",
                                    size=12,
                                    color=ft.Colors.GREY_700,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=15,
                        bgcolor="#fee2e2",
                        border_radius=8,
                        border=ft.border.all(2, "#ef4444"),
                    ),
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.ElevatedButton(
                    "RESETEAR TODO",
                    on_click=self.reset_database,
                    style=ft.ButtonStyle(
                        bgcolor="#ef4444",
                        color=ft.Colors.WHITE,
                    ),
                ),
            ],
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def reset_database(self, e):
        """Ejecuta el reseteo completo de la base de datos"""
        if self.db.reset_database():
            self.close_dialog()
            self.show_snackbar(
                "✅ Base de datos reseteada exitosamente\n" +
                "🔑 Palabras clave predeterminadas reinicializadas"
            )
            self.refresh()
            self.page.update()
        else:
            self.show_snackbar("❌ Error al resetear la base de datos", error=True)

    def confirm_restore_keywords(self, e):
        """✅ NUEVO: Confirma la restauración de palabras clave predeterminadas"""
        stats = self.db.get_database_stats()
        default_cats = stats.get("default_categories", 0)

        dialog = ft.AlertDialog(
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.RESTORE, color="#3b82f6", size=28),
                    ft.Text("Restaurar Palabras Clave", weight=ft.FontWeight.BOLD),
                ],
                spacing=10,
            ),
            content=ft.Column(
                [
                    ft.Text(
                        f"Esta acción restaurará las palabras clave predeterminadas de {default_cats} categorías.",
                        size=16,
                    ),
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "⚠️ Las palabras clave personalizadas serán reemplazadas",
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color="#f59e0b",
                                ),
                                ft.Text(
                                    "Solo afecta a categorías predeterminadas",
                                    size=12,
                                    color=ft.Colors.GREY_700,
                                ),
                            ],
                            spacing=5,
                        ),
                        padding=10,
                        bgcolor="#fef3c7",
                        border_radius=8,
                    ),
                    ft.Container(height=10),
                    ft.Text(
                        "✅ No afecta transacciones ni categorías personalizadas",
                        size=13,
                        color=ft.Colors.GREEN_700,
                    ),
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.ElevatedButton(
                    "Restaurar Keywords",
                    on_click=self.restore_keywords,
                    style=ft.ButtonStyle(bgcolor="#3b82f6", color=ft.Colors.WHITE),
                ),
            ],
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def restore_keywords(self, e):
        """✅ NUEVO: Ejecuta la restauración de palabras clave"""
        result = self.db.restore_default_keywords()
        
        self.close_dialog()
        
        if result["success"] and result["updated_count"] > 0:
            categories_list = ", ".join(result["categories_updated"][:3])
            if result["updated_count"] > 3:
                categories_list += f" y {result['updated_count'] - 3} más"
            
            self.show_snackbar(
                f"✅ {result['updated_count']} categorías actualizadas\n"
                f"🔑 Restauradas: {categories_list}"
            )
        else:
            self.show_snackbar(result["message"])
        
        self.refresh()
        self.page.update()

    def build(self) -> ft.Control:
        """Construye la vista de configuración"""
        stats = self.db.get_database_stats()

        stats_card = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "📊 Estadísticas de la Base de Datos",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Divider(),
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(
                                        "Transacciones",
                                        size=12,
                                        color=ft.Colors.GREY_600,
                                    ),
                                    ft.Text(
                                        str(stats.get("total_transactions", 0)),
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.VerticalDivider(),
                            ft.Column(
                                [
                                    ft.Text(
                                        "Categorías", size=12, color=ft.Colors.GREY_600
                                    ),
                                    ft.Text(
                                        str(stats.get("total_categories", 0)),
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        expand=True,
                    ),
                    ft.Divider(),
                    ft.Text(
                        f"💰 Ingresos totales: {Config.CURRENCY_SYMBOL} {stats.get('total_income', 0):.2f}",
                        size=14,
                    ),
                    ft.Text(
                        f"💸 Gastos totales: {Config.CURRENCY_SYMBOL} {stats.get('total_expenses', 0):.2f}",
                        size=14,
                    ),
                    ft.Text(
                        f"🏷️ Categorías personalizadas: {stats.get('custom_categories', 0)}",
                        size=14,
                    ),
                ],
                spacing=10,
            ),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
        )

        clean_transactions_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.DELETE_SWEEP, size=40, color="#f97316"
                        ),
                        width=60,
                        height=60,
                        border_radius=30,
                        bgcolor="#f9731620",
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                "Limpiar Transacciones",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "Elimina todas las transacciones",
                                size=12,
                                color=ft.Colors.GREY_600,
                            ),
                        ],
                        expand=True,
                        spacing=2,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ARROW_FORWARD_IOS,
                        icon_size=20,
                        on_click=self.confirm_clear_transactions,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            ink=True,
            on_click=self.confirm_clear_transactions,
        )

        clean_categories_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.LABEL_OFF, size=40, color="#eab308"),
                        width=60,
                        height=60,
                        border_radius=30,
                        bgcolor="#eab30820",
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                "Limpiar Categorías Personalizadas",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "Elimina solo categorías creadas por ti",
                                size=12,
                                color=ft.Colors.GREY_600,
                            ),
                        ],
                        expand=True,
                        spacing=2,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ARROW_FORWARD_IOS,
                        icon_size=20,
                        on_click=self.confirm_clear_custom_categories,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            ink=True,
            on_click=self.confirm_clear_custom_categories,
        )

        # ✅ NUEVO: Botón para restaurar palabras clave
        restore_keywords_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.RESTORE, size=40, color="#3b82f6"),
                        width=60,
                        height=60,
                        border_radius=30,
                        bgcolor="#3b82f620",
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                "Restaurar Palabras Clave",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "Restaura keywords predeterminadas sin borrar datos",
                                size=12,
                                color=ft.Colors.GREY_600,
                            ),
                        ],
                        expand=True,
                        spacing=2,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ARROW_FORWARD_IOS,
                        icon_size=20,
                        on_click=self.confirm_restore_keywords,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            ink=True,
            on_click=self.confirm_restore_keywords,
        )

        reset_database_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.RESTART_ALT, size=40, color="#ef4444"),
                        width=60,
                        height=60,
                        border_radius=30,
                        bgcolor="#ef444420",
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                "Resetear Base de Datos",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "Elimina todo excepto categorías predeterminadas",
                                size=12,
                                color=ft.Colors.GREY_600,
                            ),
                        ],
                        expand=True,
                        spacing=2,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ARROW_FORWARD_IOS,
                        icon_size=20,
                        on_click=self.confirm_reset_database,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            ink=True,
            on_click=self.confirm_reset_database,
        )

        warning_card = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.WARNING_AMBER, size=24, color="#f97316"),
                    ft.Text(
                        "⚠️ Estas acciones son irreversibles. Asegúrate de tener respaldos si es necesario.",
                        size=12,
                        color=ft.Colors.GREY_700,
                        expand=True,
                    ),
                ],
                spacing=10,
            ),
            padding=15,
            bgcolor="#fef3c7",
            border_radius=10,
            border=ft.border.all(1, "#f59e0b"),
        )

        return ft.Column(
            [
                ft.Text("⚙️ Configuración", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                stats_card,
                ft.Container(height=10),
                ft.Text("🗑️ Gestión de Datos", size=18, weight=ft.FontWeight.BOLD),
                warning_card,
                ft.Container(height=10),
                clean_transactions_btn,
                ft.Container(height=5),
                clean_categories_btn,
                ft.Container(height=5),
                restore_keywords_btn,  # ✅ NUEVO
                ft.Container(height=5),
                reset_database_btn,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=10,
        )