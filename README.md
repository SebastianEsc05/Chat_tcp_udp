# Proyecto de Chat TCP/UDP

Este es un proyecto final para la clase de Redes. Es un chat cliente-servidor que funciona con TCP y UDP.

## Características

- Funciona con TCP y UDP al mismo tiempo
- Soporta hasta 5 clientes
- Mensajes públicos y privados
- Interfaz con colores
- Selección de puerto
- Muestra tu IP local

## Requisitos

- Python 3.6 o superior
- No necesita instalar nada extra

## Cómo usarlo

### 1. Iniciar el Servidor

Abre una terminal y ejecuta:

```bash
# Para Mac/Linux
python3 main_server.py --protocol both

# Para Windows
python main_server.py --protocol both
```

El servidor te pedirá el puerto (por defecto 8888).

### 2. Conectar Clientes

Abre otra terminal para cada cliente:

```bash
# Para Mac/Linux
python3 main_client.py TuNombre --protocol tcp

# Para Windows
python main_client.py TuNombre --protocol tcp
```

Si quieres conectarte desde otra computadora en la misma red:

```bash
python3 main_client.py TuNombre --protocol tcp --host IP_DEL_SERVIDOR
```

(La IP del servidor aparece cuando lo inicias)

## Comandos del Chat

- Escribe cualquier cosa para enviar un mensaje a todos.
- Usa `/msg usuario mensaje` para enviar un mensaje privado.
- Usa `/help` para ver la ayuda.
- Usa `/quit` para salir.

## Estructura de archivos

- `main_server.py`: El código del servidor.
- `main_client.py`: El código del cliente.
- `common/`: Archivos comunes (protocolo y transporte).
- `server/`: Archivos del servidor (gestor de clientes).

## Notas

- El proyecto usa `socket` y `threading` de Python.
- Los mensajes se envían en formato JSON.
- Se puede usar en Windows, Mac y Linux.
