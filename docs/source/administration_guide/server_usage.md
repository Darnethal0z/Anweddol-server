# Server usage

----

```{warning}
You need to follows the [Installation](installation.md) section before reading this section.
```

## Start the server

If you are using the `virbr0` interface as `nat_interface_name`, the first thing you need is to start the libvirtd daemon (if not already started) : 

```
$ sudo systemctl start libvirtd.service
```

```{tip}
You can check if the Anweddol server environment is correctly set up with : 

`$ sudo anwdlserver start -c`

If some errors are displayed, check the [Troubleshooting](troubleshooting.md) section for common errors resolution.
```

### Classic server

Start the Anweddol server via systemd : 

```
$ sudo systemctl start anweddol-server.service
```

You can also start the anweddol server directly from the terminal : 

```
$ sudo anwdlserver start
```

You can add the `-d` option to enable direct execution (the server will run synchronously in the terminal, as the actual user).

```{note}
It is preferable to use systemd for server lifetime control, mixed usage between CLI and systemd can cause hazardous behaviour.
```

### Web server alternative

There is no systemd service for Anweddol server web alternative.

Instead, you can start it with the terminal just by adding the `--web` flag to the command :

```
$ sudo anwdlserver start --web
```

```{tip}
If you need a private key and a certificate to use, you can generate them with `openssl` :

`$ openssl req -newkey rsa:4096 -nodes -keyout private_key.pem -x509 -days 365 -out certificate.pem`

This command generates a 4096-bit private key and a self-signed certificate. Answer the questions and set the `ssl_pem_private_key_file_path` configuration file key with the `private_key.pem` file path, and the `ssl_pem_certificate_file_path` configuration file key with the `certificate.pem` file path.

([source](https://www.digitalocean.com/community/tutorials/openssl-essentials-working-with-ssl-certificates-private-keys-and-csrs))
```

```{warning}
If the certificate used is self-signed, there is a huge probability that most HTTP clients reject it due to its insecure nature (be it web browsers or other tools like `curl` or `wget`).

If the REST API is enabled or used on an Anweddol server, administrators shall make sure that :

	- Potential clients are aware of this ;
	- The certificate is publicly accessible ;
	- The certificate integrity is verifiable (checksums, GPG, ...) ;

Clients can always ignore the certificate authenticity check, but it's preferable to provide something to properly interact with the server.
```

## Stop the server

Stop the server via the systemd daemon : 

```
$ sudo systemctl stop anweddol-server.service
```

Or via the CLI : 

```
$ sudo anwdlserver stop
```

```{note}
As mentionned in the previous section, it is preferable to use systemd for server lifetime control : mixed usage between CLI and systemd can cause hazardous behaviour.
```