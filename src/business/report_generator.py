"""
Generador de Reportes en Excel y CSV - SIN PANDAS
Archivo: src/business/report_generator.py
"""

import csv
from datetime import datetime
from typing import Dict, List, Optional
import os


class ReportGenerator:
    """Generador de reportes financieros en Excel y CSV"""

    def __init__(self, db_manager):
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

            # Preparar resumen
            summary_data = [
                {"Concepto": "Total Ingresos", "Valor": summary["total_income"]},
                {"Concepto": "Total Gastos", "Valor": summary["total_expenses"]},
                {"Concepto": "Balance", "Valor": summary["savings"]},
                {"Concepto": "Tasa de Ahorro (%)", "Valor": summary["savings_rate"]},
                {"Concepto": "N° Transacciones", "Valor": summary["transaction_count"]}
            ]

            # Preparar gastos por categoría
            expenses_data = []
            if summary["total_expenses"] > 0:
                for cat in expenses_by_cat:
                    percentage = (cat["total"] / summary["total_expenses"] * 100)
                    expenses_data.append({
                        "Categoría": cat["category"],
                        "Total": cat["total"],
                        "Porcentaje (%)": round(percentage, 2)
                    })

            # Preparar ingresos por categoría
            income_data = []
            if summary["total_income"] > 0:
                for cat in income_by_cat:
                    percentage = (cat["total"] / summary["total_income"] * 100)
                    income_data.append({
                        "Categoría": cat["category"],
                        "Total": cat["total"],
                        "Porcentaje (%)": round(percentage, 2)
                    })

            # Determinar directorio de salida
            if output_dir is None:
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
                    output_dir, filename, transactions_data,
                    summary_data, expenses_data, income_data, year, month
                )
            else:
                return self._save_csv(
                    output_dir, filename, transactions_data,
                    summary_data, expenses_data, income_data
                )

        except Exception as e:
            return {
                "success": False,
                "filepath": None,
                "message": f"Error al generar reporte: {str(e)}"
            }

    def _save_excel(
        self, output_dir: str, filename: str,
        trans_data: List[Dict], summary_data: List[Dict],
        expenses_data: List[Dict], income_data: List[Dict],
        year: int, month: int
    ) -> Dict:
        """Guarda el reporte en formato Excel"""
        try:
            import openpyxl
            from openpyxl.styles import Font, Alignment, PatternFill
            
            filepath = os.path.join(output_dir, f"{filename}.xlsx")
            wb = openpyxl.Workbook()
            
            # Hoja 1: Resumen
            ws_summary = wb.active
            ws_summary.title = "Resumen"
            self._write_data_to_sheet(ws_summary, summary_data)
            
            # Hoja 2: Transacciones
            ws_trans = wb.create_sheet("Transacciones")
            self._write_data_to_sheet(ws_trans, trans_data)
            
            # Hoja 3: Gastos por categoría
            if expenses_data:
                ws_exp = wb.create_sheet("Gastos por Categoría")
                self._write_data_to_sheet(ws_exp, expenses_data)
            
            # Hoja 4: Ingresos por categoría
            if income_data:
                ws_inc = wb.create_sheet("Ingresos por Categoría")
                self._write_data_to_sheet(ws_inc, income_data)
            
            wb.save(filepath)
            
            return {
                "success": True,
                "filepath": filepath,
                "message": "Reporte Excel generado exitosamente"
            }
            
        except ImportError:
            return {
                "success": False,
                "filepath": None,
                "message": "openpyxl no disponible, use formato CSV"
            }
        except Exception as e:
            return {
                "success": False,
                "filepath": None,
                "message": f"Error al guardar Excel: {str(e)}"
            }

    def _write_data_to_sheet(self, worksheet, data: List[Dict]):
        """Escribe datos en una hoja de Excel"""
        if not data:
            return
        
        # Escribir encabezados
        headers = list(data[0].keys())
        for col_idx, header in enumerate(headers, start=1):
            cell = worksheet.cell(row=1, column=col_idx)
            cell.value = header
            
            # Estilo de encabezado (opcional)
            try:
                from openpyxl.styles import Font, PatternFill
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
            except:
                pass
        
        # Escribir datos
        for row_idx, row_data in enumerate(data, start=2):
            for col_idx, header in enumerate(headers, start=1):
                cell = worksheet.cell(row=row_idx, column=col_idx)
                cell.value = row_data.get(header, "")
        
        # Ajustar ancho de columnas
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if cell.value and len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

    def _save_csv(
        self, output_dir: str, filename: str,
        trans_data: List[Dict], summary_data: List[Dict],
        expenses_data: List[Dict], income_data: List[Dict]
    ) -> Dict:
        """Guarda el reporte en formato CSV"""
        try:
            # Archivo principal: transacciones
            main_filepath = os.path.join(output_dir, f"{filename}.csv")
            self._write_csv(main_filepath, trans_data)

            # Archivo de resumen
            summary_filepath = os.path.join(output_dir, f"{filename}_Resumen.csv")
            self._write_csv(summary_filepath, summary_data)

            # Archivo de gastos
            if expenses_data:
                expenses_filepath = os.path.join(output_dir, f"{filename}_Gastos.csv")
                self._write_csv(expenses_filepath, expenses_data)

            # Archivo de ingresos
            if income_data:
                income_filepath = os.path.join(output_dir, f"{filename}_Ingresos.csv")
                self._write_csv(income_filepath, income_data)

            return {
                "success": True,
                "filepath": main_filepath,
                "message": "Reportes CSV generados exitosamente"
            }

        except Exception as e:
            return {
                "success": False,
                "filepath": None,
                "message": f"Error al guardar CSV: {str(e)}"
            }

    def _write_csv(self, filepath: str, data: List[Dict]):
        """Escribe datos a un archivo CSV"""
        if not data:
            return
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

    def generate_annual_report(
        self, year: int, format: str = "xlsx",
        output_dir: Optional[str] = None
    ) -> Dict:
        """
        Genera un reporte anual completo
        """
        try:
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

            # Calcular totales anuales
            total_income = sum(t["Monto"] for t in all_transactions if t["Tipo"] == "Ingreso")
            total_expenses = sum(t["Monto"] for t in all_transactions if t["Tipo"] == "Gasto")
            annual_balance = total_income - total_expenses
            annual_savings_rate = (annual_balance / total_income * 100) if total_income > 0 else 0

            annual_summary = [
                {"Concepto": "Total Ingresos Anual", "Valor": total_income},
                {"Concepto": "Total Gastos Anual", "Valor": total_expenses},
                {"Concepto": "Balance Anual", "Valor": annual_balance},
                {"Concepto": "Tasa de Ahorro Anual (%)", "Valor": annual_savings_rate},
                {"Concepto": "N° Total Transacciones", "Valor": len(all_transactions)}
            ]

            # Determinar directorio
            if output_dir is None:
                output_dir = os.path.expanduser("~/Downloads")
                if not os.path.exists(output_dir):
                    output_dir = os.getcwd()

            filename = f"Reporte_Anual_TermoWallet_{year}"

            if format.lower() == "xlsx":
                try:
                    import openpyxl
                    filepath = os.path.join(output_dir, f"{filename}.xlsx")
                    wb = openpyxl.Workbook()
                    
                    ws_annual = wb.active
                    ws_annual.title = "Resumen Anual"
                    self._write_data_to_sheet(ws_annual, annual_summary)
                    
                    ws_monthly = wb.create_sheet("Resumen Mensual")
                    self._write_data_to_sheet(ws_monthly, monthly_summaries)
                    
                    ws_trans = wb.create_sheet("Todas las Transacciones")
                    self._write_data_to_sheet(ws_trans, all_transactions)
                    
                    wb.save(filepath)
                except ImportError:
                    filepath = os.path.join(output_dir, f"{filename}.csv")
                    self._write_csv(filepath, all_transactions)
            else:
                filepath = os.path.join(output_dir, f"{filename}.csv")
                self._write_csv(filepath, all_transactions)

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