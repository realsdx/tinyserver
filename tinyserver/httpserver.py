from .tcpserver import TCPServer
import os
import mimetypes
import threading
import gzip

WEB_DIR = 'example_html/'
mutex_lock = threading.Lock()

class HTTPRequest():
    def __init__(self, data):
        self.method = None
        self.URI = None
        self.http_version = 'HTTP/1.1'
        self.request_headers = {}
        self.use_gzip = False

        data = data.decode()
        self.parse(data)

    def parse(self, data):
        data_lines = data.split('\r\n')
        if data_lines[0]: self.parse_request_line(data_lines[0])
        if data_lines[1:] != []: self.parse_headers(data_lines[1:])

    def parse_request_line(self, req_line):
        request_info = req_line.split(' ')
        self.method = request_info[0]
        self.URI = request_info[1]
        self.http_version = request_info[2]

    def parse_headers(self, raw_headers):
        for rh in raw_headers:
            header = rh.split(":")
            if header[0] != '': self.request_headers[header[0]] = header[1]
        
        # Check for encoding header
        encodings = self.request_headers.get('Accept-Encoding', None)
        if encodings:
            if "gzip" in encodings: self.use_gzip = True


class HTTPServer(TCPServer):
    def __init__(self, host='127.0.0.1', port=5000, web_dir=None):
        self.headers = {'Server': 'Tiny Server/1.0.0', 'Connection': 'close'}
        self.status_codes = {200: 'OK', 404: 'Not Found', 501: 'Not Implemented'}
        self.web_dir = web_dir if (web_dir != None) else WEB_DIR
        self.file_cache = {}
        super().__init__(host, port)

    def add_to_cache(self, body, filepath, file_size):
        if file_size <= 512:
            with mutex_lock:
                self.file_cache[filepath] = body
                print("DEBUG: File Cached ", filepath)

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
            
        except AttributeError as e:
            print("ERROR: [%s] Method Not Implemented" %(request.method))


    def handle_GET(self, request):
        filename = request.URI.strip('/')
        if not filename:
            filename = 'index.html'
        filepath = os.path.abspath(self.web_dir+filename)

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
                self.add_to_cache(body, filepath, file_size)

            extra_headers = {
                'Content-Type': content_type
            }
            # Compress data if supported
            if request.use_gzip:
                print("DEBUG: Sending gzipped body")
                body = gzip.compress(body)
                extra_headers['Content-Encoding'] ='gzip'

            # Setup response headers
            extra_headers['Content-Length']: len(body)
            headers = self.response_headers(extra_headers)
        else:
            status_line = self.response_status_line(404)
            headers = self.response_headers()
            body = "<h1>404 Not Found</h1>".encode()

        return status_line.encode(), headers.encode(), body

    def handle_OPTIONS(self, request):
        status_line = self.response_status_line(204)
        allow_header = {'Allow': 'OPTIONS, GET'}
        headers = self.response_headers(allow_header)

        return status_line.encode(), headers.encode(), None
