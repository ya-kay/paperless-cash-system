from kivy.app import App
from kivy.lang import  Builder
from kivy.uix.screenmanager import Screen
import re
from fpdf import FPDF 

class HomeScreen(Screen):
    pass
class InputScreen(Screen):
    pass
class InputScreenM(Screen):
    pass

total = 0;

### init PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

def validateInput(count, price):
    ### todo creat regex just allow numbers and dot and comma
    if not (count and price and (re.search('[a-zA-Z]', count)) and (re.search('[a-zA-Z]', price))):
        return True
    else:
        return False        

ui = Builder.load_file("main.kv") # after class definitions
class MainApp(App):
    def build(self):
        return ui

    def change_screen(self, screen_name, *args):
        if(len(args) > 0):
            self.root.ids[screen_name].ids["product_name"].text = str(args[0])
            self.root.ids[screen_name].ids["input_price"].text = str(args[1])
        screen_manager = self.root.ids['screen_manager']
        screen_manager.current = screen_name

    def calculate(self, screen_name, *args):
        count = self.root.ids[screen_name].ids["input_count"].text
        price = self.root.ids[screen_name].ids["input_price"].text
        if(validateInput(count, price)): 
            count = count.strip()
            price = price.strip()
            print(count)
            print(price)
            if "," in count:
                count = count.replace(",", ".")
            if "," in price:
                price = price.replace(",", ".")

            amount =  float(count) * float(price)
            amount_total = float(self.root.ids["home_screen"].ids["output_total"].text) + amount
            self.root.ids["home_screen"].ids["output_total"].text = str(round(amount_total,2))

            #### write receipt pdf --> TODO: print as Tablr
            if(len(args) > 0):
                content = args[0].ids["product_name"].text + ": " + count + " x " + price + " EUR        " + str(round(amount,2)) + " EUR"
            else:
                content = "Eingabe: " + count + " x " + price + " EUR        " + str(round(amount,2)) + " EUR"   
            pdf.cell(200, 10, txt=content, ln=1, align="C")
            ### 
            self.root.ids[screen_name].ids["input_count"].text = ""
            self.root.ids[screen_name].ids["input_price"].text = ""
        else:
            print("ERROR")
      
    def finish(self):
        ### TODO: new screen -> Betrag gegeben / zurück eingeben / ausrechnen und auf den Beleg schreiben
        pdf.output("simple_demo.pdf")

    def storno(self):
            pass    



MainApp().run()