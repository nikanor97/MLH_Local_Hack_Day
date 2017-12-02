# coding=utf-8

import time
import BaseHTTPServer
import json
import os


class DialogFlowHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(s):
        s.send_response(200)
        s.end_headers()
        s.wfile.write('Test string')

    def do_POST(s):
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

if __name__ == '__main__':
    port = int(os.environ['PORT'])
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class(('', port), DialogFlowHandler)
    print(time.asctime(), 'Server started on port %s' % port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
