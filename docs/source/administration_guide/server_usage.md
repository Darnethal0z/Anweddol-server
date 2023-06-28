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

Start the Anweddol server via systemd : 

```
$ sudo systemctl start anweddol-server.service
```

Or via the CLI : 

```
$ sudo anwdlserver start
```

(**optional**) add the option `-d` to enable direct execution (the server will run synchronously in the terminal, as the actual user)

**NOTE** : It is preferable to use systemd for server lifetime control, mixed usage between CLI and systemd can cause hazardous behaviour.

## Stop the server

Stop the server via the systemd daemon : 

```
$ sudo systemctl stop anweddol-server.service
```

Or via the CLI : 

```
$ sudo anwdlserver stop
```

**NOTE** : As mentionned in the previous section, it is preferable to use systemd for server lifetime control : mixed usage between CLI and systemd can cause hazardous behaviour.