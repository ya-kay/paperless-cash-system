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
class QRScreen(Screen):
    pass


### init PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

#res = cursor.rowcount

def validateInput(count, price):
    ### TODO: creat regex just allow numbers and dot and comma
    if not (count and price and (re.search('[a-zA-Z]', count)) and (re.search('[a-zA-Z]', price))):
        return True
    else:
        return False        

        

class MainApp(App):
    ui = Builder.load_file("main.kv") # after class definitions
    amount_total = 0;
    product_price_array = []

    def build(self):
        db_cursor.execute("SELECT product_name, product_price FROM products WHERE fav = 1");
        for product, price in db_cursor.fetchall():
             self.product_price_array.append((product, price))
        self.product_price_array = self.product_price_array[0:18]
    
        for index, id in enumerate(self.ui.ids["home_screen"].ids):
            if(id.startswith("custom_btn")):
                print(index-2, id)
                if(len(self.product_price_array) > (index-2)):
                    self.ui.ids["home_screen"].ids[id].text = self.product_price_array[index-2][0]
                    self.ui.ids["home_screen"].ids[id].amount = self.product_price_array[index-2][1]
                else:    
                    self.ui.ids["home_screen"].ids[id].text = "Custom"
                    self.ui.ids["home_screen"].ids[id].amount = "0.00"
        # self.ui.ids["home_screen"].ids["custom_btn_1"].text = "updated")
        # for product, price in self.product_price_array:
        #     print(product, price)
        #     self.root.ids["home_screen"].ids[""]

        

        # for index, id in enumerate(self.root.ids['home_screen'].ids):
        #     if(id.startswith("custom_btn")):
        #         id.parent.text = self.product_price_array[index-2][0]
        #         id.parent.amount = self.product_price_array[index-2][1]
        #        #  ### load products from db
        return self.ui

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
            if "," in count:
                count = count.replace(",", ".")
            if "," in price:
                price = price.replace(",", ".")

            amount =  float(count) * float(price)
            self.amount_total = float(self.root.ids["home_screen"].ids["output_total"].text) + amount
            self.root.ids["home_screen"].ids["output_total"].text = str(round(self.amount_total,2))

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
            self.change_screen("home_screen")
        else:
            random_pdf_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(64)]) + '.pdf'
            db_cursor.execute("INSERT INTO links (random_string, is_used) VALUES(%s, %s)", (random_pdf_name, 0))
            mydb.commit()
            pdf.output("./receipts/" + random_pdf_name)
            self.change_screen("home_screen")

            img = qrcode.make("URL; http://192.168.178.82:8125/" + random_pdf_name)
            img.save("image.jpg")

            self.root.ids["home_screen"].ids["output_total"].text = "0"
            self.change_screen("qr_screen")


        ### Upload not required
        ### with open('report.xls', 'rb') as f:
        ### r = requests.post('http://httpbin.org/post', files={'report.xls': f})

        ### MAYBE: show QR on own screen

    def storno(self):
            pass 

MainApp().run()