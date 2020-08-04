from tcpserver import TCPServer
import os
import mimetypes


class HTTPRequest():
    def __init__(self, data):
        self.method = None
        self.URI = None
        self.http_version = 'HTTP/1.1'
        self.headers = {}

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
    status_codes = {
        200: 'OK',
        404: 'Not Found',
        501: 'Not Implemented'
    }

    headers = {
        'Server': 'Tiny Server',
        'ContentType': 'text/html'
    }

    def response_status_line(self, status_code):
        status_text = self.status_codes[status_code]
        return "HTTP/1.1 %s %s\r\n" % (status_code, status_text)

    def response_headers(self, extra_headers=None):
        headers_copy = self.headers.copy()
        if extra_headers:
            headers_copy.update(extra_headers)

        headers = ""
        for h in headers_copy:
            headers += "%s: %s\r\n" % (h, self.headers[h])
        return headers

    def handle_request(self, data):
        request =  HTTPRequest(data)
        try:
            handler = getattr(self, 'handle_%s' % request.method)
        except AttributeError:
            print("Not Implemented")
        response = handler(request)

        return response

    def handle_GET(self, request):
        filename = request.URI.strip('/')

        if os.path.exists(filename):
            response_status_line = self.response_status_line(200)
            content_type = mimetypes.guess_type(filename)[0] or 'text/html'

            extra_headers = {'Content-Type': content_type}
            response_headers = self.response_headers(extra_headers)

            with open(filename) as f:
                response_body = f.read()
        else:
            response_line = self.response_line(404)
            response_headers = self.response_headers()
            response_body = "<h1>404 Not Found</h1>"

        response = "%s%s\r\n%s" % (
            response_status_line, 
            response_headers, 
            response_body
        )
        return response

    def handle_OPTIONS(self, request):
        resonse_status_line = self.response_status_line(200)
        allow_header = {'Allow':'OPTIONS, GET'}
        headers = self.response_headers(allow_header)

        response = "%s%s\r\n" % (
            resonse_status_line,
            headers
        )

        return response

