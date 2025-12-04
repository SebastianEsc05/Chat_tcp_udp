import json

class Protocol:
    # Tipos de mensajes
    LOGIN = "LOGIN"
    PUBLIC_MSG = "PUBLIC_MSG"
    PRIVATE_MSG = "PRIVATE_MSG"
    ERROR = "ERROR"
    ACK = "ACK"

    @staticmethod
    def create_message(msg_type, sender, payload="", target=None):
        msg = {
            "type": msg_type,
            "sender": sender,
            "payload": payload,
            "target": target
        }
        return json.dumps(msg).encode('utf-8')

    @staticmethod
    def parse_message(data):
        try:
            return json.loads(data.decode('utf-8'))
        except:
            return None
