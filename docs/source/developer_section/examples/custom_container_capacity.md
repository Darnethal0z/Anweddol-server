# Set custom container capacity

----

```
from anwdlserver.core.server import ServerInterface

# Replace it with your own path
CONTAINER_ISO_PATH = "/path/of/the/ISO/file.iso"
NEW_CONTAINER_MEMORY = 2048
NEW_CONTAINER_VCPUS_AMOUNT = 4

# Create a new ServerInterface instance
server = ServerInterface(CONTAINER_ISO_PATH)

# Print the message when the server is ready
@server.on_server_started
def notify_started(context, data):
	print("Server is started")

# Set created containers capacity with 2048 Mb of memory and 2 VCPUs
@server.on_container_created
def handle_container_creation(context, data):
	container_instance = data.get("container_instance")

	print(f"New container created : {container_instance.getUUID()}")

	container_instance.setMemory(NEW_CONTAINER_MEMORY)
	container_instance.setVCPUs(NEW_CONTAINER_VCPUS_AMOUNT)

# Start the server
server.startServer()
```