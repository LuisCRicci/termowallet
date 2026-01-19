"""
Generador de Reportes - ✅ CORREGIDO PARA ANDROID
Archivo: src/business/report_generator.py

✅ FIX CRÍTICO: Eliminar page.save_file() y copiar directamente
"""

import csv
import sys
import os
import tempfile
import shutil
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
        
        # FilePicker para guardar archivos
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
        """Genera reporte mensual"""
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

            # ✅ GUARDAR DATOS PARA USAR EN EL CALLBACK
            return self._prepare_file_save(
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
        """Genera reporte de rango personalizado"""
        try:
            print(f"\n📊 Generando reporte personalizado: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
            
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
            
            total_income = sum(t.amount for t in transactions if t.transaction_type == "income")
            total_expenses = sum(t.amount for t in transactions if t.transaction_type == "expense")
            
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
                {"Concepto": "Fecha Inicio", "Valor": start_date.strftime("%d/%m/%Y")},
                {"Concepto": "Fecha Fin", "Valor": end_date.strftime("%d/%m/%Y")},
                {"Concepto": "Días", "Valor": (end_date - start_date).days + 1},
                {"Concepto": "Total Ingresos", "Valor": total_income},
                {"Concepto": "Total Gastos", "Valor": total_expenses},
                {"Concepto": "Balance", "Valor": total_income - total_expenses},
                {"Concepto": "Nº Transacciones", "Valor": len(transactions)}
            ]
            
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
            
            filename = f"Reporte_TermoWallet_{start_date.strftime('%d%m%Y')}_al_{end_date.strftime('%d%m%Y')}.{format}"
            
            return self._prepare_file_save(
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
        """Genera reporte anual"""
        try:
            print(f"\n📊 Generando reporte anual: {year}")
            
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
            
            total_income = sum(t.amount for t in all_transactions if t.transaction_type == "income")
            total_expenses = sum(t.amount for t in all_transactions if t.transaction_type == "expense")
            
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
            
            summary_data = [
                {"Concepto": "Año", "Valor": year},
                {"Concepto": "Total Ingresos", "Valor": total_income},
                {"Concepto": "Total Gastos", "Valor": total_expenses},
                {"Concepto": "Balance", "Valor": total_income - total_expenses},
                {"Concepto": "Tasa de Ahorro (%)", "Valor": round((total_income - total_expenses) / total_income * 100, 2) if total_income > 0 else 0},
                {"Concepto": "Nº Transacciones", "Valor": len(all_transactions)}
            ]
            
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
            
            filename = f"Reporte_TermoWallet_Anual_{year}.{format}"
            
            return self._prepare_file_save(
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
    
    
    # ✅ NUEVO MÉTODO: Preparar y abrir diálogo de guardado
    def _prepare_file_save(
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
        """Prepara los datos y abre el diálogo para guardar"""
        
        print("\n" + "="*60)
        print("💾 PREPARANDO GUARDADO DE REPORTE")
        print("="*60)
        print(f"   📄 Archivo: {filename}")
        print(f"   📊 Formato: {format}")
        print(f"   📝 Transacciones: {len(transactions_data)}")
        print("="*60 + "\n")
        
        try:
            # Guardar datos pendientes
            self._pending_data = {
                "filename": filename,
                "format": format,
                "transactions_data": transactions_data,
                "summary_data": summary_data,
                "expenses_data": expenses_data,
                "income_data": income_data,
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
                    
                    return {
                        "success": True,
                        "filepath": None,
                        "message": "Selecciona ubicación para guardar"
                    }
                    
                except Exception as e:
                    print(f"❌ Error abriendo diálogo: {e}")
                    error_msg = f"❌ Error al abrir diálogo: {str(e)}"
                    if callback_error:
                        callback_error(error_msg)
                    return {
                        "success": False,
                        "filepath": None,
                        "message": error_msg
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
            print(f"❌ Error en preparación: {e}")
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
    
    # ✅ FIX CRÍTICO: Callback cuando usuario selecciona ubicación
    def _on_file_save_result(self, e: ft.FilePickerResultEvent):
        """Callback cuando usuario selecciona ubicación - FIX CRÍTICO APLICADO"""
        
        print("\n" + "🔥"*30)
        print("CALLBACK _on_file_save_result ACTIVADO")
        print("🔥"*30)
        
        if not hasattr(self, '_pending_data'):
            print("⚠️ No hay datos pendientes")
            return
        
        data = self._pending_data
        
        print(f"📦 Datos pendientes encontrados:")
        print(f"   Archivo: {data.get('filename', 'N/A')}")
        print(f"   Formato: {data.get('format', 'N/A')}")
        print(f"   Transacciones: {len(data.get('transactions_data', []))}")
        
        if e.path is None:
            print("❌ Usuario canceló - e.path es None")
            
            if data.get('callback_success'):
                data['callback_success'](
                    "",
                    "ℹ️ Guardado cancelado"
                )
            return
        
        # Usuario eligió ubicación
        save_path = e.path
        print(f"\n{'='*60}")
        print(f"💾 INICIANDO GUARDADO")
        print(f"{'='*60}")
        print(f"   📍 Ubicación elegida: {save_path}")
        print(f"   📂 Directorio: {os.path.dirname(save_path)}")
        print(f"   📄 Nombre archivo: {os.path.basename(save_path)}")
        print(f"   📊 Formato: {data['format']}")
        print(f"   🤖 Android: {self.is_android}")
        print(f"   📝 Transacciones a guardar: {len(data['transactions_data'])}")
        print(f"{'='*60}\n")
        
        try:
            # ✅ Verificar directorio
            directory = os.path.dirname(save_path)
            if directory:
                print(f"📁 Verificando directorio: {directory}")
                if os.path.exists(directory):
                    print(f"   ✅ Directorio existe")
                    print(f"   ✅ Escritura permitida: {os.access(directory, os.W_OK)}")
                else:
                    print(f"   ⚠️ Directorio NO existe")
            
            # ✅ ESCRIBIR DIRECTAMENTE en la ubicación final
            if data['format'] == "xlsx" and openpyxl:
                print(f"\n📊 === INICIANDO GUARDADO EXCEL ===")
                success = self._save_excel(
                    save_path,
                    data['transactions_data'],
                    data['summary_data'],
                    data['expenses_data'],
                    data['income_data']
                )
                print(f"📊 === FIN GUARDADO EXCEL (success={success}) ===\n")
            else:
                print(f"\n📄 === INICIANDO GUARDADO CSV ===")
                success = self._save_csv(
                    save_path,
                    data['transactions_data']
                )
                print(f"📄 === FIN GUARDADO CSV (success={success}) ===\n")
            
            if not success:
                error_msg = "❌ La función de guardado retornó False"
                print(error_msg)
                if data.get('callback_error'):
                    data['callback_error'](error_msg)
                return
            
            # Verificar que se creó
            print(f"🔍 Verificando archivo guardado...")
            if not os.path.exists(save_path):
                error_msg = "❌ ERROR CRÍTICO: Archivo NO existe después del guardado"
                print(error_msg)
                if data.get('callback_error'):
                    data['callback_error'](error_msg)
                return
            
            file_size = os.path.getsize(save_path)
            print(f"✅ Archivo verificado:")
            print(f"   📏 Tamaño: {file_size} bytes")
            print(f"   📍 Ubicación: {save_path}")
            
            if file_size == 0:
                error_msg = "❌ ERROR: Archivo creado pero está VACÍO (0 bytes)"
                print(error_msg)
                if data.get('callback_error'):
                    data['callback_error'](error_msg)
                return
            
            print(f"{'='*60}")
            print(f"🎉 ¡GUARDADO EXITOSO!")
            print(f"{'='*60}\n")
            
            if data.get('callback_success'):
                data['callback_success'](
                    save_path,
                    f"✅ ¡Reporte guardado exitosamente!\n\n"
                    f"📍 Ubicación:\n{save_path}\n\n"
                    f"📊 Tamaño: {file_size:,} bytes"
                )
                
        except Exception as ex:
            print(f"\n{'='*60}")
            print(f"❌ EXCEPCIÓN EN CALLBACK")
            print(f"{'='*60}")
            print(f"Tipo: {type(ex).__name__}")
            print(f"Mensaje: {ex}")
            import traceback
            traceback.print_exc()
            print(f"{'='*60}\n")
            
            if data.get('callback_error'):
                data['callback_error'](
                    f"❌ Error crítico al guardar:\n{type(ex).__name__}: {str(ex)}"
                )
        
        # Limpiar datos pendientes
        delattr(self, '_pending_data')
        print("🧹 Datos pendientes limpiados\n")
    
    def _save_excel(
        self,
        filepath: str,
        trans_data: List[Dict],
        summary_data: List[Dict],
        expenses_data: List[Dict],
        income_data: List[Dict]
    ) -> bool:
        """Guarda Excel - ✅ FIX ANDROID: Usar método correcto según plataforma"""
        wb = None
        
        try:
            if not openpyxl:
                print(f"      ❌ openpyxl NO está disponible")
                raise ImportError("openpyxl no disponible")
            
            print(f"      📊 Iniciando creación de Excel...")
            print(f"      📝 Transacciones: {len(trans_data)}")
            print(f"      📍 Ruta destino: {filepath}")
            print(f"      🤖 Android: {self.is_android}")
            
            # ✅ PASO 1: Crear workbook en memoria
            print(f"      🔨 Creando workbook...")
            wb = openpyxl.Workbook()
            
            # ✅ PASO 2: Hoja Resumen
            print(f"      📄 Creando hoja 'Resumen'...")
            ws_summary = wb.active
            ws_summary.title = "Resumen"
            self._write_data_to_sheet(ws_summary, summary_data)
            print(f"      ✓ Resumen creado")
            
            # ✅ PASO 3: Hoja Transacciones
            print(f"      📄 Creando hoja 'Transacciones'...")
            ws_trans = wb.create_sheet("Transacciones")
            self._write_data_to_sheet(ws_trans, trans_data)
            print(f"      ✓ Transacciones creadas")
            
            # ✅ PASO 4: Hoja Gastos
            if expenses_data:
                print(f"      📄 Creando hoja 'Gastos'...")
                ws_exp = wb.create_sheet("Gastos por Categoría")
                self._write_data_to_sheet(ws_exp, expenses_data)
                print(f"      ✓ Gastos creados")
            
            # ✅ PASO 5: Hoja Ingresos
            if income_data:
                print(f"      📄 Creando hoja 'Ingresos'...")
                ws_inc = wb.create_sheet("Ingresos por Categoría")
                self._write_data_to_sheet(ws_inc, income_data)
                print(f"      ✓ Ingresos creados")
            
            # ✅ FIX CRÍTICO ANDROID: Guardar primero en BytesIO y luego escribir
            print(f"      💾 Guardando archivo...")
            
            if self.is_android:
                # ✅ ANDROID: Usar BytesIO intermedio y page.client_storage
                print(f"      📱 Modo Android: Usando BytesIO + write_bytes")
                from io import BytesIO
                
                # Guardar workbook en memoria
                buffer = BytesIO()
                wb.save(buffer)
                buffer.seek(0)
                excel_bytes = buffer.read()
                buffer.close()
                
                print(f"      📏 Excel en memoria: {len(excel_bytes)} bytes")
                
                # Escribir bytes directamente al archivo
                with open(filepath, 'wb') as f:
                    bytes_written = f.write(excel_bytes)
                    f.flush()
                    os.fsync(f.fileno())
                
                print(f"      ✓ Bytes escritos: {bytes_written}")
                
            else:
                # ✅ DESKTOP: Método tradicional
                print(f"      💻 Modo Desktop: Guardado directo")
                with open(filepath, 'wb') as f:
                    wb.save(f)
                    f.flush()
                    os.fsync(f.fileno())
            
            print(f"      ✓ Guardado completado")
            
            # ✅ PASO 6: Cerrar workbook
            try:
                wb.close()
                print(f"      ✓ Workbook cerrado")
            except:
                pass
            
            # ✅ PASO 7: ESPERAR (crítico en Android)
            import time
            time.sleep(0.5)
            
            # ✅ PASO 8: Verificar archivo
            print(f"      🔍 Verificando archivo creado...")
            
            if not os.path.exists(filepath):
                print(f"      ❌ ERROR: Archivo NO existe")
                return False
            
            file_size = os.path.getsize(filepath)
            print(f"      📏 Tamaño del archivo: {file_size} bytes")
            
            if file_size == 0:
                print(f"      ❌ ERROR: Archivo vacío (0 bytes)")
                return False
            
            if file_size < 1000:
                print(f"      ⚠️ ADVERTENCIA: Archivo muy pequeño ({file_size} bytes)")
            
            # ✅ PASO 9: Verificar que sea un Excel válido
            try:
                test_wb = openpyxl.load_workbook(filepath, read_only=True)
                test_wb.close()
                print(f"      ✓ Excel válido verificado")
            except Exception as verify_err:
                print(f"      ❌ ERROR: Excel corrupto: {verify_err}")
                return False
            
            print(f"      ✅ Excel guardado exitosamente: {file_size} bytes")
            return True
            
        except Exception as e:
            print(f"      ❌ EXCEPCIÓN en _save_excel: {e}")
            print(f"      📋 Tipo de error: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            
            # Limpiar archivo corrupto
            try:
                if os.path.exists(filepath) and os.path.getsize(filepath) == 0:
                    os.remove(filepath)
                    print(f"      🗑️ Archivo vacío eliminado")
            except:
                pass
            
            return False
        
        finally:
            # Asegurar cierre del workbook
            if wb:
                try:
                    wb.close()
                except:
                    pass
    
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
        """Guarda CSV - ✅ FIX ANDROID"""
        try:
            print(f"      Creando CSV con {len(trans_data)} transacciones...")
            
            if not trans_data:
                return False
            
            if self.is_android:
                # ✅ ANDROID: Escribir primero en StringIO, luego a archivo
                print(f"      📱 Modo Android: Usando StringIO + write")
                from io import StringIO
                
                # Crear CSV en memoria
                buffer = StringIO()
                writer = csv.DictWriter(buffer, fieldnames=trans_data[0].keys())
                writer.writeheader()
                writer.writerows(trans_data)
                csv_content = buffer.getvalue()
                buffer.close()
                
                # Escribir al archivo
                with open(filepath, 'w', encoding='utf-8-sig') as f:
                    f.write(csv_content)
                    f.flush()
                    os.fsync(f.fileno())
            else:
                # ✅ DESKTOP: Método tradicional
                print(f"      💻 Modo Desktop: Guardado directo")
                with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=trans_data[0].keys())
                    writer.writeheader()
                    writer.writerows(trans_data)
                    f.flush()
                    os.fsync(f.fileno())
            
            # ✅ Verificar inmediatamente
            import time
            time.sleep(0.3)
            
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"      ✅ CSV guardado: {size} bytes")
                return size > 0
            else:
                print(f"      ❌ Archivo no existe después de guardar")
                return False
            
        except Exception as e:
            print(f"      ❌ Error creando CSV: {e}")
            import traceback
            traceback.print_exc()
            return False