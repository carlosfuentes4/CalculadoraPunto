import flet as ft
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MainWindow:
    def __init__(self,page:ft.Page):
        self.page=page
        #valor del banner,vinil...
        #tipos
        self.tipos = {
            "lona": 0.20,
            "vinil": 0.25,
            "estampado":1.25,
            "fotografia":0.54,
            "sticker en pvc":0.6,
            "uv dtf":1.6,
            "dtf textil":0.95,

        }
        self.page_setup()
        self.create_component()
        self.build_ui()
        self.page.update()

    def page_setup(self):
        self.page.title="Calculadora de precios de Punto Escolar"
        self.page.window.width=500
        self.page.window.height=400
        self.page.bgcolor=ft.colors.BLUE_GREY_900

    def create_component(self):
        self.title= ft.Row([
                ft.Image(
                    src=resource_path("icon.png"),
                    height=40,
                    width=40
                ),  
                ft.Text("Calcula precio del producto",color="#ffffff",size=20,italic=True,
                        weight=ft.FontWeight.BOLD)
            ],alignment=ft.MainAxisAlignment.CENTER)
        
        self.textfield_1=ft.TextField(
            width=140,
            height=50,
            hint_text="Ancho",
            color=ft.colors.WHITE,
            border_color="#ffffff",
            
        )
        self.textfield_2=ft.TextField(
            width=140,
            height=50,
            hint_text="Alto",
            color=ft.colors.WHITE,
            border_color="#ffffff",
        )
        self.textfield_cantidad=ft.TextField(
            width=60,
            height=50,
            hint_text="Alto",
            color=ft.colors.WHITE,
            border_color="#ffffff",
        )
        self.textfield_descuento=ft.TextField(
            width=60,
            height=50,
            hint_text="Alto",
            color=ft.colors.WHITE,
            border_color="#ffffff",
        )
        self.unidades=ft.Dropdown(
            label="Unidad de medida",
            border_color=ft.colors.WHITE,
            value="pulgadas",
            width=150,
            options=[ft.dropdown.Option("pulgadas"),
                     ft.dropdown.Option("metros"),
                     ft.dropdown.Option("pies"),
                     ft.dropdown.Option("centimetros"),
                     ft.dropdown.Option("milimetros"),
            ],
            color=ft.colors.AMBER_700
        )
        #tipo del producto
        self.tipos_drop=ft.Dropdown(
            label="Producto",
            border_color=ft.colors.WHITE,
            # bgcolor=ft.colors.BLACK,
            value="lona",
            width=150,
            options=[ft.dropdown.Option("lona"),
                     ft.dropdown.Option("vinil"),
                     ft.dropdown.Option("estampado"),
                     ft.dropdown.Option("fotografia"),
                     ft.dropdown.Option("sticker en pvc"),
                     ft.dropdown.Option("uv dtf"),
                    #  ft.dropdown.Option("dtf textil"),
            ],
            color=ft.colors.AMBER_700
        )

        self.result_text=ft.Text(
            "0.00",
            # bgcolor="#ffffff",
            size=30,
            color="#ffffff",
            weight=ft.FontWeight.BOLD
        )

        self.result_button=ft.ElevatedButton(
           content=ft.Row([
                ft.Icon(ft.icons.CALCULATE_SHARP),
                ft.Text("Calcular",size=26,color="#ffffff"),
            ],alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=ft.colors.AMBER_800,
            width=200,
            height=50,
            on_click=self.calculate
        )
        
        #prueba
        # self.page.add(self.title)
        # self.page.add(self.textfield_1)
        # self.page.add(self.unidades)
        # self.page.add(self.result_text)
        # self.page.add(self.result_button)

    def build_ui(self):
        main_card=ft.Column(
            controls=[
                self.title,
                ft.Container(height=25),
                ft.Row([self.textfield_1,
                        self.textfield_2,
                        ],spacing=40,alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=5),
                #unidades y tipos
                ft.Container(content=ft.Row([self.unidades,self.tipos_drop],alignment=ft.MainAxisAlignment.CENTER,spacing=50),
                             alignment=ft.alignment.center),

                #resultado
                ft.Container(content=ft.Row([ft.Icon(ft.icons.CHEVRON_RIGHT_OUTLINED,size=50),
                            self.result_text],alignment=ft.MainAxisAlignment.CENTER,spacing=-15),
                            height=40,alignment=ft.alignment.center),
                ft.Container(height=5),
                ft.Container(content=self.result_button,alignment=ft.alignment.center),
            ]
        )

        self.page.add(main_card)

    def is_number(self,valor1:str,valor2:str):
        if not valor1 or not valor2:
            self.show_message("Debes llenar los campos de ancho y alto")
            return False
        try:
            float(valor1)
            float(valor2)
            return True
        except Exception as e:
            self.show_message(f"Debes poner solamente valores numericos.\nerror:{e}")
            return False
        
    
    def show_message(self,message):
        dlg=ft.AlertDialog(
            title=ft.Text("Alerta!",color="#ffffff"),
            content=ft.Text(message,color="#FFFFFF"),
            bgcolor=ft.colors.BLACK26,
            actions=[ft.TextButton("OK",on_click=lambda e:self.page.close(dlg))]
        )
        self.page.open(dlg)

    def calculate(self,_):
        val1=self.textfield_1.value
        val2=self.textfield_2.value
        unidad=self.unidades.value
        regulador = 0

        
        #CALCULO
        if self.is_number(val1,val2):

            if float(val1)<=0 or float(val2)<=0:
                    self.show_message("El ancho y alto deben sel mayores a 0.")
                    self.result_text.value="intenta denuevo"
                    self.page.update()
                    return

            try:
                ancho=float(val1)
                alto=float(val2)
            
                #calular area en pulgadas
                ancho_in=self.to_inches(ancho,unidad)
                alto_in=self.to_inches(alto,unidad)
                area_in=ancho_in*alto_in


                if self.tipos_drop.value=="lona" and (ancho_in < 24 and alto_in<24):
                    pass

                resultado=area_in*self.tipos[self.tipos_drop.value] #calculo de total------------
                if self.tipos_drop.value=="fotografia" and (ancho_in<=7 or alto_in<10):
                    resultado+=12
                self.result_text.value=f"{resultado:.2f} Lps."

                self.page.update()
            except Exception as e:
                self.show_message(f"error: {e}")
       
    
    def to_inches(self, valor, unidad):
        conversion = {
            "pulgadas": 1,
            "pies": 12,
            "metros": 39.3701,
            "centimetros": 0.393701,
            "milimetros": 0.0393701
        }

        return valor * conversion[unidad]
    



def main(page:ft.Page):
    app=MainWindow(page)

if __name__=="__main__":

    ft.app(
        target=main,
        
    )