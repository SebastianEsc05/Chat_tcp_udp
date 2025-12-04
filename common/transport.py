import socket
import struct

class Transport:
    def send(self, data, addr=None):
        raise NotImplementedError

    def recv(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def get_address(self):
        raise NotImplementedError

class TCPTransport(Transport):
    def __init__(self, sock=None, addr=None):
        if sock:
            self.sock = sock
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.addr = addr

    def connect(self, host, port):
        self.sock.connect((host, port))

    def bind(self, host, port):
        self.sock.bind((host, port))
        self.sock.listen(5)

    def accept(self):
        client_sock, addr = self.sock.accept()
        return TCPTransport(client_sock, addr)

    def send(self, data, addr=None):
        length = len(data)
        self.sock.sendall(struct.pack('!I', length) + data)


    def recv(self):
        # Leer longitud del mensaje
        header = self._recv_all(4)
        if not header:
            return None, None
        length = struct.unpack('!I', header)[0]
        body = self._recv_all(length)
        return body, self.addr

    def _recv_all(self, n):
        data = b''
        while len(data) < n:
            packet = self.sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def close(self):
        self.sock.close()

    def get_address(self):
        return self.addr

class UDPTransport(Transport):
    def __init__(self, host=None, port=None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if host and port:
            self.sock.bind((host, port))
        self.addr = None

    def send(self, data, addr):
        self.sock.sendto(data, addr)

    def recv(self):
        data, addr = self.sock.recvfrom(4096)
        return data, addr

    def close(self):
        self.sock.close()
    
    def get_address(self):
        return self.sock.getsockname()
