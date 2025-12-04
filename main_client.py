import sys
import threading
import argparse
from common.protocol import Protocol
from common.transport import TCPTransport, UDPTransport

# Colores ANSI
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'

class ChatClient:
    def __init__(self, username, host='127.0.0.1', port=8888, protocol_type='tcp'):
        self.username = username
        self.host = host
        self.port = port
        self.protocol_type = protocol_type
        self.running = True

        if self.protocol_type == 'tcp':
            self.transport = TCPTransport()
            try:
                self.transport.connect(self.host, self.port)
            except ConnectionRefusedError:
                print("No se pudo conectar al servidor")
                sys.exit(1)
            self.server_addr = None

        else:  
            self.transport = UDPTransport()
            self.transport.sock.bind(("0.0.0.0", 0))
            self.server_addr = (self.host, self.port)


    def start(self):
        print(f"{Colors.GREEN}{Colors.BOLD}Conectado a {self.host}:{self.port} ({self.protocol_type.upper()}){Colors.RESET}")
        
        # Enviar login
        login_msg = Protocol.create_message(Protocol.LOGIN, self.username)
        self.transport.send(login_msg, self.server_addr)

        # Thread para recibir
        threading.Thread(target=self.receive_loop, daemon=True).start()

        # Loop principal
        self.input_loop()

    def receive_loop(self):
        while self.running:
            try:
                data, _ = self.transport.recv()
                if not data:
                    if self.protocol_type == 'tcp':
                        print("\nDesconectado del servidor")
                        self.running = False
                        break
                    continue
                
                msg = Protocol.parse_message(data)
                if msg:
                    self.display_message(msg)
            except Exception as e:
                print(f"\nError: {e}")
                break

    def display_message(self, msg):
        msg_type = msg.get('type')
        sender = msg.get('sender')
        payload = msg.get('payload')
        
        if msg_type == Protocol.PUBLIC_MSG:
            if sender == "SERVER":
                print(f"\n{Colors.YELLOW}{Colors.BOLD}[Servidor]{Colors.RESET} {Colors.YELLOW}{payload}{Colors.RESET}")
            else:
                print(f"\n{Colors.CYAN}<{sender}>{Colors.RESET} {payload}")
                
        elif msg_type == Protocol.PRIVATE_MSG:
            print(f"\n{Colors.MAGENTA}{Colors.BOLD}[Privado de {sender}]{Colors.RESET} {Colors.MAGENTA}{payload}{Colors.RESET}")
            
        elif msg_type == Protocol.ERROR:
            print(f"\n{Colors.RED}{Colors.BOLD}Error:{Colors.RESET} {Colors.RED}{payload}{Colors.RESET}")
            
        elif msg_type == Protocol.ACK:
            print(f"\n{Colors.GREEN}{payload}{Colors.RESET}")

    def input_loop(self):
        print(f"{Colors.GRAY}Escribe un mensaje (o /help para ayuda):{Colors.RESET}")
        
        while self.running:
            try:
                text = input()
                
                if not text:
                    continue
                
                if text.lower() in ['/quit', '/exit']:
                    self.running = False
                    break
                
                if text.lower() in ['/help']:
                    print(f"\n{Colors.BOLD}Comandos:{Colors.RESET}")
                    print(f"  {Colors.CYAN}/msg <usuario> <mensaje>{Colors.RESET} - Mensaje privado")
                    print(f"  {Colors.CYAN}/quit{Colors.RESET} - Salir")
                    continue
                
                if text.startswith('/msg '):
                    parts = text.split(' ', 2)
                    if len(parts) < 3:
                        print(f"{Colors.RED}Uso: /msg <usuario> <mensaje>{Colors.RESET}")
                        continue
                    target = parts[1]
                    content = parts[2]
                    msg = Protocol.create_message(Protocol.PRIVATE_MSG, self.username, content, target=target)
                    print(f"{Colors.MAGENTA}Tu -> {target}:{Colors.RESET} {content}")
                else:
                    # Mensaje publico
                    msg = Protocol.create_message(Protocol.PUBLIC_MSG, self.username, text)
                
                self.transport.send(msg, self.server_addr)

            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                print(f"{Colors.RED}Error: {e}{Colors.RESET}")
                break
        
        self.transport.close()
        print(f"{Colors.GRAY}Adios{Colors.RESET}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Cliente de Chat TCP/UDP')
    parser.add_argument('username', help='Tu nombre de usuario')
    parser.add_argument('--host', default='127.0.0.1', help='Direccion del servidor')
    parser.add_argument('--port', type=int, default=8888, help='Puerto del servidor')
    parser.add_argument('--protocol', choices=['tcp', 'udp'], default='tcp', help='Protocolo a usar')
    args = parser.parse_args()

    client = ChatClient(args.username, args.host, args.port, args.protocol)
    client.start()
