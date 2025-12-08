import threading

class ClientManager:
    # Constructor: Prepara el gestor de clientes
    # Parametros:
    #   max_clients: Cuantos clientes permitimos como maximo (por defecto 5)
    def __init__(self, max_clients=5):
        self.clients = {} 
        self.max_clients = max_clients
        self.lock = threading.Lock()

    # Agrega un nuevo cliente al chat
    # Parametros:
    #   username: El nombre del usuario
    #   addr: La direccion IP y puerto del cliente
    #   transport: La conexion para enviarle mensajes
    # Retorna:
    #   True si se agrego bien, False si esta lleno o ya existe el nombre
    def add_client(self, username, addr, transport):
        with self.lock:
            if len(self.clients) >= self.max_clients:
                return False
            if username in self.clients:
                return False
            self.clients[username] = (addr, transport)
            return True

    # Elimina a un cliente del chat
    # Parametros:
    #   username: El nombre del usuario a borrar
    # Retorna: Nada
    def remove_client(self, username):
        with self.lock:
            if username in self.clients:
                del self.clients[username]

    # Busca la informacion de un cliente
    # Parametros:
    #   username: El nombre del usuario que buscamos
    # Retorna:
    #   Una tupla (addr, transport) si existe, o None si no
    def get_client(self, username):
        with self.lock:
            return self.clients.get(username)

    # Obtiene la lista de todos los usuarios conectados
    # Retorna:
    #   Una lista con los nombres de los usuarios (strings)
    def get_all_clients(self):
        with self.lock:
            return list(self.clients.keys())

    # Verifica si un usuario ya esta en el chat
    # Parametros:
    #   username: El nombre a verificar
    # Retorna:
    #   True si el usuario existe, False si no
    def is_member(self, username):
        with self.lock:
            return username in self.clients