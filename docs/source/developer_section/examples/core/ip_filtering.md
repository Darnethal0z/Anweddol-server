# Implement IP filtering

----

Here is a server stub that involves an IP filtering feature :

```{note}
For performance reasons, it is recommended to implement an IP filtering feature with the `on_connection_accepted` event since it is faster than a whole initialized client instance.
```

```
from anwdlserver.core.server import ServerInterface

# Replace it with your own path
CONTAINER_ISO_PATH = "/path/of/the/ISO/file.iso"

# The array containing denied IPs
DENIED_IP_ARRAY = ["1.1.1.1", "3.3.3.3", "5.5.5.5"]

# Create a new ServerInterface instance
server = ServerInterface(CONTAINER_ISO_PATH)

# Print the message when the server is ready
@server.on_server_started
def notify_started(context, data):
	print("Server is started")

# IP filtering implementation
@server.on_connection_accepted
def handle_connection(context, data):
	client_socket = data.get("client_socket")
	client_ip = client_socket.getpeername()[0]

	if client_ip in DENIED_IP_ARRAY:
		# The server process will notice that the client socket is closed
		# and will pass the session after the end of this routine.
		client_socket.close()

		print(f"Connection closed for denied IP : {client_ip}")

# Start the server
server.startServer()
```