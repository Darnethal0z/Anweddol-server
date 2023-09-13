# Client authentication

----

Natively, the server handles 2 kinds of credentials : 

- The session credentials ;
- The container credentials ;

## Session credentials

The session credentials are credentials used to authenticate a client when a `DESTROY` request is received.

There is 2 affiliated members : 

- *The container UUID*

  The [UUID of the container](virtualization.md#management) that the client wants to destroy.

- *The client token*

  It is a private token given to the client when a container is created on receipt of a `CREATE` request, to ensure that the client who wants to destroy the container in question is actually the one who owns it. A token is a 255-character url-safe string, to guarantee minimum usurpability.

## Container credentials

The container credentials are the SSH credentials to use with the container in order to be able to interact with it.

There is 3 affiliated members : 

- *The SSH username*

  The container SSH username in the format `user_NUM`, where `NUM` is a random number between 10000 and 90000 ;

- *The SSH password*

  The container SSH password, a 120 character string ;

- *The SSH listen port*

  A random port between 10000 and 15000 (by default) assigned on the server interface made to forward input traffic towards the container SSH port (22).