"""
Generador de Reportes en Excel y CSV
Archivo: src/business/report_generator.py

Este módulo genera reportes detallados de transacciones en formato Excel y CSV
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import os


class ReportGenerator:
    """Generador de reportes financieros en Excel y CSV"""

    def __init__(self, db_manager):
        """
        Inicializa el generador de reportes
        
        Args:
            db_manager: Instancia de DatabaseManager
        """
        self.db = db_manager

    def generate_monthly_report(
        self,
        year: int,
        month: int,
        format: str = "xlsx",
        output_dir: Optional[str] = None
    ) -> Dict:
        """
        Genera un reporte mensual completo
        
        Args:
            year: Año del reporte
            month: Mes del reporte
            format: "xlsx" o "csv"
            output_dir: Directorio de salida (None = Downloads o directorio actual)
            
        Returns:
            Dict con: {"success": bool, "filepath": str, "message": str}
        """
        try:
            # Obtener datos
            transactions = self.db.get_transactions_by_month(year, month)
            summary = self.db.get_monthly_summary(year, month)
            expenses_by_cat = self.db.get_expenses_by_category(year, month)
            income_by_cat = self.db.get_income_by_category(year, month)

            if not transactions:
                return {
                    "success": False,
                    "filepath": None,
                    "message": "No hay transacciones en este mes"
                }

            # Preparar datos de transacciones
            transactions_data = []
            for t in transactions:
                category = self.db.get_category_by_id(t.category_id)
                transactions_data.append({
                    "Fecha": t.date.strftime("%d/%m/%Y"),
                    "Descripción": t.description,
                    "Categoría": category.name if category else "Sin categoría",
                    "Tipo": "Ingreso" if t.transaction_type == "income" else "Gasto",
                    "Monto": t.amount,
                    "Notas": t.notes or "",
                })

            df_transactions = pd.DataFrame(transactions_data)

            # Preparar resumen
            summary_data = {
                "Concepto": [
                    "Total Ingresos",
                    "Total Gastos",
                    "Balance",
                    "Tasa de Ahorro (%)",
                    "N° Transacciones"
                ],
                "Valor": [
                    summary["total_income"],
                    summary["total_expenses"],
                    summary["savings"],
                    summary["savings_rate"],
                    summary["transaction_count"]
                ]
            }
            df_summary = pd.DataFrame(summary_data)

            # Preparar gastos por categoría
            expenses_data = []
            for cat in expenses_by_cat:
                percentage = (cat["total"] / summary["total_expenses"] * 100) if summary["total_expenses"] > 0 else 0
                expenses_data.append({
                    "Categoría": cat["category"],
                    "Total": cat["total"],
                    "Porcentaje (%)": round(percentage, 2)
                })
            df_expenses = pd.DataFrame(expenses_data) if expenses_data else pd.DataFrame()

            # Preparar ingresos por categoría
            income_data = []
            for cat in income_by_cat:
                percentage = (cat["total"] / summary["total_income"] * 100) if summary["total_income"] > 0 else 0
                income_data.append({
                    "Categoría": cat["category"],
                    "Total": cat["total"],
                    "Porcentaje (%)": round(percentage, 2)
                })
            df_income = pd.DataFrame(income_data) if income_data else pd.DataFrame()

            # Determinar directorio de salida
            if output_dir is None:
                # Intentar usar Downloads, sino usar directorio actual
                output_dir = os.path.expanduser("~/Downloads")
                if not os.path.exists(output_dir):
                    output_dir = os.getcwd()

            # Crear nombre de archivo
            month_names = [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ]
            filename = f"Reporte_TermoWallet_{month_names[month-1]}_{year}"

            if format.lower() == "xlsx":
                return self._save_excel(
                    output_dir,
                    filename,
                    df_transactions,
                    df_summary,
                    df_expenses,
                    df_income,
                    year,
                    month
                )
            else:  # CSV
                return self._save_csv(
                    output_dir,
                    filename,
                    df_transactions,
                    df_summary,
                    df_expenses,
                    df_income
                )

        except Exception as e:
            return {
                "success": False,
                "filepath": None,
                "message": f"Error al generar reporte: {str(e)}"
            }

    def _save_excel(
        self,
        output_dir: str,
        filename: str,
        df_trans: pd.DataFrame,
        df_summary: pd.DataFrame,
        df_expenses: pd.DataFrame,
        df_income: pd.DataFrame,
        year: int,
        month: int
    ) -> Dict:
        """Guarda el reporte en formato Excel con múltiples hojas"""
        try:
            filepath = os.path.join(output_dir, f"{filename}.xlsx")

            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja 1: Resumen
                df_summary.to_excel(writer, sheet_name='Resumen', index=False)

                # Hoja 2: Todas las transacciones
                df_trans.to_excel(writer, sheet_name='Transacciones', index=False)

                # Hoja 3: Gastos por categoría
                if not df_expenses.empty:
                    df_expenses.to_excel(writer, sheet_name='Gastos por Categoría', index=False)

                # Hoja 4: Ingresos por categoría
                if not df_income.empty:
                    df_income.to_excel(writer, sheet_name='Ingresos por Categoría', index=False)

                # Ajustar anchos de columna
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width

            return {
                "success": True,
                "filepath": filepath,
                "message": f"Reporte Excel generado exitosamente"
            }

        except Exception as e:
            return {
                "success": False,
                "filepath": None,
                "message": f"Error al guardar Excel: {str(e)}"
            }

    def _save_csv(
        self,
        output_dir: str,
        filename: str,
        df_trans: pd.DataFrame,
        df_summary: pd.DataFrame,
        df_expenses: pd.DataFrame,
        df_income: pd.DataFrame
    ) -> Dict:
        """Guarda el reporte en formato CSV (archivo principal + archivos adicionales)"""
        try:
            # Archivo principal: transacciones
            main_filepath = os.path.join(output_dir, f"{filename}.csv")
            df_trans.to_csv(main_filepath, index=False, encoding='utf-8-sig')

            # Archivo de resumen
            summary_filepath = os.path.join(output_dir, f"{filename}_Resumen.csv")
            df_summary.to_csv(summary_filepath, index=False, encoding='utf-8-sig')

            # Archivo de gastos
            if not df_expenses.empty:
                expenses_filepath = os.path.join(output_dir, f"{filename}_Gastos.csv")
                df_expenses.to_csv(expenses_filepath, index=False, encoding='utf-8-sig')

            # Archivo de ingresos
            if not df_income.empty:
                income_filepath = os.path.join(output_dir, f"{filename}_Ingresos.csv")
                df_income.to_csv(income_filepath, index=False, encoding='utf-8-sig')

            return {
                "success": True,
                "filepath": main_filepath,
                "message": f"Reportes CSV generados exitosamente"
            }

        except Exception as e:
            return {
                "success": False,
                "filepath": None,
                "message": f"Error al guardar CSV: {str(e)}"
            }

    def generate_annual_report(
        self,
        year: int,
        format: str = "xlsx",
        output_dir: Optional[str] = None
    ) -> Dict:
        """
        Genera un reporte anual completo
        
        Args:
            year: Año del reporte
            format: "xlsx" o "csv"
            output_dir: Directorio de salida
            
        Returns:
            Dict con resultado
        """
        try:
            # Obtener todas las transacciones del año
            all_transactions = []
            monthly_summaries = []

            for month in range(1, 13):
                transactions = self.db.get_transactions_by_month(year, month)
                summary = self.db.get_monthly_summary(year, month)

                for t in transactions:
                    category = self.db.get_category_by_id(t.category_id)
                    all_transactions.append({
                        "Fecha": t.date.strftime("%d/%m/%Y"),
                        "Mes": month,
                        "Descripción": t.description,
                        "Categoría": category.name if category else "Sin categoría",
                        "Tipo": "Ingreso" if t.transaction_type == "income" else "Gasto",
                        "Monto": t.amount,
                        "Notas": t.notes or "",
                    })

                monthly_summaries.append({
                    "Mes": f"{month:02d} - {summary['month_name']}",
                    "Ingresos": summary["total_income"],
                    "Gastos": summary["total_expenses"],
                    "Balance": summary["savings"],
                    "Tasa Ahorro (%)": summary["savings_rate"]
                })

            if not all_transactions:
                return {
                    "success": False,
                    "filepath": None,
                    "message": f"No hay transacciones en {year}"
                }

            df_transactions = pd.DataFrame(all_transactions)
            df_monthly = pd.DataFrame(monthly_summaries)

            # Calcular totales anuales
            total_income = df_transactions[df_transactions["Tipo"] == "Ingreso"]["Monto"].sum()
            total_expenses = df_transactions[df_transactions["Tipo"] == "Gasto"]["Monto"].sum()
            annual_balance = total_income - total_expenses
            annual_savings_rate = (annual_balance / total_income * 100) if total_income > 0 else 0

            annual_summary = pd.DataFrame({
                "Concepto": [
                    "Total Ingresos Anual",
                    "Total Gastos Anual",
                    "Balance Anual",
                    "Tasa de Ahorro Anual (%)",
                    "N° Total Transacciones"
                ],
                "Valor": [
                    total_income,
                    total_expenses,
                    annual_balance,
                    annual_savings_rate,
                    len(all_transactions)
                ]
            })

            # Determinar directorio
            if output_dir is None:
                output_dir = os.path.expanduser("~/Downloads")
                if not os.path.exists(output_dir):
                    output_dir = os.getcwd()

            filename = f"Reporte_Anual_TermoWallet_{year}"

            if format.lower() == "xlsx":
                filepath = os.path.join(output_dir, f"{filename}.xlsx")
                with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                    annual_summary.to_excel(writer, sheet_name='Resumen Anual', index=False)
                    df_monthly.to_excel(writer, sheet_name='Resumen Mensual', index=False)
                    df_transactions.to_excel(writer, sheet_name='Todas las Transacciones', index=False)
            else:
                filepath = os.path.join(output_dir, f"{filename}.csv")
                df_transactions.to_csv(filepath, index=False, encoding='utf-8-sig')

            return {
                "success": True,
                "filepath": filepath,
                "message": f"Reporte anual {year} generado exitosamente"
            }

        except Exception as e:
            return {
                "success": False,
                "filepath": None,
                "message": f"Error: {str(e)}"
            }