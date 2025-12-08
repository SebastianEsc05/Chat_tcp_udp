import sys
import threading
import argparse
import socket
from datetime import datetime
from common.protocol import Protocol
from common.transport import TCPTransport, UDPTransport
from server.client_manager import ClientManager

# Colores ANSI
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GRAY = '\033[90m'
    RED = '\033[91m'

class ChatServer:
    # Obtiene la ip local de la computadora para que otros se conecten
    # Retorna:
    #   La ip local 
    @staticmethod
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"
    
    # Constructor: Configura el servidor
    # Parametros:
    #   host: La IP donde escuchar (0.0.0.0 significa todas)
    #   port: El puerto donde escuchar (ej: 8888)
    #   protocol_type: 'tcp', 'udp' o 'both'
    def __init__(self, host='0.0.0.0', port=8888, protocol_type='tcp'):
        self.host = host
        self.port = port
        self.protocol_type = protocol_type
        self.client_manager = ClientManager()
        self.running = True
        
        self.tcp_transport = None
        self.udp_transport = None

        if self.protocol_type in ['tcp', 'both']:
            # Inicializamos el socket TCP por separado
            self.tcp_transport = TCPTransport()
            self.tcp_transport.bind(self.host, self.port)
            
        if self.protocol_type in ['udp', 'both']:
            # Inicializamos el socket UDP por separado
            self.udp_transport = UDPTransport(self.host, self.port)

        # Mostrar información de inicio
        local_ip = self.get_local_ip()
        print(f"{Colors.GREEN}{Colors.BOLD}Servidor iniciado en {self.host}:{self.port} ({self.protocol_type.upper()}){Colors.RESET}")
        
        if self.host == '0.0.0.0':
            print(f"{Colors.CYAN}Tu IP local: {local_ip}:{self.port}{Colors.RESET}")
            print(f"{Colors.GRAY}Los clientes pueden conectarse usando:{Colors.RESET}")
            print(f"{Colors.GRAY}  - Local: python3 main_client.py TuNombre --protocol tcp{Colors.RESET}")
            print(f"{Colors.GRAY}  - Remoto: python3 main_client.py TuNombre --protocol tcp --host {local_ip}{Colors.RESET}")

    # Inicia el servidor y los hilos para aceptar conexiones
    # No recibe parametros ni retorna nada
    def start(self):
        threads = []
        
        # LOGICA DE SEPARACION:
        # Usamos hilos (threads) diferentes para TCP y UDP
        # Asi pueden funcionar al mismo tiempo sin bloquearse
        
        if self.protocol_type in ['tcp', 'both']:
            # El primer Hilo se encarga nomas de escuchar conexiones TCP
            t = threading.Thread(target=self.accept_loop)
            t.start()
            threads.append(t)
            
        if self.protocol_type in ['udp', 'both']:
           # El segundo Hilo se encarga nomas de escuchar conexiones UDP
            t = threading.Thread(target=self.udp_loop)
            t.start()
            threads.append(t)
            
        try:
            for t in threads:
                t.join()
        except KeyboardInterrupt:
            self.running = False

    # Bucle infinito para aceptar clientes TCP nuevos
    # Se ejecuta en un hilo separado
    def accept_loop(self):
        while self.running:
            try:
                assert self.tcp_transport is not None

                client_transport = self.tcp_transport.accept()

                addr = client_transport.get_address()
                assert addr is not None

                print(f"{Colors.CYAN}Conexion desde {addr[0]}:{addr[1]}{Colors.RESET}")

                threading.Thread(
                    target=self.handle_tcp_client,
                    args=(client_transport,)
                ).start()

            except Exception as e:
                if self.running:
                    print(f"{Colors.RED}Error de conexion: {e}{Colors.RESET}")

    # Maneja la comunicacion con un cliente TCP especifico
    # Parametros:
    #   transport: El objeto de transporte para enviar/recibir datos
    def handle_tcp_client(self, transport):
        addr = transport.get_address()
        username = None
        try:
            while True:
                data, _ = transport.recv()
                if not data:
                    break
                
                msg = Protocol.parse_message(data)
                if not msg:
                    continue

                response = self.process_message(msg, addr, transport)
                if response:
                    transport.send(response)
                
                if msg['type'] == Protocol.LOGIN and not username:
                     if self.client_manager.is_member(msg['sender']):
                         username = msg['sender']
                     if self.client_manager.is_member(msg['sender']):
                         username = msg['sender']

        except Exception as e:
            # Manejo de errores durante la comunicación con el cliente
            print(f"{Colors.RED}Error con cliente {username or addr}: {e}{Colors.RESET}")
        finally:
            # Lógica de limpieza cuando el cliente se desconecta o hay un error
            if username:
                self.client_manager.remove_client(username)
                print(f"{Colors.YELLOW}{username} desconectado{Colors.RESET}")
                self.broadcast_system(f"{username} salio del chat")
            transport.close()

    # Bucle infinito para recibir mensajes UDP
    # Se ejecuta en un hilo separado
    def udp_loop(self):
        while self.running:
            try:
                assert self.udp_transport is not None
                data, addr = self.udp_transport.recv()
                if not data:
                    continue            
                msg = Protocol.parse_message(data)
                if not msg:
                    continue
                
                response = self.process_message(msg, addr, self.udp_transport)
                if response:
                    assert self.udp_transport is not None
                    self.udp_transport.send(response, addr)

            except Exception as e:
                if self.running:
                    print(f"{Colors.RED}Error UDP: {e}{Colors.RESET}")

    # Procesa un mensaje recibido (Login, Publico, Privado)
    # Parametros:
    #   msg: El diccionario del mensaje
    #   addr: La direccion del remitente
    #   transport: El medio para responder
    # Retorna:
    #   Una respuesta si es necesario, o None
    def process_message(self, msg, addr, transport):
        msg_type = msg.get('type')
        sender = msg.get('sender')
        sender_protocol = "TCP" if isinstance(transport,TCPTransport) else "UDP"

        if msg_type == Protocol.LOGIN:
            if self.client_manager.add_client(sender, addr, transport):
                print(f"{Colors.GREEN}{sender} se conecto desde {addr[0]}:{addr[1]}{Colors.RESET}")
                self.broadcast_system(f"{sender} entro al chat")
                return Protocol.create_message(Protocol.ACK, "SERVER", "Bienvenido al servidor")
            else:
                print(f"{Colors.RED}Login fallido: {sender}{Colors.RESET}")
                return Protocol.create_message(Protocol.ERROR, "SERVER", "Usuario ocupado o servidor lleno")

        if not self.client_manager.is_member(sender):
            return Protocol.create_message(Protocol.ERROR, "SERVER", "No has iniciado sesion")

        if msg_type == Protocol.PUBLIC_MSG:
            # Mostrar mensaje con fecha y hora
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{Colors.GRAY}[{timestamp}]{Colors.RESET} {Colors.YELLOW}[{sender_protocol}]{Colors.RESET} {Colors.BLUE}<{sender}>{Colors.RESET} {msg.get('payload')}")
            self.broadcast(msg, sender,sender_protocol)
            return None

        elif msg_type == Protocol.PRIVATE_MSG:
            target = msg.get('target')
            # Mostrar mensaje privado con fecha y hora
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"{Colors.GRAY}[{timestamp}]{Colors.RESET} {Colors.YELLOW}[{sender_protocol}]{Colors.RESET} {Colors.CYAN}{sender} -> {target}:{Colors.RESET} {msg.get('payload')}")
            self.send_private(msg, target, sender,sender_protocol)
            return None

        return None

    # Envia un mensaje a TODOS los usuarios conectados
    # Parametros:
    #   msg_dict: El contenido del mensaje
    #   sender: Quien lo envia
    def broadcast(self, msg_dict, sender, sender_protocol):
        data = Protocol.create_message(
            msg_dict['type'], 
            sender, 
            msg_dict['payload'], 
            target=None,            
            sender_protocol=sender_protocol 
        )
        for user in self.client_manager.get_all_clients():
            self._send_to_user(user, data)


    # Envia un mensaje del sistema a todos (ej: "Usuario entro")
    # Parametros:
    #   text: El texto a enviar
    def broadcast_system(self, text):
        data = Protocol.create_message(Protocol.PUBLIC_MSG, "SERVER", text)
        for user in self.client_manager.get_all_clients():
            self._send_to_user(user, data)

    # Envia un mensaje privado a un usuario especifico
    # Parametros:
    #   msg_dict: El contenido del mensaje
    #   target: El nombre del usuario destino
    #   sender: Quien lo envia
    def send_private(self, msg_dict, target, sender, sender_proto):
        data = Protocol.create_message(Protocol.PRIVATE_MSG, sender, msg_dict['payload'], target=target, sender_protocol=sender_proto)
        if self.client_manager.is_member(target):
            self._send_to_user(target, data)
        else:
            error = Protocol.create_message(Protocol.ERROR, "SERVER", f"Usuario {target} no encontrado")
            self._send_to_user(sender, error)

    # Funcion auxiliar para enviar datos a un usuario por su nombre
    # Parametros:
    #   username: Nombre del usuario destino
    #   data: Los datos a enviar (ya serializados)
    def _send_to_user(self, username, data):
        client = self.client_manager.get_client(username)
        if client:
            addr, transport = client

            try:
                if isinstance(transport, TCPTransport):
                    transport.send(data) 
                else:
                    transport.send(data, addr) 
            except:
                pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Servidor de Chat TCP/UDP')
    parser.add_argument('--protocol', choices=['tcp', 'udp', 'both'], default='both', help='Protocolo a usar')
    parser.add_argument('--port', type=int, default=None, help='Puerto de escucha')
    parser.add_argument('--host', default='0.0.0.0', help='Direccion de escucha')
    args = parser.parse_args()

    # Solicitar puerto si no se proporcionó
    port = args.port
    if port is None:
        while True:
            try:
                port_input = input("Ingresa el puerto a usar (por defecto 8888): ").strip()
                port = int(port_input) if port_input else 8888
                if 1024 <= port <= 65535:
                    break
                else:
                    print("Error: El puerto debe estar entre 1024 y 65535")
            except ValueError:
                print("Error: Ingresa un número válido")
            except KeyboardInterrupt:
                print("\nCancelado")
                sys.exit(0)

    try:
        server = ChatServer(host=args.host, port=port, protocol_type=args.protocol)
        server.start()
    except KeyboardInterrupt:
        print("\nServidor detenido")
    except Exception as e:
        print(f"Error: {e}")