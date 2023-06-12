# Set custom container capacity

----

```
from anwdlserver.core.server import ServerInterface

# Replace it with your own path
CONTAINER_ISO_PATH = "/path/of/the/ISO/file.iso"

# Create a new ServerInterface instance
server = ServerInterface(container_iso_path=CONTAINER_ISO_PATH)

# Print the message when the server is ready
@server.on_started
def notify_started(**kwargs):
	print("Server is started")

# Print a message when a request is received
@server_interface.on_request
def notify_request(**kwargs):
	request_verb = kwargs["client_instance"].getStoredRequest()
	
	print("Received {} request".format(request_verb["verb"]))

# Set created containers capacity with 2048 Mb of memory and 2 VCPUs
@server.on_container_created
def handle_container_creation(**kwargs):
	container_instance = kwargs.get("container_instance")

	print(f"New container created : {container_instance.getUUID()}")

	container_instance.setMemory(2048)
	container_instance.setVCPUs(2)

# Start the server
server.startServer()
```