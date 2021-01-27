#  coding: utf-8 
import socketserver, os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Amy Xiang
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

#-------------------------------------------------------------------------------------------#
# Code References:
#   - (handle, parseHeaders, buildHeaders) Jonathan Cardasis (Feb 7, 2017), Date Accessed: JAN 25, 2021
#     on Github Gist: https://gist.github.com/joncardasis/cc67cfb160fa61a0457d6951eff2aeae
#
#   - (lines 125, 126) MDN Web Docs, Date Accessed: JAN 26, 2021 
#     https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/301
#
#   - (lines 107, 143, 149) Python Docs OS, Date Accessed: JAN 27, 2021
#      https://docs.python.org/3/library/os.path.html
#-------------------------------------------------------------------------------------------#

class MyWebServer(socketserver.BaseRequestHandler):
    #initialize constants
    PACKET_SIZE = 1024
    BASE_PATH = 'www'
    BASE_URL = "http://127.0.0.1:8080"


    def handle(self):
        # get request data
        self.data = self.request.recv(self.PACKET_SIZE).strip()
    
        # decode and parse headers
        self.decodedData = self.data.decode('utf-8') 
        (requestMethod, requestFile, contentType) = self.parseHeaders()

        # only accept GET requests
        if requestMethod == 'GET':

            responseData = ''
            filePath =  self.BASE_PATH + requestFile

            try:
                # determine if filepath is in www directory and if path needs redirecting
                redirect = self.verifyPath(filePath)

                if redirect:
                    # send 301 and redirect path
                    correctPath = self.BASE_URL + requestFile + '/'
                    responseHeader = self.buildHeaders(301, correctPath=correctPath)
                else:
                    # send 200 and get file data
                    f = open(filePath, 'rb')
                    responseData = f.read()
                    f.close()

                    responseHeader = self.buildHeaders(200, contentType)
                
            except:
                # send 404, path doesn't exist in www directory
                responseHeader = self.buildHeaders(404)

            response = responseHeader.encode('utf-8')

            if responseData:
                response += responseData
        
        else:
            # send 405, not a GET request
            responseHeader = self.buildHeaders(405)
            response = responseHeader.encode('utf-8')

        #send response
        self.request.sendall(bytearray(response))


    def parseHeaders(self):
        # get request method and file from request
        requestMethod = self.decodedData.split(' ')[0]
        requestFile = self.decodedData.split(' ')[1]
        contentType = ''

        # sets request file as index.html if path ends in /
        if requestFile == '/' or requestFile.endswith('/'):
            requestFile = requestFile + 'index.html'

        # gets file extension
        extension = os.path.splitext(requestFile)[1]

        # sets content-type if html or css
        if extension == '.html' or extension == '.css':
            contentType = 'text/' + extension[1:]
            
        return (requestMethod, requestFile, contentType)

    
    def buildHeaders(self, responseCode, contentType='', correctPath=''):
        header = ''

        # builds header based on response code
        if responseCode == 200:
            header += 'HTTP/1.1 200 OK\n'
            header += 'Content-Type: %s\n' % contentType

        elif responseCode == 301:
            header += 'HTTP/1.1 301 Moved Permanently\n'
            header += 'Location: %s\n' % correctPath
            
        elif responseCode == 404:
            header += 'HTTP/1.1 404 Not Found\n'

        elif responseCode == 405:
            header += 'HTTP/1.1 405 Method Not Allowed\n'

        
        header += 'Server: CMPUT404-webserver-yangyi1\n'
        header += 'Connection: close \n\n'

        return header


    def verifyPath(self, path):
        # gets absolute path of location
        abspath = os.path.abspath(path)

        # determines if path location is in www directory
        if (self.BASE_PATH + '/') in abspath:

            # determines if redirecting is needed
            if os.path.isdir(abspath):
                return True
            
            return False
        
        # raise exception if file not in www
        raise Exception
 

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
