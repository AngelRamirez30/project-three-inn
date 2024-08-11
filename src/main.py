import flet as ft
import random
import math
import pandas as pd
import os

# Variables globales
attributes = []
instances = []
current_attribute_index = 0
num_attributes = 0
num_instances = 0
class_name = ""
table_fields = []

def main(page: ft.Page):
    page.title = "Árboles de Decisión"
    page.window.maximized = True
 
    
    table = ft.DataTable(columns=[ft.DataColumn(ft.Text("Tabla vacía"))], rows=[], width=800)
     
    def open_attribute_modal(attribute_index):
        global current_attribute_index
        current_attribute_index = attribute_index
        if attribute_index < num_attributes:
            if attribute_index < len(attributes):
                attribute_name_field.value = attributes[attribute_index][0]
                attribute_type_field.value = attributes[attribute_index][1]
                if attributes[attribute_index][1] == "Nominal":
                    nominal_value1.value = attributes[attribute_index][2][0] if len(attributes[attribute_index][2]) > 0 else ""
                    nominal_value2.value = attributes[attribute_index][2][1] if len(attributes[attribute_index][2]) > 1 else ""
                    nominal_value3.value = attributes[attribute_index][2][2] if len(attributes[attribute_index][2]) > 2 else ""
                    numeric_value1.visible = False
                    numeric_value2.visible = False
                    nominal_value1.visible = True
                    nominal_value2.visible = True
                    nominal_value3.visible = True
                else:
                    numeric_value1.value = str(attributes[attribute_index][2][0])
                    numeric_value2.value = str(attributes[attribute_index][2][1])
                    nominal_value1.visible = False
                    nominal_value2.visible = False
                    nominal_value3.visible = False
                    numeric_value1.visible = True
                    numeric_value2.visible = True
            else:
                attribute_name_field.value = ""
                attribute_type_field.value = ""
                nominal_value1.value = ""
                nominal_value2.value = ""
                nominal_value3.value = ""
                numeric_value1.value = ""
                numeric_value2.value = ""
                nominal_value1.visible = False
                nominal_value2.visible = False
                nominal_value3.visible = False
                numeric_value1.visible = False
                numeric_value2.visible = False

            attribute_modal.actions[0].controls[0].visible = attribute_index > 0
            attribute_modal.actions[0].controls[1].text = "Guardar" if attribute_index == num_attributes - 1 else "Siguiente"
            validate_fields()
            attribute_modal.open = True
            page.update()
        else:
            open_class_modal()

    def open_class_modal():
        class_name_field.value = ""
        class_modal.open = True
        page.update()

    def save_attribute(e):
        global current_attribute_index
        name = attribute_name_field.value.strip()  # Limpiar espacios en el nombre del atributo también
        attr_type = attribute_type_field.value
        if not name:
            return
        
        if attr_type == "Nominal":
            values = []
            # Recoger los valores de los campos y formatearlos como "n. Descripción"
            if nominal_value1.value.strip():
                values.append(f"1. {nominal_value1.value.strip()}")
            if nominal_value2.value.strip():
                values.append(f"2. {nominal_value2.value.strip()}")
            if nominal_value3.value.strip():
                values.append(f"3. {nominal_value3.value.strip()}")
            
            # Verificar que al menos dos valores están siendo ingresados
            if len(values) < 2:
                page.update()
                return
        else:
            try:
                values = [int(numeric_value1.value.strip()), int(numeric_value2.value.strip())]
            except ValueError:
                page.update()
                return

        if current_attribute_index < len(attributes):
            attributes[current_attribute_index] = (name, attr_type, values)
        else:
            attributes.append((name, attr_type, values))

        current_attribute_index += 1
        attribute_modal.open = False
        page.update()
        if current_attribute_index < num_attributes:
            open_attribute_modal(current_attribute_index)
        else:
            open_class_modal()

    def previous_attribute(e):
        global current_attribute_index
        if current_attribute_index > 0:
            current_attribute_index -= 1
            attribute_modal.open = False
            page.update()
            open_attribute_modal(current_attribute_index)

    def check_table_completion():
        all_filled = True
        for row in table_fields:
            for field in row:
                if isinstance(field, ft.Dropdown) and not field.value:
                    all_filled = False
                    break
            if not all_filled:
                break
        calculate_button.disabled = not all_filled
        page.update()

    def generate_table():
        global table_fields
        table_fields.clear()

        # Definir las columnas de la tabla aquí, después de que class_name_field esté disponible
        table.columns = [ft.DataColumn(ft.Text(attr[0])) for attr in attributes] + [ft.DataColumn(ft.Text(class_name_field.value))]

        table.rows.clear()  # Limpiar las filas

        for _ in range(num_instances):
            row = []
            for attr_name, attr_type, values in attributes:
                if attr_type == "Nominal":
                    dropdown_options = [ft.dropdown.Option(value) for value in values]
                    dropdown = ft.Dropdown(options=dropdown_options, expand=1)
                    dropdown.on_change = check_table_completion  # Asegura que el evento esté asignado después de la creación
                    row.append(ft.DataCell(dropdown))
                else:
                    x1, x2 = values
                    dropdown = ft.Dropdown(
                        options=[
                            ft.dropdown.Option(f"<{x1}"),
                            ft.dropdown.Option(f"{x1}-{x2}"),
                            ft.dropdown.Option(f">{x2}")
                        ],
                        expand=1
                    )
                    dropdown.on_change = check_table_completion  # Asegura que el evento esté asignado después de la creación
                    row.append(ft.DataCell(dropdown))
            class_dropdown = ft.Dropdown(options=[ft.dropdown.Option("0"), ft.dropdown.Option("1")], expand=1)
            class_dropdown.on_change = check_table_completion  # Asegura que el evento esté asignado después de la creación
            row.append(ft.DataCell(class_dropdown))
            table.rows.append(ft.DataRow(cells=row))  # Añadir la fila a la tabla

        num_attributes_field.disabled = True
        num_instances_field.disabled = True
        generate_button.disabled = True
        fill_random_button.disabled = False
        pick_file_button.disabled = False
        delete_table_button.disabled = False

        calculate_button.disabled = True  # Deshabilitar el botón inicialmente

        table.update()
        page.update()

    page.update()

    def save_class(e):
        global class_name
        if not class_name_field.value.strip():
            page.update()
            return

        class_name = class_name_field.value.strip()  # Guardar el nombre de la clase

        class_modal.open = False
        page.update()
        generate_table()

    def fill_randomly(e):
        for row in table_fields:
            for i, (attr_name, attr_type, values) in enumerate(attributes):
                if attr_type == "Nominal":
                    row[i].value = random.choice(values)
                else:
                    x1, x2 = values
                    row[i].value = random.choice([f"<{x1}", f"{x1}-{x2}", f">{x2}"])
            row[-1].value = random.choice(["0", "1"])
        table.update()

    def add_empty_row_to_table():
        row = []
        for attr_name, attr_type, values in attributes:
            if attr_type == "Nominal":
                dropdown = ft.Dropdown(
                    options=[ft.dropdown.Option(v) for v in values], 
                    expand=1,
                    on_change=lambda e: check_table_completion()  # Añadir on_change para validar la tabla
                )
            else:
                x1, x2 = values
                dropdown = ft.Dropdown(
                    options=[
                        ft.dropdown.Option(f"<{x1}"),
                        ft.dropdown.Option(f"{x1}-{x2}"),
                        ft.dropdown.Option(f">{x2}")
                    ],
                    expand=1,
                    on_change=lambda e: check_table_completion()  # Añadir on_change para validar la tabla
                )
            row.append(dropdown)

        class_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option("0"), ft.dropdown.Option("1")],
            expand=1,
            on_change=lambda e: check_table_completion()  # Añadir on_change para validar la tabla
        )
        row.append(class_dropdown)
        
        table_fields.append(row)
        table.rows.append(ft.DataRow(cells=[ft.DataCell(cell) for cell in row]))

        # Actualizar la tabla y la página
        table.update()
        page.update()

        
    def update_table_with_excel_data(df):
        global num_instances

        # Limpiar las filas existentes en la tabla y en table_fields
        table.rows.clear()
        table_fields.clear()

        all_valid = True  # Bandera para rastrear si todos los datos son válidos

        # Asegurarse de tener suficientes filas en la tabla
        for i, row in enumerate(df.itertuples(index=False), start=0):
            table_row = []
            for j, (attr_name, attr_type, values) in enumerate(attributes):
                cell_value = str(row[j]).strip()  # Limpieza de espacios alrededor del valor

                if attr_type == "Nominal":
                    try:
                        nominal_value = int(cell_value)
                        matched_value = next((v for v in values if v.startswith(f"{nominal_value}.")), "")
                        dropdown = ft.Dropdown(options=[ft.dropdown.Option(v) for v in values], 
                                            value=matched_value, 
                                            expand=1,
                                            on_change=lambda e: check_table_completion())
                        if not matched_value:
                            all_valid = False
                    except ValueError:
                        dropdown = ft.Dropdown(options=[ft.dropdown.Option(v) for v in values], 
                                            expand=1,
                                            on_change=lambda e: check_table_completion())
                        all_valid = False
                else:  # Numeric
                    clean_value = cell_value.replace(" ", "")
                    valid_options = [f"<{values[0]}", f"{values[0]}-{values[1]}", f">{values[1]}"]
                    dropdown = ft.Dropdown(options=[ft.dropdown.Option(opt) for opt in valid_options], 
                                        value=clean_value if clean_value in valid_options else None,
                                        expand=1,
                                        on_change=lambda e: check_table_completion())
                    if clean_value not in valid_options:
                        all_valid = False

                table_row.append(ft.DataCell(dropdown))
            
            class_value = str(row[-1]).strip()  # Extraer el valor de la clase
            class_dropdown = ft.Dropdown(options=[ft.dropdown.Option("0"), ft.dropdown.Option("1")], 
                                        value=class_value if class_value in ["0", "1"] else None,
                                        expand=1,
                                        on_change=lambda e: check_table_completion())
            if class_value not in ["0", "1"]:
                all_valid = False
            
            table_row.append(ft.DataCell(class_dropdown))
            table.rows.append(ft.DataRow(cells=table_row))
            table_fields.append([cell.content for cell in table_row])  # Guardar los controles para futuras referencias

        num_instances_from_excel = len(df)  # Número de instancias del Excel

        # Si hay menos instancias en el Excel que el número configurado, agregar filas vacías
        if num_instances > num_instances_from_excel:
            all_valid = False  # No permitir que el botón de cálculo se habilite
            for _ in range(num_instances - num_instances_from_excel):
                add_empty_row_to_table()

        num_instances = max(num_instances, num_instances_from_excel)  # Ajustar el número de instancias

        # Actualizar la tabla y la página
        table.update()
        page.update()

        # Habilitar el botón de calcular si todos los datos son válidos y no hay filas vacías agregadas
        calculate_button.disabled = not all_valid
        page.update()

    def load_excel_data(result):
        if not result.files:
            display_error("No se seleccionó ningún archivo.")
            return

        file_path = result.files[0].path
        if not (file_path.endswith('.xls') or file_path.endswith('.xlsx')):
            display_error("Por favor, suba un archivo Excel válido (.xls o .xlsx).")
            return

        try:
            df = pd.read_excel(file_path, header=None, skiprows=1)  # Asumiendo que la primera fila es el encabezado
            if len(df.columns) != num_attributes + 1:
                display_error("El número de columnas no coincide con el número de atributos y la clase.")
                return

            update_table_with_excel_data(df)
        except Exception as e:
            display_error(str(e))

    def display_error(message):
        snackbar = ft.SnackBar(
            content=ft.Text(message, color=ft.colors.WHITE),
            bgcolor=ft.colors.RED,
            duration=3000            
        )
        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()


    def confirm_delete(e):
        delete_confirmation_dialog.open = True
        page.update()

    def delete_table(e):
        global attributes, instances, current_attribute_index, num_attributes, num_instances, table_fields
        attributes.clear()
        instances.clear()
        table_fields.clear()
        current_attribute_index = 0
        num_attributes = 0
        num_instances = 0
        num_attributes_field.value = ""
        num_instances_field.value = ""
        num_attributes_field.disabled = False
        num_instances_field.disabled = False
        generate_button.disabled = False
        fill_random_button.disabled = True
        pick_file_button.disabled = True
        delete_table_button.disabled = True
        calculate_button.disabled = True
        table.rows.clear()
        table.columns = [ft.DataColumn(ft.Text("Tabla vacía"))]
        delete_confirmation_dialog.open = False
        page.update()
    
    def calculate_results(e):
        # Realiza los cálculos de entropía, ganancia, y nodo raíz
        overall_entropy, gains, root_node = calculate_entropy_and_gain(attributes, instances)
        
        # Crear las filas de la tabla de resultados
        results_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Atributo", size=18)),
                ft.DataColumn(ft.Text("Ganancia de Información", size=18)),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(attr, size=16)),
                    ft.DataCell(ft.Text(f"{gain:.4f}", size=16)),
                ]) for attr, gain in gains.items()
            ]
        )

        # Muestra los resultados en un popup
        results_popup = ft.AlertDialog(
            title=ft.Text("Resultados de los Cálculos", size=24),
            content=ft.Column([
                ft.Text(f"Entropía General: {overall_entropy:.4f}", size=18),
                ft.Text("Ganancias de Información:", size=18),
                results_table,
                ft.Text(f"El Nodo Raíz sugerido es: {root_node}", size=18),
            ], scroll="always")
        )
        
        page.overlay.append(results_popup)
        results_popup.open = True
        page.update()

    def calculate_entropy_and_gain(attributes, instances):
        # Convertir las filas actuales en la tabla en una lista de instancias para procesar
        processed_instances = []
        for row in table_fields:
            instance = []
            for field in row:
                if isinstance(field, ft.Dropdown):
                    instance.append(field.value.split(".")[0] if field.value else None)
            processed_instances.append(instance)
        
        # Reemplaza las instancias con las procesadas
        instances = processed_instances

        # Función para calcular la entropía
        def entropy(instances):
            positive_count = sum(1 for instance in instances if instance[-1] == "1")
            negative_count = len(instances) - positive_count
            total_count = len(instances)
            
            if positive_count == 0 or negative_count == 0:
                return 0
            
            p_positive = positive_count / total_count
            p_negative = negative_count / total_count
            
            return -(p_positive * math.log2(p_positive) + p_negative * math.log2(p_negative))

        # Función para calcular la ganancia de información
        def gain(attribute_index, instances):
            subsets = {}
            for instance in instances:
                value = instance[attribute_index]
                if value not in subsets:
                    subsets[value] = []
                subsets[value].append(instance)
            
            weighted_entropy = sum(
                (len(subset) / len(instances)) * entropy(subset)
                for subset in subsets.values()
            )
            return entropy(instances) - weighted_entropy

        overall_entropy = entropy(instances)
        gains = {attributes[i][0]: gain(i, instances) for i in range(len(attributes))}
        root_node = max(gains, key=gains.get)
        
        return overall_entropy, gains, root_node

    def start_attribute_input(e):
        global num_attributes, num_instances, attributes
        if not num_attributes_field.value.isdigit() or not num_instances_field.value.isdigit():
            page.update()
            return
        
        num_attributes = int(num_attributes_field.value)
        num_instances = int(num_instances_field.value)
        
        if num_attributes < 3 or num_attributes > 5:
            page.update()
            return
        
        attributes.clear()  # Asegúrese de limpiar los atributos anteriores antes de comenzar
        open_attribute_modal(0)

    def on_attribute_type_change(e):
        if attribute_type_field.value == "Nominal":
            nominal_value1.visible = True
            nominal_value2.visible = True
            nominal_value3.visible = True
            numeric_value1.visible = False
            numeric_value2.visible = False
        else:
            nominal_value1.visible = False
            nominal_value2.visible = False
            nominal_value3.visible = False
            numeric_value1.visible = True
            numeric_value2.visible = True
        validate_fields()
        page.update()

    def validate_fields(e=None):
        name_filled = bool(attribute_name_field.value)
        attr_type = attribute_type_field.value
        if attr_type == "Nominal":
            values_filled = sum(bool(v) for v in [nominal_value1.value, nominal_value2.value, nominal_value3.value]) >= 2
        else:
            values_filled = bool(numeric_value1.value) and bool(numeric_value2.value)
        
        next_button.disabled = not (name_filled and values_filled)
        page.update()

    def restrict_input(e):
        # Limpiar espacios y validar el input para campos numéricos
        e.control.value = e.control.value.strip()
        if not (e.control.value.isdigit() or (e.control.value.startswith('-') and e.control.value[1:].isdigit()) or (e.control.value.startswith('+') and e.control.value[1:].isdigit())):
            e.control.value = ''.join(filter(lambda x: x.isdigit() or x in '-+', e.control.value.strip()))
        validate_fields()
        page.update()
        
    def restrict_attributes_input(e):
        if e.control.value:  # Solo si hay un valor ingresado
            e.control.value = e.control.value[-1]  # Mantener solo el último dígito ingresado
            if e.control.value not in ["3", "4", "5"]:
                e.control.value = ""  # Borra el valor si no es 3, 4 o 5
        page.update()

        
    def restrict_instances_input(e):
        if not e.control.value.isdigit():
            e.control.value = ''.join(filter(str.isdigit, e.control.value))
        page.update()
        
    file_picker = ft.FilePicker(on_result=load_excel_data)
    page.overlay.append(file_picker)

    pick_file_button = ft.ElevatedButton(text="Seleccionar archivo", on_click=lambda _: file_picker.pick_files(), disabled=True)

    # Define UI elements
    num_attributes_field = ft.TextField(label="Número de Atributos (min=3, max=5)", width=350, on_change=restrict_attributes_input)
    num_instances_field = ft.TextField(label="Número de Instancias", width=250, on_change=restrict_instances_input)
    generate_button = ft.ElevatedButton(text="Generar Tabla", on_click=start_attribute_input)
    fill_random_button = ft.ElevatedButton(text="Llenado Aleatorio", on_click=fill_randomly, disabled=True)
    delete_table_button = ft.ElevatedButton(text="Eliminar Tabla", on_click=confirm_delete, disabled=True)
    calculate_button = ft.ElevatedButton(
        text="Calcular Resultados", 
        on_click=calculate_results, 
        disabled=True  # Inicia deshabilitado
    )
    
    # Attribute modal
    attribute_name_field = ft.TextField(label="Nombre del Atributo", on_change=validate_fields)
    attribute_type_field = ft.Dropdown(label="Tipo de Dato", options=[
        ft.dropdown.Option("Nominal"),
        ft.dropdown.Option("Numérico")
    ], on_change=on_attribute_type_change)
    nominal_value1 = ft.TextField(label="Valor para 1", visible=False, on_change=validate_fields)
    nominal_value2 = ft.TextField(label="Valor para 2", visible=False, on_change=validate_fields)
    nominal_value3 = ft.TextField(label="Valor para 3", visible=False, on_change=validate_fields)
    numeric_value1 = ft.TextField(label="Número 1", visible=False, on_change=restrict_input)
    numeric_value2 = ft.TextField(label="Número 2", visible=False, on_change=restrict_input)
    
    next_button = ft.ElevatedButton(text="Siguiente", on_click=save_attribute, disabled=True)
    
    attribute_modal = ft.AlertDialog(
        title=ft.Text("Ingresar Atributo"),
        content=ft.Column([
            attribute_name_field,
            attribute_type_field,
            nominal_value1,
            nominal_value2,
            nominal_value3,
            numeric_value1,
            numeric_value2,
        ], height=300),
        actions=[
            ft.Row(
                [
                    ft.ElevatedButton(text="Atrás", on_click=previous_attribute),
                    next_button
                ]
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    # Class modal
    class_name_field = ft.TextField(label="Nombre de la Clase", on_change=lambda e: setattr(next_button_class, "disabled", not bool(class_name_field.value)) or page.update())
    next_button_class = ft.ElevatedButton(text="Guardar", on_click=save_class, disabled=True)
    class_modal = ft.AlertDialog(
        title=ft.Text("Ingresar Clase"),
        content=ft.Column([
            class_name_field,
        ], height=300),
        actions=[
            next_button_class
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    # Delete confirmation dialog
    delete_confirmation_dialog = ft.AlertDialog(
        title=ft.Text("Confirmar"),
        content=ft.Text("¿Está seguro de que desea eliminar la tabla?"),
        actions=[
            ft.ElevatedButton(text="Cancelar", on_click=lambda e: setattr(delete_confirmation_dialog, "open", False) or page.update()),
            ft.ElevatedButton(text="Eliminar", on_click=delete_table),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    page.overlay.append(attribute_modal)
    page.overlay.append(class_modal)
    page.overlay.append(delete_confirmation_dialog)
    
    # Define layout
    page.add(
    ft.Column(
        [
            ft.Row(
                [
                    ft.Text("Árboles de Decisión", size=36, weight=ft.FontWeight.BOLD, )
                ],
                alignment=ft.MainAxisAlignment.CENTER, 
            ),
            ft.Row(
                [
                    num_attributes_field,
                    num_instances_field,
                    generate_button
                ],
                alignment=ft.MainAxisAlignment.CENTER, 
            ),
            ft.Row(
                [
                    fill_random_button,
                    pick_file_button,
                    delete_table_button,
                    calculate_button
                ],
                alignment=ft.MainAxisAlignment.CENTER, 
            ),
            # Tabla con scroll, centrada horizontalmente, y al inicio verticalmente
            ft.Container(
                content=ft.Row(
                    [
                        ft.Column(
                            [table],
                            alignment=ft.MainAxisAlignment.START, 
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                            scroll="always",
                            expand=True
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True
                ),
                alignment=ft.alignment.top_center,
                expand=True
            )
        ],
        alignment=ft.MainAxisAlignment.START, 
        expand=True
    )
)

ft.app(target=main)
