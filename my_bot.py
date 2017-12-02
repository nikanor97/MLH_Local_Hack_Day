# coding=utf-8

import time
import json
import os

from http.server import BaseHTTPRequestHandler, HTTPServer

class DialogFlowHandler(BaseHTTPRequestHandler):

    def do_GET(s):
        s.send_response(200)
        s.end_headers()
        s.wfile.write('Test string')

    def do_POST(s):
        print('some good words')
        s.send_response(200)
        s.send_header('Content-type', 'application/json')
        s.end_headers()
        message = 'Test message'
        df_response = dict({
            'speech': message,
            'displayText': message,
            'data': {},
            'contextOut': [],
            'source': ''
        })
        s.wfile.write(json.dumps(df_response))
        print('some bad words')

if __name__ == '__main__':
    port = 0
    server_class = HTTPServer
    httpd = server_class(('', port), DialogFlowHandler)
    print(time.asctime(), 'Server started on port %s' % port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
