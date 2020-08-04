import socket


REQUEST_QUEUE_SIZE = 1

class TCPServer():
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port

    def start_server(self):
        """ Starts a TCP Server to handle http requests"""

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(REQUEST_QUEUE_SIZE)

        print("Started server at ", self.server_socket.getsockname())

        while True:
            conn, addr = self.server_socket.accept()
            data =  conn.recv(1024)

            response = self.handle_request(data)
            conn.sendall(response.encode())
            conn.close()

    def handle_request(self, data):
        """Incoming Ruquest handler. For generating response
        Override this in the HTTPServer subclass"""

        return "Empty Response"