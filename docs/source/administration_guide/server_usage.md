# Server usage

----

> You need to follows the [Installation](installation.md) section before continuing this tutorial.

## Start the server

First, you need the libvirtd daemon running : 

```
$ sudo systemctl start libvirtd.service
```

(**optional**) You may need to check if the server environment is correctly set up : 
```
$ sudo anwdlserver start -c
```

If some error occured, check the [Troubleshooting](troubleshooting.md) section to fix them.

Start the server via the CLI : 

```
$ sudo anwdlserver start
```

(**optional**) add the option `-d` to enable direct execution (the server will run synchronously in the terminal)

Or via the systemd daemon : 

```
$ sudo systemctl start anweddol-server.service
```

## Stop the server

Stop the server via the CLI : 

```
$ sudo anwdlserver stop
```

Or via the systemd daemon : 

```
$ sudo systemctl stop anweddol-server.service
```
