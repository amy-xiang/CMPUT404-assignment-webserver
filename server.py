#  coding: utf-8 
import socketserver, os, time

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
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    # Heavily Referenced Jonathan Cardasis (Feb 7, 2017) 
    # on Github Gist: https://gist.github.com/joncardasis/cc67cfb160fa61a0457d6951eff2aeae

    PACKET_SIZE = 1024
    BASE_PATH = 'www'
    
    def handle(self):
        self.data = self.request.recv(self.PACKET_SIZE).strip()
        print ("Got a request of: %s\n" % self.data)
        
        self.decodedData = self.data.decode('utf-8') 

        (requestMethod, requestFile, contentType) = self.parseHeaders()

        if requestMethod == 'GET':

            filePath =  self.BASE_PATH + requestFile
            print("Serving web page: " + filePath)

            try:
                f = open(filePath, 'rb')
                responseData = f.read()
                f.close()

                responseHeader = self.buildHeaders(200, contentType)

                response = responseHeader.encode('utf-8')
                response += responseData

            except:
                print("File not found. Serving 404 page")
                responseHeader = self.buildHeaders(404, contentType)

                response = responseHeader.encode('utf-8')
            
        
            self.request.sendall(bytearray(response))

    def parseHeaders(self):
        requestMethod = self.decodedData.split(' ')[0]
        requestFile = self.decodedData.split(' ')[1]

        if requestFile == '/':
            requestFile = '/index.html'

        contentType = 'text/' + requestFile.split('.')[1]
        print("Request Method: %s, Request File: %s, Content-Type: %s" % (requestMethod, requestFile, contentType))

        return (requestMethod, requestFile, contentType)

    
    
    def buildHeaders(self, responseCode, contentType):
        header = ''

        if responseCode == 200:
            header += 'HTTP/1.1 200 OK\n'

        elif responseCode == 404:
            header += 'HTTP/1.1 404 Not Found\n'
        
        header += 'Server: CMPUT404-webserver-yangyi1\n'
        header += 'Content-Type: %s\n' % contentType
        header += 'Connection: close\n\n'

        return header



if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
