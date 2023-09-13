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

# Create a new ServerInterface instance
server = ServerInterface(CONTAINER_ISO_PATH)

# Sends 'PONG' in response when a 'PING' request is received
def handle_ping_request(client_instance):
	print("Received PING request")

	client_instance.sendResponse(True, RESPONSE_MSG_OK, data={"answer": "PONG"})
	client_instance.closeConnection()

# Print the message when the server is ready
@server.on_server_started
def notify_started(context, data):
	print("Server is started")
	
# Add the new 'PING' request handler
server.setRequestHandler("PING", handle_ping_request)

# Start the server
server.startServer()
```