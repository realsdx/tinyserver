from .tcpserver import TCPServer
import os
import mimetypes
import threading

WEB_DIR = 'example_html/'
mutex_lock = threading.Lock()

class HTTPRequest():
    def __init__(self, data):
        self.method = None
        self.URI = None
        self.http_version = 'HTTP/1.1'
        self.headers = {}

        data = data.decode()
        self.parse(data)

    def parse(self, data):
        data_lines = data.split('\r\n')
        if data_lines[0]: self.parse_request_line(data_lines[0])

    def parse_request_line(self, req_line):
        request_info = req_line.split(' ')
        self.method = request_info[0]
        self.URI = request_info[1]
        self.http_version = request_info[2]

    def parse_headers(self):
        pass


class HTTPServer(TCPServer):
    status_codes = {200: 'OK', 404: 'Not Found', 501: 'Not Implemented'}
    headers = {'Server': 'Tiny Server', 'Connection': 'close'}

    def __init__(self, host='127.0.0.1', port=5000, web_dir=None):
        self.web_dir = web_dir if (web_dir != None) else WEB_DIR
        super().__init__(host, port)

    def response_status_line(self, status_code):
        status_text = self.status_codes[status_code]
        return "HTTP/1.1 %s %s\r\n" % (status_code, status_text)

    def response_headers(self, extra_headers=None):
        headers_copy = self.headers.copy()
        if extra_headers:
            headers_copy.update(extra_headers)

        headers = ""
        for h in headers_copy:
            headers += "%s: %s\r\n" % (h, headers_copy[h])

        # append body separator '\r\n'
        headers += "\r\n"
        return headers

    def handle_request(self, data, connection_socket):
        request = HTTPRequest(data)
        try: 
            handler = getattr(self, 'handle_%s' % request.method)
            status_line, headers, body = handler(request)
            connection_socket.sendall(status_line)
            connection_socket.sendall(headers)
            if body: connection_socket.sendall(body)
            
        except AttributeError:
            print("ERROR: [%s] Method Not Implemented in %s" %(request.method, threading.current_thread().name))


    def handle_GET(self, request):
        filename = request.URI.strip('/')
        if not filename:
            filename = 'index.html'
        filepath = os.path.abspath(WEB_DIR+filename)

        if os.path.exists(filepath):
            status_line = self.response_status_line(200)
            content_type = mimetypes.guess_type(filepath)[0] or 'text/html'

            # Check in cache
            body = self.file_cache.get(filepath)

            if not body:
                with open(filepath, 'rb') as f:
                    file_data = f.read()
                    file_size = len(file_data)/1024                  

                if content_type == "text/html":
                    body = file_data.decode().encode(
                        'utf-8')  # decode from binary, encode to utf-8
                else:
                    body = file_data
                
                # Now put body content in the cache
                if file_size <= 512:
                    with mutex_lock:
                        self.file_cache[filepath] = body
                        print("DEBUG: Cached ", filepath)

            extra_headers = {
                'Content-Type': content_type,
                'Content-Length': len(body)
            }
            headers = self.response_headers(extra_headers)
        else:
            status_line = self.response_status_line(404)
            headers = self.response_headers()
            body = "<h1>404 Not Found</h1>".encode()

        return status_line.encode(), headers.encode(), body

    def handle_OPTIONS(self, request):
        status_line = self.response_status_line(200)
        allow_header = {'Allow': 'OPTIONS, GET'}
        headers = self.response_headers(allow_header)

        return status_line.encode(), headers.encode(), None
