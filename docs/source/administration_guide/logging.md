# Logging

----

The Anweddol server CLI uses the `logging` python module to ensure viable logging feature.

Logs are stored in `/var/log/anweddol/runtime.txt` and are stored in this format :

```
" ** %(asctime)s %(levelname)s : %(message)s"
```

Here is a sample of logs generated during the development phase of the Anweddol server : 

```
 ** 2023-05-09 21:37:34,327 INFO : New client (ID : 12ca17b)
 ** 2023-05-09 21:37:34,371 INFO : [12ca17b] Received STAT request
 ** 2023-05-09 21:37:34,373 INFO : [12ca17b] Connection closed
 ** 2023-05-09 21:48:33,576 INFO : New client (ID : 12ca17b)
 ** 2023-05-09 21:48:33,621 INFO : [12ca17b] Received CREATE request
 ** 2023-05-09 21:48:33,621 INFO : [12ca17b] Container 41e7a14c-d050-40e1-842c-a9c86f903459 was created
 ** 2023-05-09 21:48:47,378 INFO : Connected (version 2.0, client OpenSSH_8.4p1)
 ** 2023-05-09 21:48:47,498 INFO : Authentication (password) successful!
 ** 2023-05-09 21:48:47,498 INFO : [12ca17b] Endpoint shell opened
 ** 2023-05-09 21:48:49,411 INFO : [12ca17b] Connection closed
```

**NOTE** : Clients are represented by their IDs, here "12ca17b" : It is a way of programmatically identifying the client other than with his IP. It is the first 7 characters of the client's IP SHA256.