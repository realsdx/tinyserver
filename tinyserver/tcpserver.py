import socket
import selectors


REQUEST_QUEUE_SIZE = 50


class TCPServer():
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.selector = selectors.DefaultSelector()
    
    def accept_client(self, server_socket, mask):
        conn, addr = server_socket.accept()
        conn.setblocking(False)
        self.selector.register(conn, selectors.EVENT_READ, self.read_client)

    def read_client(self, conn, mask):
        data = conn.recv(1024)
        if data:
            try:
                self.handle_request(data, conn)
            except (BrokenPipeError, ConnectionResetError):
                print("Error: Clinet connection lost")
        
        self.selector.unregister(conn)
        conn.close()

    def start_server(self):
        """ Starts a TCP Server to handle http requests"""

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(REQUEST_QUEUE_SIZE)
        self.server_socket.setblocking(False)

        self.selector.register(self.server_socket, selectors.EVENT_READ, self.accept_client)

        print("Started server at ", self.server_socket.getsockname())

        try:
            while True:
                events =  self.selector.select()
                for key , mask in events:
                    callback = key.data
                    callback(key.fileobj, mask)

        except KeyboardInterrupt:
            print(" Exiting...")

    def handle_request(self, data, connection_socket):
        """Incoming Ruquest handler. For generating response
        Override this in the HTTPServer subclass"""

        return "Empty Response"
