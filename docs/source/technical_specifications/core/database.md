# Database

----

## Engine

The server is using a sqlite-based SQLAlchemy ORM memory database engine to ensure its content volatility.

See the [SQLAlchemy website](https://www.sqlalchemy.org/) to learn more.

## Table representation

The table used for databse instance is `AnweddolServerSessionCredentialsTable`.

Here is its representation :

| EntryID               | CreationTimestamp | ContainerUUID | ClientToken   |
| --------------------- | ----------------- | ------------- | ------------- |
| `Integer primary key` | `Integer`         | `String`      | `String`      |

- *EntryID*

  The entry ID, identifies the row.

- *CreationTimestamp*

  The creation timestamp of the entry.

- *ContainerUUID*

  The container UUID.

- *ClientToken*

  The affiliated client token.

## Security

The data written in the *ContainerUUID* and the *ClientToken* columns are hashed with SHA256.