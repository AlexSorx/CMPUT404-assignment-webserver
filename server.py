#  coding: utf-8 
import socketserver
from struct import pack
import os.path
from os import path
import os
from numpy import byte

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#3
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    # Handles 301 incorrect path - path does not contain '.' and does not end in '/'
    def handle_301(self, newPath):
        response ="HTTP/1.1 301 Permanently Moved \r\nLocation"
    
        response+= newPath +"\n\n"
        self.request.sendall(bytearray(response, 'utf-8'))

    # Handles 404 error ie: invalid path request
    def handle_404(self):
        response = "HTTP/1.1 404 Not Found \r\n"
        self.request.sendall(bytearray(response, 'utf-8'))
    # Handles 405 error ie: not GET request
    def handle_405(self):
        response = "HTTP/1.1 405 Method Not Allowed \r\n"
        self.request.sendall(bytearray(response, 'utf-8'))

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        data_decoded = self.data.decode('utf-8')


        lines = data_decoded.split('\r\n')
        line1 = lines[0]
        line1split = line1.split(' ')
        # Split data into request type and path
        request = line1split[0]
        
        fpath = line1split[1]
        fpath = line1split[1]

        self.splitdata = self.data.splitlines()
        self.request_path = self.splitdata[0].split()[1]

       
        # See if we are working with a file and operate accordingly
        if path.isfile('www'+ fpath):

            # Identify file type
            if fpath.endswith('.html'):
                response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\n\n"
                response += open('./www' + fpath, 'r').read()
                self.request.sendall(bytearray(response,'utf-8'))
            elif fpath.endswith('.css'):
                response = "HTTP/1.1 200 OK\r\nContent-Type: text/css\n\n"
                response += open('./www' + fpath, 'r').read()
                self.request.sendall(bytearray(response,'utf-8'))               

        # If file ends in / we know to add to index
        elif fpath[len(fpath)-1]=='/' or path.isfile('www' +fpath):
            fpath+= 'index.html'
            try:
                f = open('./www'+ fpath )
                fdata = f.read()
                if fpath.endswith('.html'):
                    self.request.sendall(b"HTTP/1.1 200 OK\nContent-Type: text/html\n\n")
                elif fpath.endswith('.css'):
                    self.request.sendall(b"HTTP/1.1 200 OK\nContent-Type: text/cssl\n\n")
                else: 
                    self.request.sendall(b"HTTP/1.1 404 Not Found\n\n")
                self.request.sendall(bytearray(fdata, 'utf-8'))
                
            except FileNotFoundError:
                response = "HTTP/1.1 404 Not Found \r\n\r\n"
                self.request.sendall(bytearray(response, 'utf-8'))

         # 301 for conditions not met   
        elif fpath[len(fpath)-1]!='/' and path.exists('www' +fpath):
            new_path =  fpath +"/"
            self.handle_301(new_path)
            relocatedLocation = fpath + "/"

            response = "HTTP/1.1 301 Permanently Moved\r\n \r\nLocation "
            response += relocatedLocation + "\n\n"
            self.request.sendall(bytearray(response,'utf-8'))

        # Conditions for a 405
        elif request.lower()!= 'get' or len(lines)==0 or len(request)==0:
            self.handle_405()


            
        # Conditions for a 404
        elif '/..' in fpath or not path.exists('www' +fpath):
            self.handle_404()
        
    # returns file type html/css 
    def get_file_type(self, path):
        return path.split('.')[-1]

    """""
    # 200 Index handler not used
    def handle_200_index(self, fpath):
            fpath+= 'index.html'
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\n\n"
            response += open('./www' + fpath , 'r').read()
            
            self.request.sendall(bytearray(response,'utf-8'))
    """""


    
       

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()