# Access token

----

An access token system is provided in the `tools` features, it is used to restrict users of the service by providing tokens to authenticate them before processing any request.

If the server is in a public or multi-user area, it makes a pretty easy-to-deploy solution to prevent unwanted usage.

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

- *EntryID*

  The entry ID, identifies the row.

- *CreationTimestamp*

  The row creation timestamp.

- *AccessToken*

  The affiliated access token.

- *Enabled*

  A boolean integer (`1` or `0`) depicting if the row must be used or not.

### Security

Any tokens written in the `AccessToken` column are hashed with SHA256.