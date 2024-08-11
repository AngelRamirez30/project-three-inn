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
    
    error_text = ft.Text(value="", color="red")
    page.add(error_text)

    
    def open_attribute_modal(attribute_index):
        global current_attribute_index
        current_attribute_index = attribute_index
        if attribute_index < num_attributes:
            if attribute_index < len(attributes):
                attribute_name_field.value = attributes[attribute_index][0]
                attribute_type_field.value = attributes[attribute_index][1]
                if attributes[attribute_index][1] == "Nominal":
                    nominal_value1.value = attributes[attribute_index][2][0]
                    nominal_value2.value = attributes[attribute_index][2][1]
                    nominal_value3.value = attributes[attribute_index][2][2]
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
                results_text.value = "Por favor, ingrese al menos dos valores para atributos nominales."
                page.update()
                return
        else:
            try:
                values = [int(numeric_value1.value.strip()), int(numeric_value2.value.strip())]
            except ValueError:
                results_text.value = "Por favor, ingrese valores numéricos válidos."
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


    def generate_table():
        global table_fields
        table_fields.clear()
        table.controls.clear()
        header_row = [ft.Text(attr[0], expand=1) for attr in attributes]
        header_row.append(ft.Text(class_name, expand=1))  # Utilizar el valor guardado en class_name
        
        table.controls.append(ft.Row(controls=header_row))
        
        for _ in range(num_instances):
            row = []
            for attr_name, attr_type, values in attributes:
                if attr_type == "Nominal":
                    dropdown_options = [ft.dropdown.Option(value) for value in values]
                    dropdown = ft.Dropdown(options=dropdown_options, expand=1)
                    row.append(dropdown)
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
                    row.append(dropdown)
            class_dropdown = ft.Dropdown(options=[ft.dropdown.Option("0"), ft.dropdown.Option("1")], expand=1)
            row.append(class_dropdown)
            table_fields.append(row)
            table.controls.append(ft.Row(controls=row))
        
        num_attributes_field.disabled = True
        num_instances_field.disabled = True
        generate_button.disabled = True
        fill_random_button.disabled = False
        pick_file_button.disabled = False
        calculate_button.disabled = False
        delete_table_button.disabled = False
        
        table.update()
        page.update()

    def save_class(e):
        global class_name
        if not class_name_field.value.strip():
            error_text.value = "Debe ingresar un nombre para la clase."
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

    def update_table_with_excel_data(df):
        global num_instances
        # Asegurarse de tener suficientes filas en la tabla
        while len(table_fields) < len(df):
            add_empty_row_to_table()

        for i, row in enumerate(df.itertuples(index=False), start=0):
            for j, (attr_name, attr_type, values) in enumerate(attributes):
                cell_value = str(row[j]).strip()  # Limpieza de espacios alrededor del valor

                if attr_type == "Nominal":
                    try:
                        nominal_value = int(cell_value)
                        # Buscar un valor que comience con el número correcto
                        matched_value = next((v for v in values if v.startswith(f"{nominal_value}.")), "")
                        if matched_value:
                            table_fields[i][j].value = matched_value
                        else:
                            table_fields[i][j].value = ""
                    except ValueError:
                        table_fields[i][j].value = ""
                else:  # Numeric
                    clean_value = cell_value.replace(" ", "")
                    valid_options = [f"<{values[0]}", f"{values[0]}-{values[1]}", f">{values[1]}"]
                    if clean_value in valid_options:
                        table_fields[i][j].value = clean_value
                    else:
                        table_fields[i][j].value = ""
            
            # Ahora manejamos la última columna (la clase)
            class_value = str(row[-1]).strip()  # Extraer el valor de la clase
            if class_value in ["0", "1"]:  # Validar que el valor de la clase sea '0' o '1'
                table_fields[i][-1].value = class_value
            else:
                table_fields[i][-1].value = ""  # Si no es válido, dejarlo en blanco

        num_instances = max(num_instances, len(df))
        table.update()


    def add_empty_row_to_table():
        row = []
        for attr_name, attr_type, values in attributes:
            if attr_type == "Nominal":
                dropdown = ft.Dropdown(options=[ft.dropdown.Option(v) for v in values], expand=1)
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
            row.append(dropdown)
        class_dropdown = ft.Dropdown(options=[ft.dropdown.Option("0"), ft.dropdown.Option("1")], expand=1)
        row.append(class_dropdown)
        table_fields.append(row)
        table.controls.append(ft.Row(controls=row))
   
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
        # Aquí puedes usar un control de texto que ya esté en la página para mostrar errores
        error_text.value = message  # Asegúrate de tener un control `Text` llamado `error_text` en tu página
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
        table.controls.clear()
        table.controls.append(ft.Text("Tabla vacía"))
        delete_confirmation_dialog.open = False
        page.update()
    
    def calculate_results(e):
        # Realiza los cálculos de entropía, ganancia, y nodo raíz
        overall_entropy, gains, root_node = calculate_entropy_and_gain(attributes, instances)
        
        # Prepara los textos de resultado
        entropy_text = ft.Text(f"Entropía General: {overall_entropy:.4f}")
        gains_text = ft.Text("Ganancias de Información:")
        gains_content = ft.Column([ft.Text(f"{attr}: {gain:.4f}") for attr, gain in gains.items()])
        root_node_text = ft.Text(f"El Nodo Raíz sugerido es: {root_node}")
        
        # Muestra los resultados en un popup
        results_popup = ft.AlertDialog(
            title=ft.Text("Resultados de los Cálculos"),
            content=ft.Column([
                entropy_text,
                gains_text,
                gains_content,
                root_node_text,
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
            results_text.value = "Por favor, ingrese números válidos para el número de atributos y el número de instancias."
            page.update()
            return
        
        num_attributes = int(num_attributes_field.value)
        num_instances = int(num_instances_field.value)
        
        if num_attributes < 3 or num_attributes > 5:
            results_text.value = "El número de atributos debe estar entre 3 y 5."
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
        
    file_picker = ft.FilePicker(on_result=load_excel_data)
    page.overlay.append(file_picker)

    pick_file_button = ft.ElevatedButton(text="Seleccionar archivo", on_click=lambda _: file_picker.pick_files(), disabled=True)

    # Define UI elements
    num_attributes_field = ft.TextField(label="Número de Atributos (min=3, max=5)", width=200)
    num_instances_field = ft.TextField(label="Número de Instancias", width=200)
    generate_button = ft.ElevatedButton(text="Generar Tabla", on_click=start_attribute_input)
    fill_random_button = ft.ElevatedButton(text="Llenado Aleatorio", on_click=fill_randomly, disabled=True)
    delete_table_button = ft.ElevatedButton(text="Eliminar Tabla", on_click=confirm_delete, disabled=True)
    calculate_button = ft.ElevatedButton(
        text="Calcular Resultados", 
        on_click=calculate_results, 
        disabled=True  # Inicia deshabilitado
    )

    results_text = ft.Text(value="", max_lines=None)  # Using max_lines=None to allow multiline text
    
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
        ]),
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
        ]),
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
    table = ft.Column([ft.Text("Tabla vacía")])
    page.add(
        ft.Column([
            ft.Row([num_attributes_field, num_instances_field, generate_button]),
            ft.Row([fill_random_button, pick_file_button, delete_table_button, calculate_button]),
            table,
            results_text
        ])
    )

ft.app(target=main)
