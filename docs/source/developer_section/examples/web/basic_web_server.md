# Basic web server

----

Here is a simple web server stub that can be used as a functional web server :

```{note}
The HTTP server will listen on port `8080` by default.

You can make a request on `http://localhost:8080/stat` with `curl` or `wget` to send a STAT request to the server.
```

```
from anwdlserver.web.server import WebServerInterface

# Replace it with your own path
CONTAINER_ISO_PATH = "/path/of/the/ISO/file.iso"

web_server = WebServerInterface(CONTAINER_ISO_PATH)

# Print the message when the server is ready
@web_server.on_server_started
def notify_started(context, data):
	print("Web server is started, listening on port 8080")

# Start the server
web_server.startServer()
```