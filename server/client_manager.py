import threading

class ClientManager:
    def __init__(self, max_clients=5):
        self.clients = {}  # username -> (addr, transport)
        self.max_clients = max_clients
        self.lock = threading.Lock()

    def add_client(self, username, addr, transport):
        with self.lock:
            if len(self.clients) >= self.max_clients:
                return False
            if username in self.clients:
                return False
            self.clients[username] = (addr, transport)
            return True

    def remove_client(self, username):
        with self.lock:
            if username in self.clients:
                del self.clients[username]

    def get_client(self, username):
        with self.lock:
            return self.clients.get(username)

    def get_all_clients(self):
        with self.lock:
            return list(self.clients.keys())

    def is_member(self, username):
        with self.lock:
            return username in self.clients
