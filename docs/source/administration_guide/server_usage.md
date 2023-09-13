# Server usage

----

> You need to follows the [Installation](installation.md) section before continuing this tutorial.

## Start the server

If you are using the `virbr0` interface as `nat_interface_name`, the first thing you need is to start the libvirtd daemon (if not already started) : 

```
$ sudo systemctl start libvirtd.service
```

You may also need to check if the server environment is correctly set up : 
```
$ sudo anwdlserver start -c
```

If some errors are displayed, check the [Troubleshooting](troubleshooting.md) section to fix them.

And start the Anweddol server via systemd : 

```
$ sudo systemctl start anweddol-server.service
```

You can also start the anweddol server directly from the terminal : 

```
$ sudo anwdlserver start
```

You can add the option `-d` to enable direct execution (the server will run synchronously in the terminal, as the actual user).

```{note}
It is preferable to use systemd for server lifetime control, mixed usage between CLI and systemd can cause hazardous behaviour.
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

As mentionned in the previous section, it is preferable to use systemd for server lifetime control : mixed usage between CLI and systemd can cause hazardous behaviour.