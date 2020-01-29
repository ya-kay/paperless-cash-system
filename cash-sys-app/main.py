from kivy.app import App
from kivy.lang import  Builder
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.animation import Animation
from fpdf import FPDF, HTMLMixin
from functools import partial
from datetime import datetime

import re
import requests
import random
import string
import io

import configparser
import mysql.connector

import qrcode

### doesnt needed cause no keyboard pops up, inputtext readonly, write with numpad
# from kivy.core.window import Window
# Window.keyboard_anim_args = {'d': .2, 't': 'in_out_expo'}
# Window.softinput_mode = "below_target"



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
class LoadingScreen(Screen):
    pass

class FPDF(FPDF):
    def header(self):
        # Select Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Move to the right
        self.cell(self.w/4)
        # Framed title
        self.cell(self.w/2, 10, 'Beleg: Yaniks Backstube', 1, 0, 'C')
        self.cell(self.w/4)
        # Line break
        self.ln(20)


def validateInput(count, price):
    ### TODO: creat regex just allow numbers and dot and comma
    if (count and price and (re.search('[a-zA-Z]', count)) and (re.search('[a-zA-Z]', price))):
        return False
    elif ((float(count) <= 0) or (float(price) <= 0)):
        return False
    else:
        return True        
        

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

    def on_start(self):
        anim = Animation(color=[1,1,1,1], duration=3)
        anim.start(self.root.ids["loading_screen"].ids["lb_loading_screen"])
        Clock.schedule_once(partial(self.change_screen, "home_screen"), 3.7)

    def change_screen(self, screen_name, *args):
        if(len(args) > 1):
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
            col_width = self.pdf.w / 3.3
            if(len(args) > 0):
                self.pdf.cell(col_width, self.pdf.font_size*1.5,txt=args[0].ids["product_name"].text, border=1)
            else:
                self.pdf.cell(col_width, self.pdf.font_size*1.5, "Eingabe", border=1)

            self.pdf.cell(col_width, self.pdf.font_size*1.5,txt=(count + " x " + str("{:.2f}".format(float(price)) + " EUR")), border=1)
            self.pdf.cell(col_width, self.pdf.font_size*1.5,txt=str("{:.2f}".format(float(amount)) + " EUR"), border=1)
            self.pdf.ln(self.pdf.font_size*1.5)    
              
            self.root.ids[screen_name].ids["input_count"].text = ""
            self.root.ids[screen_name].ids["input_price"].text = ""
        else:
            print("ERROR")

    def checkFinish(self):
        if self.amount_total == 0:
            self.change_screen("home_screen")
        else: 
            self.root.ids["finish_screen"].ids["output_total"].text = self.root.ids["home_screen"].ids["output_total"].text
            self.change_screen("finish_screen")

    def finishPayment(self):
        col_width = self.pdf.w / 3.3

        total = self.root.ids["finish_screen"].ids["output_total"].text
        input = self.root.ids["finish_screen"].ids["input_money"].text
        back = self.root.ids["finish_screen"].ids["money_back"].text

        if(total == "" or input == "" or back == ""):
            self.change_screen("home_screen")   
        else:
            self.pdf.cell(col_width, self.pdf.font_size*1.5, "Total", border=1)
            self.pdf.cell(col_width, self.pdf.font_size*1.5,txt= "", border=1)
            self.pdf.cell(col_width, self.pdf.font_size*1.5,txt= (str("{:.2f}".format(float(total))) + " EUR"), border=1)
            self.pdf.ln(self.pdf.font_size*1.5)    

            self.pdf.cell(col_width, self.pdf.font_size*1.5, "Gegeben", border=1)
            self.pdf.cell(col_width, self.pdf.font_size*1.5,txt= "", border=1)
            self.pdf.cell(col_width, self.pdf.font_size*1.5,txt= (str("{:.2f}".format(float(input))) + " EUR"), border=1)
            self.pdf.ln(self.pdf.font_size*1.5)

            self.pdf.cell(col_width, self.pdf.font_size*1.5, "Zurück", border=1)
            self.pdf.cell(col_width, self.pdf.font_size*1.5,txt= "", border=1)
            self.pdf.cell(col_width, self.pdf.font_size*1.5,txt= (str("{:.2f}".format(float(back))) + " EUR"), border=1)
            self.pdf.ln(self.pdf.font_size*3)

            now = datetime.now()
            self.pdf.cell(self.pdf.w, self.pdf.font_size*1.5, now.strftime("%d/%m/%Y %H:%M:%S"), border=0, align="C")
            self.pdf.ln(self.pdf.font_size*1.5) 

            self.change_screen("qr_screen")     
                   
    def finish(self, mode):
        
        random_pdf_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(64)]) + '.pdf'
        db_cursor.execute("INSERT INTO links (random_string, is_used) VALUES(%s, %s)", (random_pdf_name, 0))
        mydb.commit()

        # safe pdf content as string, CAREFUL since python 3.x need encode("latin-1") https://pyfpdf.readthedocs.io/en/latest/reference/output/index.html)

        pdf_string = self.pdf.output("", "S").encode("latin-1")
        if mode == "qr":
            requests.post('http://192.168.178.82:8125/post', files={random_pdf_name: pdf_string}, headers={"file_name": random_pdf_name})
        elif mode == "print":
            print("Print job")

        self.storno()
        self.change_screen("home_screen")


       
    def storno(self):
        self.root.ids["input_screen"].ids["input_count"].text = ""
        self.root.ids["input_screen"].ids["input_price"].text = ""
        self.root.ids["input_screen_m"].ids["input_count"].text = ""
        self.root.ids["input_screen_m"].ids["input_price"].text = "" 
        self.root.ids["home_screen"].ids["output_total"].text = "0"

        self.root.ids["finish_screen"].ids["output_total"].text = ""
        self.root.ids["finish_screen"].ids["input_money"].text = ""
        self.root.ids["finish_screen"].ids["money_back"].text = ""

        self.amount_total = 0
        self.initPDF()


    def resetInputs(self):
        self.root.ids["input_screen"].ids["input_count"].text = ""
        self.root.ids["input_screen"].ids["input_price"].text = ""
        self.root.ids["input_screen_m"].ids["input_count"].text = ""
        self.root.ids["input_screen_m"].ids["input_price"].text = ""

    def initPDF(self):
        self.pdf = FPDF()
        self.pdf.add_page()
        self.pdf.set_font("Arial", size=12)         

MainApp().run()


###### TODO: Abbrechen --> inputtext leeren [X]
###### TODO: Amount == 0; nicht done drücken [X]
###### TODO: Storno --> alles 0, neues PDF [X]
###### TODO: Design --> HomeScreen InputText dicker, größer, mehr Abstand zum Top [X]
###### TODO: Produkte --> Label Hintergrundfarbe, Schrift größer, dicker [X]
###### TODO: QR-Screen -> remove image, ask if qr or print [X]
###### TODO: Finish-Screen -> total, gegeben, zurück -> pdf print also [X]
###### TODO: ADD Header to PDF with name and date, time



###### TODO: admin-console to edit database products
###### TODO: add validation of one minute
