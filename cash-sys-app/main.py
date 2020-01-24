from kivy.app import App
from kivy.lang import  Builder
from kivy.uix.screenmanager import Screen
from fpdf import FPDF, HTMLMixin
import re
import requests
import random
import string
import io

import configparser
import mysql.connector

import qrcode

from kivy.core.window import Window
Window.keyboard_anim_args = {'d': .2, 't': 'in_out_expo'}
Window.softinput_mode = "below_target"






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

### HTML to PDF
# class HTML2PDF(FPDF, HTMLMixin):
#     pass

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

    ### init PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    def build(self):

        ### load from database
        db_cursor.execute("SELECT product_name, product_price FROM products WHERE fav = 1");
        for product, price in db_cursor.fetchall():
             self.product_price_array.append((product, price))
        self.product_price_array = self.product_price_array[0:18]
    
        for index, id in enumerate(self.ui.ids["home_screen"].ids):
            if(id.startswith("custom_btn")):
                if(len(self.product_price_array) > (index-2)):
                    self.ui.ids["home_screen"].ids[id].text = self.product_price_array[index-2][0]
                    self.ui.ids["home_screen"].ids[id].amount = self.product_price_array[index-2][1]
                else:    
                    self.ui.ids["home_screen"].ids[id].text = "Custom"
                    self.ui.ids["home_screen"].ids[id].amount = "0.00"

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

            #### write receipt pdf
            col_width = self.pdf.w / 3.5
            if(len(args) > 0):
                # content = args[0].ids["product_name"].text + ": " + count + " x " + price + " EUR        " + str(locale.format_string('%.2f', amount, True)) + " EUR"
                self.pdf.cell(col_width, self.pdf.font_size*1.5,txt=args[0].ids["product_name"].text, border=1)
            else:
                self.pdf.cell(col_width, self.pdf.font_size*1.5, "Eingabe", border=1)

            self.pdf.cell(col_width, self.pdf.font_size*1.5,txt=(count + " x " + str("{:.2f}".format(float(price)) + " EUR")), border=1)
            self.pdf.cell(col_width, self.pdf.font_size*1.5,txt=str("{:.2f}".format(float(amount)) + " EUR"), border=1)
            self.pdf.ln(self.pdf.font_size*1.5)    
                # content = "Eingabe: " + count + " x " + price + " EUR        " + str(locale.format_string('%.2f', amount, True)) + " EUR"
                   
                #self.pdf.cell(200, 10, txt=content, ln=1, align="C")
                #  
            self.root.ids[screen_name].ids["input_count"].text = ""
            self.root.ids[screen_name].ids["input_price"].text = ""
        else:
            print("ERROR")
      
    def finish(self):
        
        ### TODO: new screen -> Betrag gegeben / zurück eingeben / ausrechnen und auf den Beleg schreiben
        if self.amount_total == 0:
            self.change_screen("home_screen")
        else:
            random_pdf_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(64)]) + '.pdf'
            db_cursor.execute("INSERT INTO links (random_string, is_used) VALUES(%s, %s)", (random_pdf_name, 0))
            mydb.commit()

            ### TODO: Upload PDF,
            
            ### Upload 
           
            # CAN'T store files on running ios App
            # self.pdf.output("./receipts/" + random_pdf_name)
            # with open("./receipts/" + random_pdf_name, 'rb') as f:


            # safe pdf content as string, CAREFUL since python 3.x need encode("latin-1") https://pyfpdf.readthedocs.io/en/latest/reference/output/index.html)

            pdf_string = self.pdf.output("", "S").encode("latin-1")
            requests.post('http://192.168.178.82:8125/post', files={random_pdf_name: pdf_string}, headers={"file_name": random_pdf_name})


            self.pdf = FPDF()
            self.pdf.add_page()
            self.pdf.set_font("Arial", size=12)

            ### TODO: QRScreen -> select between print and create qrcode
            ### TODO: QRCode displayed on server -> extra screen

            # img = qrcode.make("URL; http://192.168.178.82:8125/" + random_pdf_name)
            # img.save("./images/img_" + random_pdf_name[0:-4]+".jpg")
            # self.root.ids["qr_screen"].ids["qr_image"].source = "./images/img_" + random_pdf_name[0:-4] + ".jpg"


            self.root.ids["home_screen"].ids["output_total"].text = "0"
            self.change_screen("qr_screen")


       
    def storno(self):
            pass 

MainApp().run()