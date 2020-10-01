import socket
import errno

from threading import Thread

REQUEST_QUEUE_SIZE = 25


class TCPServer():
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.thread_pool = []

    def start_server(self):
        """ Starts a TCP Server to handle http requests"""

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(REQUEST_QUEUE_SIZE)

        print("Started server at ", self.server_socket.getsockname())

        try:
            while True:
                connection_socket, addr = self.server_socket.accept()

                Thread(target=self.handle_clients, args=(connection_socket,)).start()
        except KeyboardInterrupt:
            print(" Exiting...")
        
    def handle_clients(self, connection_socket):
        try:
            data = connection_socket.recv(2048)
            self.handle_request(data, connection_socket)
        except (BrokenPipeError, ConnectionResetError):
            print("ERROR: Client connection lost")
        finally:
            connection_socket.close()


    def handle_request(self, data, connection_socket):
        """Incoming Ruquest handler. For generating response
        Override this in the HTTPServer subclass"""

        return "Empty Response"

# TODO: https://github.com/python/cpython/blob/bd0a08ea90e4c7a2ebf29697937e9786d4d8e5ee/Lib/socketserver.py#L631