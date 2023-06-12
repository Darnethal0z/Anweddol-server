# Handle a custom request verb

----

This stub shows how to implement a custom verb handling, here the server will respond "PONG" in parameters when a client sends a "PING" request : 

```
from anwdlserver.core.server import (
	ServerInterface, 
	RESPONSE_MSG_OK
)

# Replace it with your own path
CONTAINER_ISO_PATH = "/path/of/the/ISO/file.iso"

# Sends 'PONG' in response when a 'PING' request is received
def handle_ping_request(**kwargs):
	client_instance = kwargs.get("client_instance")

	print("Received PING request")

	client_instance.sendResponse(True, RESPONSE_MSG_OK, data={"answer": "PONG"})

	# Not mandatory, but programatically correct
	client_instance.closeConnection()

# Create a new ServerInterface instance
server = ServerInterface(container_iso_path=CONTAINER_ISO_PATH)

# Print the message when the server is ready
@server.on_started
def notify_started(**kwargs):
	print("Server is started")
	
# Add the new 'PING' request handler
server.setRequestHandler("PING", handle_ping_request)

# Start the server
server.startServer()
```