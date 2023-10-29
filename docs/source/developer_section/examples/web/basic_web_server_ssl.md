# Basic web server with SSL support

----

Here is a simple web server stub that can be used as a functional web server, with SSL enabled:

```{note}
The HTTP server will listen on port `4443`.

You can make a request on `https://localhost:4443/stat` with `curl` or `wget` to send a SSL-wrapped STAT request to the server.
```

```{tip}
If you need a private key and a certificate, you can generate them with `openssl` :

`$ openssl req -newkey rsa:4096 -nodes -keyout private_key.pem -x509 -days 365 -out certificate.pem`

This command generates a 4096-bit private key and a self-signed certificate. Answer the questions and set the `ssl_pem_private_key_file_path` parameter with the `private_key.pem` file path, and the `ssl_pem_certificate_file_path` parameter with the `certificate.pem` file path.

([source](https://www.digitalocean.com/community/tutorials/openssl-essentials-working-with-ssl-certificates-private-keys-and-csrs))
```

```
from anwdlserver.web.server import WebServerInterface

# Replace it with your own paths and values
CONTAINER_ISO_PATH = "/path/of/the/ISO/file.iso"
PRIVATE_KEY_FILE_PATH = "/path/of/the/pem/key/file"
CERTIFICATE_FILE_PATH = "/path/of/the/pem/certificate/file"
LISTEN_PORT = 4443

web_server = WebServerInterface(
	CONTAINER_ISO_PATH, 
	listen_port=LISTEN_PORT,
	enable_ssl=True,
	ssl_pem_private_key_file_path=PRIVATE_KEY_FILE_PATH,
	ssl_pem_certificate_file_path=CERTIFICATE_FILE_PATH,
)

# Print the message when the server is ready
@web_server.on_server_started
def notify_started(context, data):
	print(f"Web server is started, listening on port {LISTEN_PORT}")

# Start the server
web_server.startServer()
```