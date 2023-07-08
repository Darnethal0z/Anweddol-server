# Logging

----

The Anweddol server CLI uses the `logging` python module to ensure viable logging feature.

Logs are stored in `/var/log/anweddol/runtime.txt` and are stored in this format :

```
%(asctime)s %(levelname)s : %(message)s
```

Here is a sample of logs generated during the development phase of the Anweddol server : 

```
2023-06-27 17:59:25,126 WARNING : [INIT] Initializing server (running as 'anweddol') ...
2023-06-27 17:59:25,126 INFO : [INIT] Loading instance RSA key pair ...
2023-06-27 17:59:25,700 INFO : [INIT] Initializing server interface ...
2023-06-27 17:59:25,711 INFO : [INIT] Binding handlers routine ...
2023-06-27 17:59:25,711 INFO : [INIT] All done. Server is ready
2023-06-27 17:59:25,711 INFO : Starting server ...
2023-06-27 17:59:25,712 INFO : Server is started
2023-06-27 17:59:42,724 INFO : (client ID 12ca17b) New client connected
2023-06-27 17:59:42,770 INFO : (client ID 12ca17b) Received STAT request
2023-06-27 17:59:42,778 INFO : (client ID 12ca17b) Connection closed
2023-06-27 17:59:49,958 INFO : (client ID 12ca17b) New client connected
2023-06-27 17:59:50,003 INFO : (client ID 12ca17b) Received CREATE request
2023-06-27 17:59:50,003 INFO : (client ID 12ca17b) Container 5d730281-414d-4bd8-ae01-13ebf302fd17 was created
2023-06-27 18:00:03,421 INFO : (client ID 12ca17b) Container 5d730281-414d-4bd8-ae01-13ebf302fd17 domain is started
2023-06-27 18:00:03,443 INFO : Connected (version 2.0, client OpenSSH_8.4p1)
2023-06-27 18:00:03,567 INFO : Authentication (password) successful!
2023-06-27 18:00:03,567 INFO : (client ID 12ca17b) Endpoint shell opened
2023-06-27 18:00:05,458 INFO : (client ID 12ca17b) Connection closed
2023-06-27 18:00:19,881 INFO : (client ID 12ca17b) New client connected
2023-06-27 18:00:19,927 INFO : (client ID 12ca17b) Received DESTROY request
2023-06-27 18:00:20,143 INFO : (client ID 12ca17b) Container 5d730281-414d-4bd8-ae01-13ebf302fd17 was destroyed
2023-06-27 18:00:20,145 INFO : (client ID 12ca17b) Connection closed
```

**NOTE** : Clients are represented by their IDs, here "12ca17b" : It is a way of programmatically identifying the client other than with his IP. It is the first 7 characters of the client's IP SHA256.

## Log rotation

You have the possibility to rotate logs by archiving or deleting them.

Archived logs will be stored in a separate folder withing zipped files with the name format : 

```
archived_<DATE>.zip
```

where `DATE` is the rotation date. See the `log_rotation` section in the [configuration file](configuration_file.md) for more.