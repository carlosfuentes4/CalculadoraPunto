import flet as ft
import os
import sys
import json

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

CONFIG_FILE = "config.json"

# Configuración por defecto (incluye parámetros de descuento por volumen)
DEFAULT_CONFIG = {
    "admin_password": "",
    "products": {
        "lona": {"price": 0.20, "min_w": 0, "min_h": 0, "inc": 0, "min_qty_desc": 0, "desc_porcentaje": 0},
        "vinil": {"price": 0.25, "min_w": 0, "min_h": 0, "inc": 0, "min_qty_desc": 0, "desc_porcentaje": 0},
        "estampado": {"price": 1.25, "min_w": 0, "min_h": 0, "inc": 0, "min_qty_desc": 0, "desc_porcentaje": 0},
        "fotografia": {"price": 0.54, "min_w": 7, "min_h": 10, "inc": 12, "min_qty_desc": 0, "desc_porcentaje": 0},
        "sticker en pvc": {"price": 0.60, "min_w": 0, "min_h": 0, "inc": 0, "min_qty_desc": 0, "desc_porcentaje": 0},
        "uv dtf": {"price": 1.60, "min_w": 0, "min_h": 0, "inc": 0, "min_qty_desc": 0, "desc_porcentaje": 0},
        "dtf textil": {"price": 0.95, "min_w": 0, "min_h": 0, "inc": 0, "min_qty_desc": 0, "desc_porcentaje": 0}
    }
}

class MainWindow:
    def __init__(self, page: ft.Page):
        self.page = page
        self.load_config()
        self.page_setup()
        self.create_component()
        self.build_ui()
        self.page.update()

    def load_config(self):
        """Carga la configuración o crea una si no existe."""
        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            self.config = DEFAULT_CONFIG.copy()
        else:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                self.config = json.load(f)
            
            # Migración: Si se usa un config.json viejo, le agregamos los campos nuevos
            for prod, data in self.config.get("products", {}).items():
                if "min_qty_desc" not in data:
                    data["min_qty_desc"] = 0
                if "desc_porcentaje" not in data:
                    data["desc_porcentaje"] = 0
            self.save_config()

    def save_config(self):
        """Guarda la configuración actual en el JSON."""
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

    def page_setup(self):
        self.page.title = "Calculadora de precios de Punto Escolar"
        self.page.window.width = 500
        self.page.window.height = 550
        self.page.bgcolor = ft.colors.BLUE_GREY_900

    def create_component(self):
        self.title = ft.Row([
            ft.Image(src=resource_path("icon.png"), height=40, width=40, error_content=ft.Icon(ft.icons.CALCULATE)),  
            ft.Text("Calcula precio del producto", color="#ffffff", size=20, italic=True, weight=ft.FontWeight.BOLD),
            ft.Container(width=10),
            ft.IconButton(icon=ft.icons.SETTINGS, icon_color=ft.colors.WHITE, on_click=self.check_admin_auth, tooltip="Configuración")
        ], alignment=ft.MainAxisAlignment.CENTER)
        
        self.textfield_1 = ft.TextField(width=140, height=50, hint_text="Ancho", color=ft.colors.WHITE, border_color="#ffffff")
        self.textfield_2 = ft.TextField(width=140, height=50, hint_text="Alto", color=ft.colors.WHITE, border_color="#ffffff")
        
        # Solo pedimos la Cantidad. El descuento ahora es automático según configuración.
        self.textfield_cantidad = ft.TextField(width=140, height=50, hint_text="Cantidad (Ej: 1)", color=ft.colors.WHITE, border_color="#ffffff")
        
        self.unidades = ft.Dropdown(
            label="Unidad",
            border_color=ft.colors.WHITE,
            value="pulgadas",
            width=150,
            options=[
                ft.dropdown.Option("pulgadas"),
                ft.dropdown.Option("metros"),
                ft.dropdown.Option("pies"),
                ft.dropdown.Option("centimetros"),
                ft.dropdown.Option("milimetros"),
            ],
            color=ft.colors.AMBER_700
        )
        
        opciones_productos = [ft.dropdown.Option(prod) for prod in self.config["products"].keys()]
        self.tipos_drop = ft.Dropdown(
            label="Producto",
            border_color=ft.colors.WHITE,
            value=opciones_productos[0].key if opciones_productos else None,
            width=150,
            options=opciones_productos,
            color=ft.colors.AMBER_700
        )

        self.result_text = ft.Text("0.00", size=30, color="#ffffff", weight=ft.FontWeight.BOLD)
        
        # Texto de ayuda para mostrar si se aplicó un descuento o incremento en pantalla
        self.info_text = ft.Text("", size=12, color=ft.colors.AMBER_300, italic=True)

        self.result_button = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.icons.CALCULATE_SHARP),
                ft.Text("Calcular", size=26, color="#ffffff"),
            ], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=ft.colors.AMBER_800,
            width=200,
            height=50,
            on_click=self.calculate
        )

    def build_ui(self):
        main_card = ft.Column(
            controls=[
                self.title,
                ft.Container(height=10),
                ft.Row([self.textfield_1, self.textfield_2], spacing=20, alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([self.textfield_cantidad], alignment=ft.MainAxisAlignment.CENTER), # Solo cantidad visible
                ft.Container(height=5),
                ft.Row([self.unidades, self.tipos_drop], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                ft.Container(height=10),
                ft.Row([ft.Icon(ft.icons.CHEVRON_RIGHT_OUTLINED, size=50, color=ft.colors.WHITE), self.result_text], alignment=ft.MainAxisAlignment.CENTER, spacing=-15),
                ft.Container(content=self.info_text, alignment=ft.alignment.center), # Texto que avisa de descuentos/incrementos
                ft.Container(height=5),
                ft.Container(content=self.result_button, alignment=ft.alignment.center),
            ]
        )
        self.page.add(main_card)

    def is_number(self, valor1: str, valor2: str):
        if not valor1 or not valor2:
            self.show_message("Debes llenar los campos de ancho y alto")
            return False
        try:
            float(valor1)
            float(valor2)
            return True
        except Exception:
            self.show_message("Debes poner solamente valores numéricos en ancho y alto.")
            return False
        
    def show_message(self, message):
        dlg = ft.AlertDialog(
            title=ft.Text("Atención", color="#ffffff"),
            content=ft.Text(message, color="#ffffff"),
            bgcolor=ft.colors.BLUE_GREY_800,
            actions=[ft.TextButton("OK", on_click=lambda e: self.page.close(dlg))]
        )
        self.page.open(dlg)

    def calculate(self, _):
        val1 = self.textfield_1.value
        val2 = self.textfield_2.value
        unidad = self.unidades.value
        producto_seleccionado = self.tipos_drop.value
        self.info_text.value = "" # Reseteamos el texto de info

        if not producto_seleccionado:
            self.show_message("Seleccione un producto")
            return

        if self.is_number(val1, val2):
            if float(val1) <= 0 or float(val2) <= 0:
                self.show_message("El ancho y alto deben ser mayores a 0.")
                self.result_text.value = "0.00"
                self.page.update()
                return

            try:
                ancho = float(val1)
                alto = float(val2)
                ancho_in = self.to_inches(ancho, unidad)
                alto_in = self.to_inches(alto, unidad)
                area_in = ancho_in * alto_in

                # Parámetros del producto desde el JSON
                params = self.config["products"][producto_seleccionado]
                precio = params["price"]
                min_w = params.get("min_w", 0)
                min_h = params.get("min_h", 0)
                inc = params.get("inc", 0)
                min_qty_desc = params.get("min_qty_desc", 0)
                desc_porcentaje = params.get("desc_porcentaje", 0)

                # 1. Calculo de área base (Por una unidad)
                costo_unidad = area_in * precio 
                
                info_mensajes = []
                
                # 2. Aplicar condicional (Incremento si la medida es muy pequeña)
                if min_w > 0 and min_h > 0:
                    if ancho_in <= min_w or alto_in <= min_h:
                        costo_unidad += inc
                        info_mensajes.append(f"+{inc} Lps (Tamaño pequeño)")

                # Manejar Cantidad
                try:
                    cantidad = int(self.textfield_cantidad.value) if self.textfield_cantidad.value else 1
                except:
                    cantidad = 1
                
                # Subtotal antes de descuentos globales por cantidad
                resultado_total = costo_unidad * cantidad

                # 3. Aplicar descuento automático por cantidad
                if min_qty_desc > 0 and desc_porcentaje > 0:
                    if cantidad >= min_qty_desc:
                        descuento_aplicado = resultado_total * (desc_porcentaje / 100)
                        resultado_total -= descuento_aplicado
                        info_mensajes.append(f"-{desc_porcentaje}% descuento (Volumen)")

                # Actualizar pantalla
                self.result_text.value = f"{resultado_total:.2f} Lps."
                if info_mensajes:
                    self.info_text.value = "Aplicado: " + " | ".join(info_mensajes)
                    
                self.page.update()

            except Exception as e:
                self.show_message(f"Error interno: {e}")
       
    def to_inches(self, valor, unidad):
        conversion = {
            "pulgadas": 1,
            "pies": 12,
            "metros": 39.3701,
            "centimetros": 0.393701,
            "milimetros": 0.0393701
        }
        return valor * conversion[unidad]

    # ================= FUNCIONES DE ADMINISTRACIÓN ================= #

    def check_admin_auth(self, e):
        password = self.config.get("admin_password", "")
        input_pass = ft.TextField(password=True, can_reveal_password=True, hint_text="Contraseña")
        
        def verify_pass(e):
            if input_pass.value == password:
                self.page.close(dlg)
                self.open_settings_panel()
            else:
                self.show_message("Contraseña incorrecta.")

        def create_pass(e):
            if input_pass.value.strip() == "":
                self.show_message("La contraseña no puede estar vacía.")
                return
            self.config["admin_password"] = input_pass.value
            self.save_config()
            self.page.close(dlg)
            self.open_settings_panel()

        if password == "":
            dlg = ft.AlertDialog(
                title=ft.Text("Crear Contraseña de Admin"),
                content=ft.Column([ft.Text("Cree una contraseña para la configuración."), input_pass], tight=True),
                actions=[ft.TextButton("Guardar", on_click=create_pass)]
            )
        else:
            dlg = ft.AlertDialog(
                title=ft.Text("Ingresar como Administrador"),
                content=ft.Column([ft.Text("Ingrese su contraseña:"), input_pass], tight=True),
                actions=[ft.TextButton("Entrar", on_click=verify_pass)]
            )
        
        self.page.open(dlg)

    def open_settings_panel(self):
        input_name = ft.TextField(label="Nombre Producto", width=150)
        input_price = ft.TextField(label="Precio x Pulgada²", width=150)
        input_min_w = ft.TextField(label="Ancho Mínimo (in)", width=150, value="0")
        input_min_h = ft.TextField(label="Alto Mínimo (in)", width=150, value="0")
        input_inc = ft.TextField(label="Incremento (+ Lps)", width=150, value="0")
        
        # Nuevos campos para Descuento por Volumen (Cantidad)
        input_min_qty = ft.TextField(label="A partir de (Cant.)", width=150, value="0", hint_text="Ej: 50")
        input_desc_porc = ft.TextField(label="% Descuento", width=150, value="0", hint_text="Ej: 10")

        def load_product_data(e):
            if dropdown_edit.value in self.config["products"]:
                prod = self.config["products"][dropdown_edit.value]
                input_name.value = dropdown_edit.value
                input_price.value = str(prod.get("price", 0))
                input_min_w.value = str(prod.get("min_w", 0))
                input_min_h.value = str(prod.get("min_h", 0))
                input_inc.value = str(prod.get("inc", 0))
                input_min_qty.value = str(prod.get("min_qty_desc", 0))
                input_desc_porc.value = str(prod.get("desc_porcentaje", 0))
                self.page.update()

        dropdown_edit = ft.Dropdown(
            label="Seleccionar para editar",
            options=[ft.dropdown.Option(p) for p in self.config["products"].keys()],
            on_change=load_product_data,
            width=200
        )

        def save_product(e):
            name = input_name.value.strip().lower()
            if not name:
                self.show_message("El nombre no puede estar vacío.")
                return
            try:
                self.config["products"][name] = {
                    "price": float(input_price.value),
                    "min_w": float(input_min_w.value),
                    "min_h": float(input_min_h.value),
                    "inc": float(input_inc.value),
                    "min_qty_desc": float(input_min_qty.value),
                    "desc_porcentaje": float(input_desc_porc.value)
                }
                self.save_config()
                
                opciones = [ft.dropdown.Option(p) for p in self.config["products"].keys()]
                self.tipos_drop.options = opciones
                dropdown_edit.options = opciones
                
                self.show_message(f"Producto '{name}' guardado correctamente.")
                self.page.update()
            except Exception as err:
                self.show_message(f"Ingrese solo números en los campos de valores. Error: {err}")

        settings_dlg = ft.AlertDialog(
            title=ft.Text("Configuración de Productos y Reglas"),
            content=ft.Column([
                dropdown_edit,
                ft.Divider(),
                ft.Row([input_name, input_price]),
                ft.Text("1. Regla de incremento si es menor al tamaño:", size=13, color=ft.colors.AMBER),
                ft.Row([input_min_w, input_min_h]),
                input_inc,
                ft.Text("2. Regla de descuento por alta cantidad:", size=13, color=ft.colors.AMBER),
                ft.Row([input_min_qty, input_desc_porc]),
            ], scroll=ft.ScrollMode.AUTO, tight=True),
            actions=[
                ft.TextButton("Guardar", on_click=save_product),
                ft.TextButton("Cerrar", on_click=lambda e: self.page.close(settings_dlg))
            ]
        )
        self.page.open(settings_dlg)

def main(page: ft.Page):
    app = MainWindow(page)

if __name__ == "__main__":
    ft.app(target=main)