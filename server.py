#  coding: utf-8 
import socketserver
import os

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

    def build_response_header(self, protocol, code, mime):
        messages = {'200': 'OK', '301': 'Moved Permanently', '404': 'Not Found', '405': 'Method Not Allowed'}

        head = ' '.join([protocol, code, messages[code]])+'\r\n'
        content_type = 'Content-Type: text/{}; charset=utf-8\r\n'.format(mime)

        return head + content_type + '\r\n'


    def handle(self):
        self.data = self.request.recv(1024).strip()

        # decode the incoming request so we can parse it
        request = self.data.decode()

        # Parse the headers 
        headers = request.split('\n')[0].split()
        method, filename, protocol = headers
        
        # this server can only handle GET; return 405 for any other method
        if method != 'GET':
            response = self.build_response_header(protocol, '405', 'html')
            self.request.sendall(bytearray(response, 'utf-8'))
            return
        
        # parse path and file, strip all ../ from path to be secure (i.e. keep it in root)
        path, file = os.path.split(filename)
        path = path.strip('../')

        if file == '':
            file += 'index.html'
        try:
            if path:
                page = open('/'.join(['www', path, file]))
            else:
                page = open('/'.join(['www', file]))
            content = page.read()
            page.close()
            mime = file.split('.')[-1]
            response = self.build_response_header(protocol, '200', mime) + content
            self.request.sendall(response.encode())
        except Exception:
            # file not found, try to redirct or send 404
            try:
                if path:
                    page = open('/'.join(['www', path, file, 'index.html']))
                else:
                    page = open('/'.join(['www', file, 'index.html']))
                
                # if we can open page, send 301 and redirect
                response = self.build_response_header(protocol, '301', 'html')
                self.request.sendall(response.encode())
                content = page.read()
                page.close()
                mime = file.split('.')[-1]
                response = self.build_response_header(protocol, '200', mime) + content
                self.request.sendall(response.encode())
            except Exception:
                response = self.build_response_header(protocol, '404', 'html')
                self.request.sendall(response.encode())


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
