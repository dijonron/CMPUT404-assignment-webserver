#  coding: utf-8 
import socketserver
from urllib.parse import urlparse
from time import strftime, localtime

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Dalton Ronan
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
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    def build_response_header(self, protocol, code, length = '', mime='octet-stream', location=''):
        messages = {'200': 'OK', '301': 'Moved Permanently', '404': 'Not Found', '405': 'Method Not Allowed'}

        status_line = ' '.join([protocol, code, messages[code]])+'\r\n'

        charset = ''
        if mime != 'octet-stream':
            charset = '; charset=utf-8'

        content_type = 'Content-Type: text/{}{}\r\n'.format(mime, charset)

        content_length = ''
        if length:
            content_length += 'Content-Length: {}\r\n'.format(length)

        date = 'Date: {}\r\n'.format(strftime("%a, %d %b %Y %H:%M:%S %Z", localtime()))
        connection = 'Connection: close\r\n'

        if location:
            location = 'Location: {}\r\n'.format(location)

        return status_line + connection + date + content_type + content_length + location + '\r\n'


    def handle(self):
        self.data = self.request.recv(1024)

        # decode the incoming request so we can parse it
        request = self.data.decode()

        # Parse the headers 
        headers, host = request.split('\n')[0:2]
        method, filename, protocol = headers.split()
        host = host.split()[-1]

        # this server can only handle GET; return 405 for any other method
        if method != 'GET':
            response = self.build_response_header(protocol, '405')
            self.request.sendall(bytearray(response, 'utf-8'))
            return
        
        # parse path and file, strip all ../ from path to be secure (i.e. keep it in root)
        url = urlparse(filename)
        path = url.path.lstrip('../')

        if path == '' or path[-1] == '/':
            path += 'index.html'
        try:
            page = open('/'.join(['www', path]))
            content = page.read()
            page.close()
            mime = path.split('.')[-1]

            # Python : Get size of string in bytes
            # https://stackoverflow.com/a/30686735/16792989
            # Answered by : Kris (https://stackoverflow.com/users/3783770/kris)
            # CC BY-SA 3.0
            length = len(content.encode())

            response = self.build_response_header(protocol, '200', length, mime) + content
            self.request.sendall(response.encode())
        except Exception:
            # file not found, try to redirct or send 404
            try:
                page = open('/'.join(['www', path, 'index.html']))
                page.close()
                # if we can open page, build location url and send 301
                # build url by taking /path/ and parse
                location = urlparse('/'.join([path, ''])).geturl()
                content = '<html><head><title>301 Moved Permanently</title></head><body bgcolor="white"><center><h1>301 Moved Permanently</h1></center></body></html>'
                response = self.build_response_header(protocol, '301', 'html', location)
                self.request.sendall(response.encode())
            except Exception:
                response = self.build_response_header(protocol, '404')
                self.request.sendall(response.encode())


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
