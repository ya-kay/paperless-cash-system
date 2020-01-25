# paperless-cash-system

- [ ] a python mobile app with https://github.com/kivy/kivy
- [ ] a own written cash system
- [ ] write a reiceipt as pdf
- [X] set up database
- [X] create webserver with one-time-use download-links, TODO: add validation of one minute
- [X] after paying upload receipt on (local) server
- [X] create download-link as QR-Code 
- [X] display QR-Code
- [X] administrate all products with prices in a database (NOT DONE:maybe a own administration console)

# implementation
- building app with kivy, using external packages:fpdf, mysql, qrcode
- building web-server with nodejs, using packages: http, fs, path and mysql
- local mysql-database with MAMP (macOS)
- kivy-app loads products from database, and set up predefined labels with product and set their prices
- with DONE button in the app, a pdf will be created and send to server with 'requests'
- web-server listing on post requests on xxx.xxx.xxx.xxx:YYYY/post to store the pdf file with fs.createWriteStream and request.pipe(WriteStream)
- TODO: qr-code
- web-server handle get-request and check if the requested file wasn't used before and then answer with the pdf file


# building ios app
- python3 toolchain.py create cash-system ~/Desktop/python/cash-sys-app/cash-sys-app
- open cash-system-ios/cash-system.xcodeproj 
- press on cash-system-project -> signing -> choose developer
- before run on system, start with "node server.js" webserver and mysql database

# problems while programming:
- [X] building ios apps: resolved with copying all pip3 installed packages from /usr/local/lib/python3.7/site-packages/ to ./kivy-ios/dist/root/python3/lib/python3.7/site-packages, copying toolchain.py, toolchain.pyc, sh.py and sh.pyc, ... also in the ./kivy-ios/.../site-packages folder (https://github.com/kivy/kivy-ios/issues/320)
- [X] installed failed packages with "python3 toolchain.py pip install PACKAGE"
- [X] can't store files on running iOS system, so use pdf.output("", "S").encode("latin-1") (https://pyfpdf.readthedocs.io/en/latest/reference/output/index.html)
- [ ] locale.setlocale(locale.LC_ALL, 'de_DE') --> running ios doesn't know locale.LC_ALL --> replaced with string format 
