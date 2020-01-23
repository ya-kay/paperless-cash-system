import http.server  
import socketserver 
import os

PORT = 8000

web_dir = os.path.join(os.path.dirname(__file__), 'receipts')
os.chdir(web_dir)

Handler = CustomHTTPRequestHandler
httpd = socketserver.TCPServer(("", PORT), Handler)

print ("Running on Port: " + str(PORT))
httpd.serve_forever()