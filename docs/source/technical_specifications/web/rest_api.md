# Web server

----

## Description

The `web` module is an HTTP alternative to the classic server. 

It consists of a REST API based on the `ServerInterface` class, which provides 
all the features of a classic server, but in the form of a web server.

## Request / response format

The request / response scheme stays the same, except that the requests are exprimed
in the form of an URL : "http://server:port/verb".

The server will respond by a JSON-formatted normalized [response dictionary](../core/communication.md).

## SSL support

The web server provides SSL support to allow secure communications between client and server.

```{warning}
If the certificate used is self-signed, there is a huge probability that most HTTP clients reject it due to its insecure nature (be it web browsers or other tools like `curl` or `wget`).

If the REST API is enabled or used on an Anweddol server, administrators shall make sure that :

	- Potential clients are aware of this ;
	- The certificate is publicly accessible ;
	- The certificate integrity is verifiable (checksums, GPG, ...) ;

Clients can always ignore the certificate authenticity check, but it's preferable to provide something to properly interact with the server.

```