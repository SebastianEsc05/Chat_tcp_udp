import json

class Protocol:
    # Tipos de mensajes
    LOGIN = "LOGIN"
    PUBLIC_MSG = "PUBLIC_MSG"
    PRIVATE_MSG = "PRIVATE_MSG"
    ERROR = "ERROR"
    ACK = "ACK"
    #Cmpaqueta un mensaje en formato JSON y lo convierte a byes para enviarlo
    #Parametros:
    #   msg_type: Tipo de mensaje
    #   sender: nombre del usuario que envia el mensaje
    #   payload: el contenido del texto
    #   target: el destinatario del mensaje en caso de que sea paea usuarios privados
    #Retorna: 
    #   Mensaje convertido en bytes codificado en utf-8
    @staticmethod
    def create_message(msg_type, sender, payload="", target=None, sender_protocol=""):
        msg = {
            "type": msg_type,
            "sender": sender,
            "payload": payload,
            "target": target,
            "sender_protocol": sender_protocol
        }
        return json.dumps(msg).encode('utf-8')
    #Convierte los bytes recibidos de vuelta a un diccionario de python
    #Parametros:
    #   data: los bytes recibidos
    #Returna: 
    #   Diccionario con los datos del mensaje, o None si paso algun error al decodificarlo

    @staticmethod
    def parse_message(data):
        try:
            return json.loads(data.decode('utf-8'))
        except:
            return None
