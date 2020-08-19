from .tcpserver import TCPServer
import os
import mimetypes

WEB_DIR = 'html/'


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
        self.parse_request_line(data_lines[0])

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

    def __init__(self, host='127.0.0.1', port=5000):
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
        except AttributeError:
            print("Not Implemented")
        status_line, headers, body = handler(request)
        connection_socket.sendall(status_line)
        connection_socket.sendall(headers)
        if body: connection_socket.sendall(body)

    def handle_GET(self, request):
        filename = request.URI.strip('/')
        filepath = os.path.abspath(WEB_DIR+filename)

        if os.path.exists(filepath):
            status_line = self.response_status_line(200)
            content_type = mimetypes.guess_type(filepath)[0] or 'text/html'

            with open(filepath, 'rb') as f:
                file_data = f.read()
                if content_type == "text/html":
                    body = file_data.decode().encode(
                        'utf-8')  # decode from binary, encode to utf-8
                else:
                    body = file_data

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
