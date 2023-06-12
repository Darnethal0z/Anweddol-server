# Implement IP filtering

----

Here is a server stub that involves an IP filtering feature :

> For performance reasons, it is recommended to implement an IP filtering feature with the `on_connection` callback since it is faster than a whole client instance.

```
from anwdlserver.core.server import ServerInterface

# Replace it with your own path / values
CONTAINER_ISO_PATH = "/path/of/the/ISO/file.iso"
DENIED_IP_ARRAY = ["1.1.1.1", "3.3.3.3", "5.5.5.5"]

# Create a new ServerInterface instance
server = ServerInterface(container_iso_path=CONTAINER_ISO_PATH)

# Print the message when the server is ready
@server.on_started
def notify_started(**kwargs):
	print("Server is started")

# IP filtering implementation
@server.on_connection
def handle_connection(**kwargs):
	client_socket = kwargs.get("client_socket")
	client_ip = client_socket.getpeername()[0]

	if client_ip in DENIED_IP_ARRAY:
		# The server process will notice that the client socket is closed
		# and will pass the session after the end of this routine.
		print(f"Connection closed for denied IP : {client_ip}")

		client_socket.close()

# Start the server
server.startServer()
```