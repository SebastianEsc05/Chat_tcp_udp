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
    #Constructor que crea el socket TCP
    #Parametros:
    #   sock: socket existente (se usa cuando el servidor acepta a un cliente)
    #   addr: la direccion asociada (se usa cuando el servifor acepta un cliente)
    def __init__(self, sock=None, addr=None):
        if sock:
            self.sock = sock
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.addr = addr

    #Conecta el socket a un servidor remoto
    #Parametros:
    #   host: La ip del servdor
    #   port: el pierto del servidor
    def connect(self, host, port):
        self.sock.connect((host, port))

    #Asigna el socket a una direccion local para escuchar conexiones
    #Parametros:
    #   host: ip local
    #   port: puerto local
    def bind(self, host, port):
        self.sock.bind((host, port))
        self.sock.listen(5)

    #Espera y acepta una nueva conexion entrante
    #Retorna:
    # Un nuevo objeto TCPTransport exclusivo para ese cliente
    def accept(self):
        client_sock, addr = self.sock.accept()
        return TCPTransport(client_sock, addr)

    #Envia datos agregando un encabezado de 4 bytes con la longitud total, necesario para que en TCP se sepa donde se termina el msg
    #Parametros
    #   data: bytes a enviar
    #   adrr: ignorado en tcp ya que la conexion ya esta establecida, pero requerido por la interfaz
    def send(self, data, addr=None):
        length = len(data)
        self.sock.sendall(struct.pack('!I', length) + data)


    #Recibe un mensaje completo leyendo primero la longitud y luego su contenido
    #Retorna:
    #   tupla de (datos_bytes, direccion_remota)
    def recv(self):
        # Leer longitud del mensaje
        header = self._recv_all(4)
        if not header:
            return None, None
        length = struct.unpack('!I', header)[0]
        body = self._recv_all(length)
        return body, self.addr
    #Metodo interno auxiliar para asegurar que leemos exactamente "n" bytes 
    #parametros:
    #   n: cantidad de bytes que necesitamos leer
    #Retorna:
    #   los bytes leidos o "none" si la conección se cerró
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
    #Envia un paquete (datagrama) a un adireccion expecifica
    #Parametros: 
    #   data: los bytes que se enviarán
    #   addr: la tupla (ip, puerto) del destino, obligatorio en udp
    def send(self, data, addr):
        self.sock.sendto(data, addr)

    #recibe un paquete (datagrama) de hasta 4096 bytes
    #Retorna:
    #  tupla (datos_bytes, direccion_remitente)
    def recv(self):
        data, addr = self.sock.recvfrom(4096)
        return data, addr

    def close(self):
        self.sock.close()
    
    def get_address(self):
        return self.sock.getsockname()
