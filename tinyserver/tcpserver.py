import socket

from threading import Thread

REQUEST_QUEUE_SIZE = 5


class TCPServer():
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.thread_pool = []

    def start_server(self):
        """ Starts a TCP Server to handle http requests"""

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(REQUEST_QUEUE_SIZE)

        print("Started server at ", self.server_socket.getsockname())

        try:
            while True:
                connection_socket, addr = self.server_socket.accept()

                th = Thread(target=self.handle_clients, args=(connection_socket,))
                th.start()
                self.thread_pool.append(th)
        except KeyboardInterrupt:
            print(" Exiting...")
        finally:
            print("DEBUG: Thread Count: ", len(self.thread_pool))
            for _th in self.thread_pool:
                _th.join()
        
    def handle_clients(self, connection_socket):
        data = connection_socket.recv(2048)
        self.handle_request(data, connection_socket)
        connection_socket.close()

    def handle_request(self, data, connection_socket):
        """Incoming Ruquest handler. For generating response
        Override this in the HTTPServer subclass"""

        return "Empty Response"