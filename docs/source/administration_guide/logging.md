# Logging

----

## General informations

The Anweddol server CLI uses the `logging` python module to ensure viable logging feature.

Logs are stored in `/var/log/anweddol/runtime.txt` and are stored in this format :

```
%(asctime)s %(levelname)s : %(message)s
```

```{note}
Clients are represented by their IDs : It is a way of programmatically identifying the client other than with his IP. It is the first 7 characters of the client's IP SHA256.
```

## Log rotation

You have the possibility to enable log rotation by archiving or deleting them after a defined amount of lines reached.

Archived logs will be stored in a separate folder withing zipped files with the name format : 

```
archived_<DATE>.zip
```

where `DATE` is the rotation date. See the `log_rotation` section in the [configuration file](configuration_file.md) for more.