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


- Problems while programming:
- [X] building ios apps: resolved with copying all pip3 installed packages from /usr/local/lib/python3.7/site-packages/ to ./kivy-ios/dist/root/python3/lib/python3.7/site-packages, copying toolchain.py, toolchain.pyc, sh.py and sh.pyc also in the ./kivy-ios/.../site-packages
- [X] installed failed packages with python3 toolchain.py pip install PACKAGE
- [X] can't store files on running iOS system, so use pdf.output("", "S").encode("latin-1") (https://pyfpdf.readthedocs.io/en/latest/reference/output/index.html)
