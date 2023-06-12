# Basic server

----

Here is a simple server stub that can be used as a functional server :

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

# Start the server
server.startServer()
```