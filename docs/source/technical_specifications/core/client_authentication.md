# Client authentication

----

Natively, the server handles 2 kinds of credentials : 

- The session credentials ;
- The container credentials ;

## Session credentials

The session credentials are credentials used to authenticate a client when a DESTROY request is received.
There is 2 affiliated members : 

- The container UUID ;
- The client token ;

The container UUID is the [UUID of the container](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/virtualization.html#management) that the client wants to destroy.

The client token is a private token given to the client when a container is created on receipt of a CREATE request, to ensure that the client who wants to destroy the container in question is actually the one who owns it. A token is a 255-character url-safe string, to guarantee minimum usurpability.

## Container credentials

The container credentials are the SSH credentials to use with the container in order to be able to interact with it.
There is 3 affiliated members : 

- The SSH username ;
- The SSH password ;
- The SSH listen port ;

The SSH username is in the format `user_NUM`, where NUM is a random number between 10000 and 90000.

The SSH password is a 120 character string.

The SSH listen port is a random port between 10000 and 15000, whose bindability is checked before assignation.