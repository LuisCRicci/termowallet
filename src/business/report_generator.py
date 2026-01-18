"""
Generador de Reportes - ✅ COMPATIBLE CON ANDROID usando Sistema Nativo
Archivo: src/business/report_generator.py

✅ Sin jnius - Usa sistema de compartir de Android
✅ El usuario elige dónde guardar (Drive, Downloads, etc.)
"""

import csv
import sys
import os
import tempfile
from datetime import datetime
from typing import Dict, List

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill
except ImportError:
    openpyxl = None
import flet as ft


class ReportGenerator:
    """Generador de reportes con sistema nativo de compartir"""

    def __init__(self, db_manager, page=None):
        self.db = db_manager
        self.page = page
        from src.utils.config import Config
        self.is_android = Config.is_android()
        
        # FilePicker para compartir archivos
        self.file_picker = None
        if page:
            try:
                self.file_picker = ft.FilePicker(
                    on_result=self._on_file_save_result
                )
                self._picker_added = False
            except Exception as e:
                print(f"⚠️ Error creando FilePicker: {e}")
    
    def generate_monthly_report(
        self,
        year: int,
        month: int,
        format: str = "xlsx",
        callback_success = None,
        callback_error = None
    ) -> Dict:
        """
        Genera reporte mensual y permite al usuario guardarlo
        
        Returns:
            Dict con resultado
        """
        try:
            print(f"\n📊 Generando reporte mensual: {month}/{year}")
            
            # Obtener datos
            transactions = self.db.get_transactions_by_month(year, month)
            summary = self.db.get_monthly_summary(year, month)
            expenses_by_cat = self.db.get_expenses_by_category(year, month)
            income_by_cat = self.db.get_income_by_category(year, month)

            if not transactions:
                error_msg = "❌ No hay transacciones en este mes"
                print(error_msg)
                if callback_error:
                    callback_error(error_msg)
                return {
                    "success": False,
                    "filepath": None,
                    "message": error_msg
                }

            # Preparar datos
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

            summary_data = [
                {"Concepto": "Total Ingresos", "Valor": summary["total_income"]},
                {"Concepto": "Total Gastos", "Valor": summary["total_expenses"]},
                {"Concepto": "Balance", "Valor": summary["savings"]},
                {"Concepto": "Tasa de Ahorro (%)", "Valor": summary["savings_rate"]},
                {"Concepto": "Nº Transacciones", "Valor": summary["transaction_count"]}
            ]

            expenses_data = []
            if summary["total_expenses"] > 0:
                for cat in expenses_by_cat:
                    percentage = (cat["total"] / summary["total_expenses"] * 100)
                    expenses_data.append({
                        "Categoría": cat["category"],
                        "Total": cat["total"],
                        "Porcentaje (%)": round(percentage, 2)
                    })

            income_data = []
            if summary["total_income"] > 0:
                for cat in income_by_cat:
                    percentage = (cat["total"] / summary["total_income"] * 100)
                    income_data.append({
                        "Categoría": cat["category"],
                        "Total": cat["total"],
                        "Porcentaje (%)": round(percentage, 2)
                    })

            # Nombre de archivo
            month_names = [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ]
            filename = f"Reporte_TermoWallet_{month_names[month-1]}_{year}.{format}"

            # ✅ NUEVA ESTRATEGIA: Crear en temp y compartir
            return self._create_and_share_file(
                filename,
                format,
                transactions_data,
                summary_data,
                expenses_data,
                income_data,
                callback_success,
                callback_error
            )

        except Exception as e:
            print(f"❌ Error generando reporte: {e}")
            import traceback
            traceback.print_exc()
            error_msg = f"❌ Error: {str(e)}"
            if callback_error:
                callback_error(error_msg)
            return {
                "success": False,
                "filepath": None,
                "message": error_msg
            }
    
    
    def generate_custom_range_report(
        self,
        start_date: datetime,
        end_date: datetime,
        format: str = "xlsx",
        callback_success = None,
        callback_error = None
    ) -> Dict:
        """
        Genera reporte de rango personalizado de fechas
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            format: Formato del archivo (xlsx o csv)
            callback_success: Función de éxito
            callback_error: Función de error
        
        Returns:
            Dict con resultado
        """
        try:
            print(f"\n📊 Generando reporte personalizado: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
            
            # Obtener transacciones del rango
            transactions = self.db.get_transactions_by_date_range(start_date, end_date)
            
            if not transactions:
                error_msg = "❌ No hay transacciones en este rango de fechas"
                print(error_msg)
                if callback_error:
                    callback_error(error_msg)
                return {
                    "success": False,
                    "filepath": None,
                    "message": error_msg
                }
            
            # Calcular estadísticas del rango
            total_income = sum(t.amount for t in transactions if t.transaction_type == "income")
            total_expenses = sum(t.amount for t in transactions if t.transaction_type == "expense")
            
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
            
            # Resumen general
            summary_data = [
                {"Concepto": "Fecha Inicio", "Valor": start_date.strftime("%d/%m/%Y")},
                {"Concepto": "Fecha Fin", "Valor": end_date.strftime("%d/%m/%Y")},
                {"Concepto": "Días", "Valor": (end_date - start_date).days + 1},
                {"Concepto": "Total Ingresos", "Valor": total_income},
                {"Concepto": "Total Gastos", "Valor": total_expenses},
                {"Concepto": "Balance", "Valor": total_income - total_expenses},
                {"Concepto": "Nº Transacciones", "Valor": len(transactions)}
            ]
            
            # Gastos por categoría
            expenses_by_cat = {}
            for t in transactions:
                if t.transaction_type == "expense":
                    category = self.db.get_category_by_id(t.category_id)
                    cat_name = category.name if category else "Sin categoría"
                    
                    if cat_name not in expenses_by_cat:
                        expenses_by_cat[cat_name] = 0
                    expenses_by_cat[cat_name] += t.amount
            
            expenses_data = []
            if total_expenses > 0:
                for cat_name, total in sorted(expenses_by_cat.items(), key=lambda x: x[1], reverse=True):
                    percentage = (total / total_expenses * 100)
                    expenses_data.append({
                        "Categoría": cat_name,
                        "Total": total,
                        "Porcentaje (%)": round(percentage, 2)
                    })
            
            # Ingresos por categoría
            income_by_cat = {}
            for t in transactions:
                if t.transaction_type == "income":
                    category = self.db.get_category_by_id(t.category_id)
                    cat_name = category.name if category else "Sin categoría"
                    
                    if cat_name not in income_by_cat:
                        income_by_cat[cat_name] = 0
                    income_by_cat[cat_name] += t.amount
            
            income_data = []
            if total_income > 0:
                for cat_name, total in sorted(income_by_cat.items(), key=lambda x: x[1], reverse=True):
                    percentage = (total / total_income * 100)
                    income_data.append({
                        "Categoría": cat_name,
                        "Total": total,
                        "Porcentaje (%)": round(percentage, 2)
                    })
            
            # Nombre de archivo
            filename = f"Reporte_TermoWallet_{start_date.strftime('%d%m%Y')}_al_{end_date.strftime('%d%m%Y')}.{format}"
            
            # Crear y compartir archivo
            return self._create_and_share_file(
                filename,
                format,
                transactions_data,
                summary_data,
                expenses_data,
                income_data,
                callback_success,
                callback_error
            )
            
        except Exception as e:
            print(f"❌ Error generando reporte personalizado: {e}")
            import traceback
            traceback.print_exc()
            error_msg = f"❌ Error: {str(e)}"
            if callback_error:
                callback_error(error_msg)
            return {
                "success": False,
                "filepath": None,
                "message": error_msg
            }


    def generate_annual_report(
        self,
        year: int,
        format: str = "xlsx",
        callback_success = None,
        callback_error = None
    ) -> Dict:
        """
        Genera reporte anual completo
        
        Args:
            year: Año del reporte
            format: Formato del archivo (xlsx o csv)
            callback_success: Función de éxito
            callback_error: Función de error
        
        Returns:
            Dict con resultado
        """
        try:
            print(f"\n📊 Generando reporte anual: {year}")
            
            # Obtener todas las transacciones del año
            all_transactions = []
            for month in range(1, 13):
                monthly_trans = self.db.get_transactions_by_month(year, month)
                all_transactions.extend(monthly_trans)
            
            if not all_transactions:
                error_msg = f"❌ No hay transacciones en el año {year}"
                print(error_msg)
                if callback_error:
                    callback_error(error_msg)
                return {
                    "success": False,
                    "filepath": None,
                    "message": error_msg
                }
            
            # Calcular estadísticas anuales
            total_income = sum(t.amount for t in all_transactions if t.transaction_type == "income")
            total_expenses = sum(t.amount for t in all_transactions if t.transaction_type == "expense")
            
            # Preparar datos de transacciones
            transactions_data = []
            for t in all_transactions:
                category = self.db.get_category_by_id(t.category_id)
                transactions_data.append({
                    "Fecha": t.date.strftime("%d/%m/%Y"),
                    "Descripción": t.description,
                    "Categoría": category.name if category else "Sin categoría",
                    "Tipo": "Ingreso" if t.transaction_type == "income" else "Gasto",
                    "Monto": t.amount,
                    "Notas": t.notes or "",
                })
            
            # Resumen anual
            summary_data = [
                {"Concepto": "Año", "Valor": year},
                {"Concepto": "Total Ingresos", "Valor": total_income},
                {"Concepto": "Total Gastos", "Valor": total_expenses},
                {"Concepto": "Balance", "Valor": total_income - total_expenses},
                {"Concepto": "Tasa de Ahorro (%)", "Valor": round((total_income - total_expenses) / total_income * 100, 2) if total_income > 0 else 0},
                {"Concepto": "Nº Transacciones", "Valor": len(all_transactions)}
            ]
            
            # Gastos por categoría
            expenses_by_cat = {}
            for t in all_transactions:
                if t.transaction_type == "expense":
                    category = self.db.get_category_by_id(t.category_id)
                    cat_name = category.name if category else "Sin categoría"
                    
                    if cat_name not in expenses_by_cat:
                        expenses_by_cat[cat_name] = 0
                    expenses_by_cat[cat_name] += t.amount
            
            expenses_data = []
            if total_expenses > 0:
                for cat_name, total in sorted(expenses_by_cat.items(), key=lambda x: x[1], reverse=True):
                    percentage = (total / total_expenses * 100)
                    expenses_data.append({
                        "Categoría": cat_name,
                        "Total": total,
                        "Porcentaje (%)": round(percentage, 2)
                    })
            
            # Ingresos por categoría
            income_by_cat = {}
            for t in all_transactions:
                if t.transaction_type == "income":
                    category = self.db.get_category_by_id(t.category_id)
                    cat_name = category.name if category else "Sin categoría"
                    
                    if cat_name not in income_by_cat:
                        income_by_cat[cat_name] = 0
                    income_by_cat[cat_name] += t.amount
            
            income_data = []
            if total_income > 0:
                for cat_name, total in sorted(income_by_cat.items(), key=lambda x: x[1], reverse=True):
                    percentage = (total / total_income * 100)
                    income_data.append({
                        "Categoría": cat_name,
                        "Total": total,
                        "Porcentaje (%)": round(percentage, 2)
                    })
            
            # Nombre de archivo
            filename = f"Reporte_TermoWallet_Anual_{year}.{format}"
            
            # Crear y compartir archivo
            return self._create_and_share_file(
                filename,
                format,
                transactions_data,
                summary_data,
                expenses_data,
                income_data,
                callback_success,
                callback_error
            )
            
        except Exception as e:
            print(f"❌ Error generando reporte anual: {e}")
            import traceback
            traceback.print_exc()
            error_msg = f"❌ Error: {str(e)}"
            if callback_error:
                callback_error(error_msg)
            return {
                "success": False,
                "filepath": None,
                "message": error_msg
            }
    
    
    
    
    def _create_and_share_file(
        self,
        filename: str,
        format: str,
        transactions_data: List[Dict],
        summary_data: List[Dict],
        expenses_data: List[Dict],
        income_data: List[Dict],
        callback_success,
        callback_error
    ) -> Dict:
        """Crea archivo temporal y abre diálogo para guardar/compartir"""
        
        print("\n" + "="*60)
        print("💾 CREANDO REPORTE TEMPORAL")
        print("="*60)
        
        try:
            # Crear archivo en directorio temporal
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, filename)
            
            print(f"   📁 Ruta temporal: {temp_path}")
            
            # Generar archivo
            if format == "xlsx" and openpyxl:
                print(f"   📊 Generando Excel...")
                success = self._save_excel(
                    temp_path,
                    transactions_data,
                    summary_data,
                    expenses_data,
                    income_data
                )
            else:
                print(f"   📄 Generando CSV...")
                success = self._save_csv(
                    temp_path,
                    transactions_data
                )
            
            if not success:
                error_msg = "❌ Error al crear archivo"
                print(error_msg)
                if callback_error:
                    callback_error(error_msg)
                return {
                    "success": False,
                    "filepath": None,
                    "message": error_msg
                }
            
            # Verificar que se creó
            if not os.path.exists(temp_path):
                error_msg = "❌ Archivo temporal no se creó"
                print(error_msg)
                if callback_error:
                    callback_error(error_msg)
                return {
                    "success": False,
                    "filepath": None,
                    "message": error_msg
                }
            
            file_size = os.path.getsize(temp_path)
            print(f"   ✅ Archivo creado: {file_size} bytes")
            print("="*60 + "\n")
            
            # Guardar callbacks y datos para el diálogo
            self._pending_data = {
                "temp_path": temp_path,
                "filename": filename,
                "format": format,
                "callback_success": callback_success,
                "callback_error": callback_error
            }
            
            # Agregar FilePicker al overlay si no está
            if self.file_picker and not self._picker_added and self.page:
                try:
                    self.page.overlay.append(self.file_picker)
                    self._picker_added = True
                    self.page.update()
                except Exception as e:
                    print(f"⚠️ Error agregando FilePicker: {e}")
            
            # Abrir diálogo de guardar
            if self.file_picker:
                print("📂 Abriendo diálogo para guardar archivo...")
                
                try:
                    self.file_picker.save_file(
                        dialog_title="Guardar reporte",
                        file_name=filename,
                        allowed_extensions=[format],
                    )
                    
                    # Mostrar mensaje informativo
                    if callback_success:
                        callback_success(
                            temp_path,
                            f"📂 Elige dónde guardar tu reporte\n\n"
                            f"💡 Puedes guardarlo en:\n"
                            f"• Descargas\n"
                            f"• Google Drive\n"
                            f"• Cualquier carpeta de tu dispositivo"
                        )
                    
                    return {
                        "success": True,
                        "filepath": temp_path,
                        "message": "Selecciona ubicación para guardar"
                    }
                    
                except Exception as e:
                    print(f"❌ Error abriendo diálogo: {e}")
                    
                    # Fallback: Mostrar info del archivo temporal
                    if callback_success:
                        callback_success(
                            temp_path,
                            f"✅ Reporte generado\n\n"
                            f"📁 Ubicación temporal:\n{temp_path}\n\n"
                            f"💡 En Android:\n"
                            f"• Conecta tu celular por USB\n"
                            f"• Navega a la carpeta temporal\n"
                            f"• Copia el archivo donde desees"
                        )
                    
                    return {
                        "success": True,
                        "filepath": temp_path,
                        "message": "Archivo creado en ubicación temporal"
                    }
            else:
                error_msg = "❌ FilePicker no disponible"
                if callback_error:
                    callback_error(error_msg)
                return {
                    "success": False,
                    "filepath": None,
                    "message": error_msg
                }
            
        except Exception as e:
            print(f"❌ Error en creación: {e}")
            import traceback
            traceback.print_exc()
            error_msg = f"❌ Error: {str(e)}"
            if callback_error:
                callback_error(error_msg)
            return {
                "success": False,
                "filepath": None,
                "message": error_msg
            }
    
    def _on_file_save_result(self, e: ft.FilePickerResultEvent):
        """Callback cuando usuario selecciona ubicación"""
        
        if not hasattr(self, '_pending_data'):
            print("⚠️ No hay datos pendientes")
            return
        
        data = self._pending_data
        
        if e.path is None:
            # Usuario canceló
            print("❌ Usuario canceló")
            
            # El archivo temporal sigue disponible
            if data.get('callback_success'):
                data['callback_success'](
                    data['temp_path'],
                    f"ℹ️ Guardado cancelado\n\n"
                    f"El archivo temporal está en:\n{data['temp_path']}\n\n"
                    f"Puedes copiarlo manualmente si lo necesitas"
                )
            return
        
        # Usuario eligió ubicación
        save_path = e.path
        print(f"💾 Usuario eligió guardar en: {save_path}")
        
        try:
            # Copiar archivo temporal a ubicación elegida
            import shutil
            shutil.copy2(data['temp_path'], save_path)
            
            print(f"✅ Archivo guardado: {save_path}")
            
            if data.get('callback_success'):
                data['callback_success'](
                    save_path,
                    f"✅ ¡Reporte guardado exitosamente!\n\n"
                    f"📁 Ubicación:\n{save_path}\n\n"
                    f"Puedes abrirlo desde tu explorador de archivos"
                )
            
            # Limpiar archivo temporal
            try:
                os.remove(data['temp_path'])
                print("🗑️ Archivo temporal eliminado")
            except:
                pass
                
        except Exception as ex:
            print(f"❌ Error guardando: {ex}")
            import traceback
            traceback.print_exc()
            
            if data.get('callback_error'):
                data['callback_error'](
                    f"❌ Error al guardar archivo: {str(ex)}\n\n"
                    f"El archivo temporal sigue en:\n{data['temp_path']}"
                )
        
        # Limpiar datos pendientes
        delattr(self, '_pending_data')
    
    def _save_excel(
        self,
        filepath: str,
        trans_data: List[Dict],
        summary_data: List[Dict],
        expenses_data: List[Dict],
        income_data: List[Dict]
    ) -> bool:
        """Guarda Excel"""
        try:
            if not openpyxl:
                raise ImportError("openpyxl no disponible")
            
            print(f"   Creando Excel con {len(trans_data)} transacciones...")
            
            wb = openpyxl.Workbook()
            
            # Hoja 1: Resumen
            ws_summary = wb.active
            ws_summary.title = "Resumen"
            self._write_data_to_sheet(ws_summary, summary_data)
            
            # Hoja 2: Transacciones
            ws_trans = wb.create_sheet("Transacciones")
            self._write_data_to_sheet(ws_trans, trans_data)
            
            # Hoja 3: Gastos
            if expenses_data:
                ws_exp = wb.create_sheet("Gastos por Categoría")
                self._write_data_to_sheet(ws_exp, expenses_data)
            
            # Hoja 4: Ingresos
            if income_data:
                ws_inc = wb.create_sheet("Ingresos por Categoría")
                self._write_data_to_sheet(ws_inc, income_data)
            
            wb.save(filepath)
            print(f"   ✅ Excel guardado")
            return True
            
        except Exception as e:
            print(f"   ❌ Error creando Excel: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _write_data_to_sheet(self, worksheet, data: List[Dict]):
        """Escribe datos en hoja Excel"""
        if not data:
            return
        
        # Encabezados
        headers = list(data[0].keys())
        for col_idx, header in enumerate(headers, start=1):
            cell = worksheet.cell(row=1, column=col_idx)
            cell.value = header
            
            try:
                cell.font = Font(bold=True)
                cell.fill = PatternFill(
                    start_color="CCCCCC",
                    end_color="CCCCCC",
                    fill_type="solid"
                )
            except:
                pass
        
        # Datos
        for row_idx, row_data in enumerate(data, start=2):
            for col_idx, header in enumerate(headers, start=1):
                cell = worksheet.cell(row=row_idx, column=col_idx)
                cell.value = row_data.get(header, "")
        
        # Ajustar ancho
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
    
    def _save_csv(self, filepath: str, trans_data: List[Dict]) -> bool:
        """Guarda CSV"""
        try:
            print(f"   Creando CSV con {len(trans_data)} transacciones...")
            
            if not trans_data:
                return False
            
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=trans_data[0].keys())
                writer.writeheader()
                writer.writerows(trans_data)
            
            print(f"   ✅ CSV guardado")
            return True
            
        except Exception as e:
            print(f"   ❌ Error creando CSV: {e}")
            import traceback
            traceback.print_exc()
            return False