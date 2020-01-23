from kivy.app import App
from kivy.lang import  Builder
from kivy.uix.screenmanager import Screen
from fpdf import FPDF 
import re
import requests
import random
import string

import configparser
import mysql.connector

import qrcode



### DATABASE init from config.ini
config = configparser.ConfigParser()
config.read('config.ini')
mydb = mysql.connector.connect(
    host = config['mysqlDB']['host'],
    port = config['mysqlDB']['port'],
    user = config['mysqlDB']['user'],
    passwd = config['mysqlDB']['pass'],
    db = config['mysqlDB']['db']
)

db_cursor = mydb.cursor()

### SCREENs init
class HomeScreen(Screen):
    pass
class InputScreen(Screen):
    pass
class InputScreenM(Screen):
    pass
class FinishScreen(Screen):
    pass

amount_total = 0;

### init PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

def validateInput(count, price):
    ### TODO: creat regex just allow numbers and dot and comma
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
            self.amount_total = float(self.root.ids["home_screen"].ids["output_total"].text) + amount
            self.root.ids["home_screen"].ids["output_total"].text = str(round(amount_total,2))

            #### write receipt pdf --> TODO: print as Table
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

        ### TODO: RANDOM Name
        if self.amount_total == 0:
            print("AAA")
            self.change_screen("home_screen")
        else:
            print("BBB")
            random_pdf_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(64)]) + '.pdf'
            db_cursor.execute("INSERT INTO links (random_string, is_used) VALUES(%s, %s)", (random_pdf_name, 0))
            mydb.commit()
            pdf.output("./receipts/" + random_pdf_name)
            self.change_screen("home_screen")

            img = qrcode.make("URL; http://192.168.178.82:8125/" + random_pdf_name)
            img.save("image.jpg")


        ### Upload not required
        ### with open('report.xls', 'rb') as f:
        ### r = requests.post('http://httpbin.org/post', files={'report.xls': f})

        ### MAYBE: show QR on own screen

    def storno(self):
            pass    



MainApp().run()