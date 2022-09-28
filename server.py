#  coding: utf-8 
import socketserver
import mimetypes
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

    def createReply(self, request):
        response_code = "200"
        reason_phrase = "OK"
        content = ""
        headers = []

        request_list = request.decode().split()
        #print(request_list)
        request_command = request_list[0]
        request_dir = request_list[1]
        # If the path ends in "/", we return index.html instead
        if request_dir[-1] == "/": 
            request_dir = request_dir + "index.html"

        #Check if the command is GET
        if request_command != "GET":
            response_code = "405"
            reason_phrase = "Method Not Allowed"

        #Try to open the request_dir
        try:
            # Check if client is trying to access files outside www
            path_www = os.getcwd()+"/www"
            path = "./www"+request_dir
            if not os.path.abspath(path).startswith(path_www):
                response_code = "404"
                response_phrase = "Not Found"
            else:
                file = open(path, "r")
                content = file.read()
                headers.append("Content-Type: {}\r\nContent-Length: {}\r\n".format(mimetypes.guess_type(path)[0],len(content)))
        except FileNotFoundError:
            response_code = "404"
            reason_phrase = "Not Found"
        except IsADirectoryError:
            response_code = "301"
            reason_phrase = "Moved Permanently"
        
        #Format our response
        reply = (
            "HTTP/1.1 {} {}\r\n"
            ).format(response_code, reason_phrase)
        for header in headers:
            reply = reply + header
        reply = reply + "\r\n" + content
        #print(reply)
        return reply

    def handle(self):
        self.data = self.request.recv(1024).strip()
        #print ("Got a request of: %s\n" % self.data)

        reply = self.createReply(self.data)
        self.request.sendall(bytearray(reply,'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
