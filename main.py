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

def validateInput(count, price):
    if not (count and price and (re.search('[a-zA-Z]', count)) and (re.search('[a-zA-Z]', price))):
        return True
    else:
        return False        

ui = Builder.load_file("main.kv") # after class definitions
class MainApp(App):
    def build(self):
        return ui

    def change_screen(self, screen_name, *args):
        screen_manager = self.root.ids['screen_manager']
        screen_manager.current = screen_name

    def calculate(self, screen_name):
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

            amount = float(self.root.ids["home_screen"].ids["output_total"].text) + float(count) * float(price)
            self.root.ids["home_screen"].ids["output_total"].text = str(amount)

            self.root.ids[screen_name].ids["input_count"].text = ""
            self.root.ids[screen_name].ids["input_price"].text = ""
        else:
            print("ERROR")   


MainApp().run()