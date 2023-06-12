# Access token

----

An access token system is provided in the `tools` features.
It is used to restrict users of the service by providing tokens to authenticate them before processing the request.

A typical use case is when a client sends a request on a server, it must send an access token in the request parameters that must match one of the tokens in the database in order to be processed by the server.

## Tokens

Tokens used are 124 characters url-safe strings.

## Database

### Engine

This feature is using a SQLite file to store data.

### Table representation

Here is a representation of the used SQL table :

| EntryID                        | CreationTimestamp   | AccessToken     | Enabled            |
|------------------------------- | ------------------- | --------------- | ------------------ |
| `INTEGER NOT NULL PRIMARY KEY` | `INTEGER NOT NULL`  | `TEXT NOT NULL` | `INTEGER NOT NULL` |

- `EntryID` : Identifies the row
- `CreationTimestamp` : Store the row creation timestamp
- `AccessToken` : Store the affiliated access token
- `Enabled` : Store a boolean value (`1` / `0`) depicting if the row must be used or ignored

### Security

Any tokens written in the `AccessToken` column are hashed with SHA256.